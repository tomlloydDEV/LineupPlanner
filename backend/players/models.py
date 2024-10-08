from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class League(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country_code = models.CharField(max_length=3, default='UNK')  # ISO 3166-1 alpha-3
    tier = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1
    )

    @property
    def code(self):
        return f"{self.country_code}{self.tier}"

    class Meta:
        unique_together = [['country_code', 'tier'], ['name', 'country_code']]

    def __str__(self):
        return f"{self.name} ({self.code})"

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(15), MaxValueValidator(50)])
    shirt_number = models.IntegerField(null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"