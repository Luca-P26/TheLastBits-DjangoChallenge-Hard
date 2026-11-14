import random

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FightForm, UnitForm
from .models import Fight, FightTurn, Unit


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
    return render(request, 'units/unit_list.html', {'units': units, 'recent_fights': recent_fights})


def unit_detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    return render(request, 'units/unit_detail.html', {'unit': unit})


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
