from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UnitForm
from .models import Unit


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
    return render(request, 'units/unit_list.html', {'units': units})


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
