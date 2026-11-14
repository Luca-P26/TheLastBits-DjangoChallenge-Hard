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
