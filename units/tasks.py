import json
import re
from urllib.error import URLError
from urllib.request import urlopen

from celery import shared_task
from django.db import transaction
from django.db.utils import OperationalError
from django.db.models import Case, F, Value, When

from .models import ImportedFight, ImportedFightEvent, Person


API_ROOT = 'https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net'


def _get_json(path):
    with urlopen(f'{API_ROOT}/{path.lstrip("/")}', timeout=15) as response:
        payload = json.load(response)
    if response.status >= 400:
        raise URLError(f'Challenge API returned HTTP {response.status}')
    return payload


def _first_endpoint(message, pattern, fallback):
    match = re.search(pattern, message)
    return match.group(1) if match else fallback


@shared_task(autoretry_for=(TimeoutError, URLError, OSError), retry_backoff=True, retry_jitter=True, max_retries=5)
def register_people():
    """Register the peacetime roster, then queue the first independent draft batch."""
    people = _get_json('/people')['data']
    Person.objects.bulk_create(
        [Person(id=item['id'], name=item['name'], age=item['age']) for item in people],
        update_conflicts=True,
        update_fields=('name', 'age'),
        unique_fields=('id',),
    )
    hellstorm = next((person for person in people if person['name'] == 'Hellstorm Fireburn'), None)
    if not hellstorm or not hellstorm.get('key'):
        raise ValueError('Hellstorm Fireburn did not provide the next endpoint key.')
    instructions = _get_json(f"/{hellstorm['key']}")['data']['message']
    first_batch = int(_first_endpoint(instructions, r'/draft/(\d+)', '/draft/0'))
    draft_people_batch.delay(first_batch)
    return len(people)


@shared_task(autoretry_for=(TimeoutError, URLError, OSError), retry_backoff=True, retry_jitter=True, max_retries=5)
def draft_people_batch(batch_number):
    batch = _get_json(f'/draft/{batch_number}')
    with transaction.atomic():
        for person in batch['data']:
            saved_person, created = Person.objects.get_or_create(
                id=person['id'],
                defaults={
                    'name': person['name'],
                    'age': person['age'],
                    'rank': person['rank'],
                    'health': person['health'],
                },
            )
            if not created:
                saved_person.name = person['name']
                saved_person.age = person['age']
                update_fields = ['name', 'age']
                # A repeated import must not heal a soldier after recorded fights.
                if not saved_person.rank:
                    saved_person.rank = person['rank']
                    saved_person.health = person['health']
                    update_fields.extend(('rank', 'health'))
                saved_person.save(update_fields=update_fields)
    next_batch = batch.get('next_batch')
    if next_batch is not None:
        draft_people_batch.delay(next_batch)
    else:
        hellstorm = next((person for person in batch['data'] if person['name'] == 'Hellstorm Fireburn'), None)
        if not hellstorm or not hellstorm.get('key'):
            raise ValueError('The final draft batch did not include Hellstorm Fireburn’s next endpoint key.')
        instructions = _get_json(f"/{hellstorm['key']}")['data']['message']
        first_fight_batch = int(_first_endpoint(instructions, r'/fight/(\d+)', '/fight/0'))
        download_fight_batch.delay(first_fight_batch)
    return len(batch['data'])


@shared_task(autoretry_for=(TimeoutError, URLError, OSError), retry_backoff=True, retry_jitter=True, max_retries=5)
def download_fight_batch(batch_number):
    batch = _get_json(f'/fight/{batch_number}')
    with transaction.atomic():
        queued_fight_ids = []
        for item in batch['data']:
            fight, _ = ImportedFight.objects.update_or_create(
                id=item['fight_id'],
                defaults={
                    'blue_soldier_id': item['blue_soldier_id'],
                    'red_soldier_id': item['red_soldier_id'],
                },
            )
            if fight.status == ImportedFight.Status.PENDING:
                queued_fight_ids.append(fight.pk)
            for turn, event in enumerate(item['steps'], start=1):
                ImportedFightEvent.objects.get_or_create(
                    fight=fight,
                    turn_number=turn,
                    defaults={
                        'attacker_id': event['attacker'],
                        'defender_id': event['defender'],
                        'damage': event['damage'],
                    },
                )
    # Each fight gets its own worker call as soon as its batch has been stored.
    for fight_id in queued_fight_ids:
        simulate_fight.delay(fight_id)
    next_batch = batch.get('next_batch')
    if next_batch is not None:
        download_fight_batch.delay(next_batch)
    else:
        fight_instructions = _get_json('/fight-info')['data']['message']
        next_instructions = _first_endpoint(
            fight_instructions, r'(/simulate-fight-info)', '/simulate-fight-info'
        )
        _get_json(next_instructions)
        dispatch_pending_fights.delay()
    return len(batch['data'])


@shared_task(autoretry_for=(TimeoutError, URLError, OSError, OperationalError), retry_backoff=True, retry_jitter=True, max_retries=5)
def simulate_fight(fight_id):
    """Replay one fight. Conditional claiming prevents duplicate tasks replaying damage."""
    # Keep the claim and replay in one transaction. A worker crash then rolls the
    # claim back to pending, so late-ack redelivery can safely resume the fight.
    with transaction.atomic():
        claimed = ImportedFight.objects.filter(
            pk=fight_id, status=ImportedFight.Status.PENDING
        ).update(status=ImportedFight.Status.RUNNING)
        if not claimed:
            return 'already running or complete'

        events = list(
            ImportedFightEvent.objects.filter(fight_id=fight_id)
            .order_by('turn_number')
        )
        for event in events:
            # Lock the soldier row on databases that support row locks. The
            # conditional update keeps health nonnegative on every backend.
            soldier = Person.objects.select_for_update().get(pk=event.defender_id)
            Person.objects.filter(pk=soldier.pk).update(
                health=Case(
                    When(health__lte=event.damage, then=Value(0)),
                    default=F('health') - event.damage,
                )
            )
            soldier.refresh_from_db(fields=('health',))
            event.defender_health_after = soldier.health
            event.save(update_fields=('defender_health_after',))
        ImportedFight.objects.filter(pk=fight_id).update(status=ImportedFight.Status.COMPLETE)
    return 'complete'


@shared_task
def dispatch_pending_fights():
    """Queue a distinct background task for each fight not yet replayed."""
    fight_ids = list(
        ImportedFight.objects.filter(status=ImportedFight.Status.PENDING)
        .order_by('id').values_list('id', flat=True)
    )
    for fight_id in fight_ids:
        simulate_fight.delay(fight_id)
    return len(fight_ids)
