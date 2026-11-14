from django.contrib import admin

from .models import Fight, FightTurn, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'team', 'health', 'attack_points')
    list_filter = ('team', 'type')
    search_fields = ('name',)


class FightTurnInline(admin.TabularInline):
    model = FightTurn
    extra = 0
    readonly_fields = ('turn_number', 'attacker', 'defender', 'attack_points', 'attacker_health', 'defender_health')


@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_one', 'unit_two', 'winner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = (FightTurnInline,)
