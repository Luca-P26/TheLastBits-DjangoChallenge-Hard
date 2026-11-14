import random

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FightForm, UnitForm
from .models import Fight, FightTurn, Unit
from .models import ImportedFight, ImportedFightEvent, Person


def register_challenge_roster(request):
    if request.method != 'POST':
        return redirect('simulate-challenge')
    from .tasks import register_people

    register_people.delay()
    messages.success(request, 'Roster registration has started in the background.')
    return redirect('simulate-challenge')


def simulate_challenge(request):
    # The page is also the challenge's live status board. Any pending imported
    # fights are dispatched independently and the task safely claims each once.
    pending_count = ImportedFight.objects.filter(status=ImportedFight.Status.PENDING).count()
    if pending_count:
        from .tasks import dispatch_pending_fights

        dispatch_pending_fights.delay()
    fights = ImportedFight.objects.select_related('blue_soldier', 'red_soldier').prefetch_related(
        'events__attacker', 'events__defender'
    )
    return render(request, 'units/simulate.html', {
        'people_count': Person.objects.count(),
        'drafted_count': Person.objects.exclude(rank='').count(),
        'fights': fights,
        'event_count': ImportedFightEvent.objects.count(),
        'pending_count': pending_count,
        'running_count': ImportedFight.objects.filter(status=ImportedFight.Status.RUNNING).count(),
    })


def create_unit(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'{unit.name} joined the army.')
            return redirect('unit-detail', pk=unit.pk)
        messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = UnitForm()
    return render(request, 'units/unit_form.html', {'form': form})


def unit_list(request):
    units = Unit.objects.all()
    recent_fights = Fight.objects.select_related('unit_one', 'unit_two', 'winner')[:5]
    fight_counts = Fight.objects.aggregate(
        blue=Count('id', filter=Q(unit_one__team=Unit.Team.BLUE) | Q(unit_two__team=Unit.Team.BLUE)),
        red=Count('id', filter=Q(unit_one__team=Unit.Team.RED) | Q(unit_two__team=Unit.Team.RED)),
    )
    damage_totals = FightTurn.objects.aggregate(
        blue_caused=Sum('attack_points', filter=Q(attacker__team=Unit.Team.BLUE)),
        blue_taken=Sum('attack_points', filter=Q(defender__team=Unit.Team.BLUE)),
        red_caused=Sum('attack_points', filter=Q(attacker__team=Unit.Team.RED)),
        red_taken=Sum('attack_points', filter=Q(defender__team=Unit.Team.RED)),
    )
    team_statistics = [
        {
            'team': 'Blue',
            'fights': fight_counts['blue'],
            'damage_caused': damage_totals['blue_caused'] or 0,
            'damage_taken': damage_totals['blue_taken'] or 0,
        },
        {
            'team': 'Red',
            'fights': fight_counts['red'],
            'damage_caused': damage_totals['red_caused'] or 0,
            'damage_taken': damage_totals['red_taken'] or 0,
        },
    ]
    return render(request, 'units/unit_list.html', {
        'units': units,
        'recent_fights': recent_fights,
        'team_statistics': team_statistics,
    })


def unit_detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    fights = Fight.objects.filter(Q(unit_one=unit) | Q(unit_two=unit)).select_related(
        'unit_one', 'unit_two', 'winner'
    ).prefetch_related('turns__attacker', 'turns__defender')
    return render(request, 'units/unit_detail.html', {'unit': unit, 'fights': fights})


def heal_unit(request, pk):
    if request.method != 'POST':
        return redirect('unit-list')
    unit = get_object_or_404(Unit, pk=pk)
    unit.health = 100
    unit.save(update_fields=('health',))
    messages.success(request, f'{unit.name} has been fully healed.')
    return redirect('unit-list')


def simulate_fight(request):
    if request.method == 'POST':
        form = FightForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                fighter_one = Unit.objects.select_for_update().get(pk=form.cleaned_data['fighter_one'].pk)
                fighter_two = Unit.objects.select_for_update().get(pk=form.cleaned_data['fighter_two'].pk)
                fight = Fight.objects.create(unit_one=fighter_one, unit_two=fighter_two)

                if fighter_one.attack_points == 0 and fighter_two.attack_points == 0:
                    fight.status = Fight.Status.STALEMATE
                    fight.save(update_fields=('status',))
                else:
                    attacker, defender = fighter_one, fighter_two
                    turn_number = 0
                    while fighter_one.health > 0 and fighter_two.health > 0:
                        turn_number += 1
                        attack_points = random.randint(0, attacker.attack_points)
                        defender.health = max(0, defender.health - attack_points)
                        defender.save(update_fields=('health',))
                        FightTurn.objects.create(
                            fight=fight,
                            turn_number=turn_number,
                            attacker=attacker,
                            defender=defender,
                            attack_points=attack_points,
                            attacker_health=attacker.health,
                            defender_health=defender.health,
                        )
                        attacker, defender = defender, attacker

                    fight.winner = fighter_one if fighter_one.health > 0 else fighter_two
                    fight.save(update_fields=('winner',))
            return redirect('fight-result', pk=fight.pk)
        messages.error(request, 'Choose two different fighters from opposing teams.')
    else:
        form = FightForm()
    return render(request, 'units/fight_form.html', {'form': form})


def fight_result(request, pk):
    fight = get_object_or_404(
        Fight.objects.select_related('unit_one', 'unit_two', 'winner').prefetch_related(
            'turns__attacker', 'turns__defender'
        ),
        pk=pk,
    )
    return render(request, 'units/fight_result.html', {'fight': fight})
