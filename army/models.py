from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Unit(models.Model):
    class UnitType(models.TextChoices):
        INFANTRY = 'Infantry', 'Infantry'
        CANNON = 'Cannon', 'Cannon'
        CAVALRY = 'Cavalry', 'Cavalry'
        KNIGHT = 'Knight', 'Knight'

    class TeamColor(models.TextChoices):
        BLUE = 'Blue', 'Blue'
        RED = 'Red', 'Red'

    name = models.CharField(max_length=100)
    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.INFANTRY,
    )
    team = models.CharField(
        max_length=10,
        choices=TeamColor.choices,
        default=TeamColor.BLUE,
    )
    health = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    attack_points = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    profile_image_link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.name} ({self.team} - {self.unit_type})"