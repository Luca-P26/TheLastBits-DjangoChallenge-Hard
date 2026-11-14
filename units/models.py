from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Unit(models.Model):
    class UnitType(models.TextChoices):
        INFANTRY = 'Infantry', 'Infantry'
        CANNON = 'Cannon', 'Cannon'
        CAVALRY = 'Cavalry', 'Cavalry'
        KNIGHT = 'Knight', 'Knight'

    class Team(models.TextChoices):
        BLUE = 'Blue', 'Blue'
        RED = 'Red', 'Red'

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=UnitType.choices)
    team = models.CharField(max_length=10, choices=Team.choices, default=Team.BLUE)
    health = models.PositiveSmallIntegerField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attack_points = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    profile_image_link = models.URLField(max_length=500)

    class Meta:
        ordering = ('name', 'id')

    def __str__(self):
        return f'{self.name} ({self.type})'


class Fight(models.Model):
    class Status(models.TextChoices):
        COMPLETE = 'complete', 'Complete'
        STALEMATE = 'stalemate', 'Stalemate'

    unit_one = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='fights_as_first')
    unit_two = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='fights_as_second')
    winner = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name='fights_won', null=True, blank=True
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.COMPLETE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', '-id')

    def __str__(self):
        return f'{self.unit_one.name} vs {self.unit_two.name} ({self.get_status_display()})'


class FightTurn(models.Model):
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.PositiveIntegerField()
    attacker = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='attacks_made')
    defender = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='attacks_received')
    attack_points = models.PositiveSmallIntegerField(help_text='Random attack value rolled for this turn.')
    attacker_health = models.PositiveSmallIntegerField()
    defender_health = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('turn_number',)
        constraints = [
            models.UniqueConstraint(fields=('fight', 'turn_number'), name='unique_fight_turn_number')
        ]

    def __str__(self):
        return f'Turn {self.turn_number}: {self.attacker.name} hit {self.defender.name} for {self.attack_points}'


class Person(models.Model):
    """A person from the challenge roster; the source ID stays stable across imports."""

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    rank = models.CharField(max_length=30, blank=True)
    health = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} ({self.rank or "civilian"})'


class ImportedFight(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETE = 'complete', 'Complete'

    id = models.PositiveIntegerField(primary_key=True)
    blue_soldier = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='blue_fights')
    red_soldier = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='red_fights')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id',)


class ImportedFightEvent(models.Model):
    fight = models.ForeignKey(ImportedFight, on_delete=models.CASCADE, related_name='events')
    turn_number = models.PositiveSmallIntegerField()
    attacker = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='events_attacked')
    defender = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='events_defended')
    damage = models.PositiveSmallIntegerField()
    defender_health_after = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('turn_number',)
        constraints = [models.UniqueConstraint(fields=('fight', 'turn_number'), name='unique_imported_fight_turn')]
