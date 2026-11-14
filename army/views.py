from django.shortcuts import render, redirect
from .models import Unit
from .forms import UnitForm


def battlefield_view(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('battlefield')
    else:
        form = UnitForm()

    blue_team = Unit.objects.filter(team=Unit.TeamColor.BLUE).order_by('-attack_points')
    red_team = Unit.objects.filter(team=Unit.TeamColor.RED).order_by('-attack_points')

    context = {
        'form': form,
        'blue_team': blue_team,
        'red_team': red_team,
    }
    return render(request, 'army/battlefield.html', context)