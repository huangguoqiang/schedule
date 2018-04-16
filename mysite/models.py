from django.db import models


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Shift(models.Model):
    name = models.CharField(max_length=30, unique=True)
    time = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Person(models.Model):
    team_id = models.PositiveSmallIntegerField()
    team_name = models.CharField(max_length=30)
    name = models.CharField(max_length=30, unique=True)
    tel_num = models.CharField(max_length=20)
    email = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    team_id = models.PositiveSmallIntegerField()
    date = models.DateField()
    person_id = models.PositiveSmallIntegerField()
    person_name = models.CharField(max_length=30)
    shift_id = models.PositiveSmallIntegerField()
    shift_name = models.CharField(max_length=30)
    is_master = models.BooleanField()

    def __str__(self):
        return self.id

    class Meta:
        ordering = ('date', 'id')
