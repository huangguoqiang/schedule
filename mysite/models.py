from django.db import models


# Create your models here.
class MultipleWages(models.Model):
    date = models.DateTimeField()
    ratio = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.date


class Team(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Shift(models.Model):
    name = models.CharField(max_length=30)
    team_id = models.PositiveSmallIntegerField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    order = models.PositiveSmallIntegerField()
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Person(models.Model):
    team_id = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=30)
    tel_num = models.CharField(max_length=20)
    email = models.CharField(max_length=40, unique=True)
    slack_id = models.CharField(max_length=128, null=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    team_id = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
    person_id = models.PositiveSmallIntegerField()
    shift_id = models.PositiveSmallIntegerField()
    is_master = models.BooleanField()
    is_base = models.BooleanField()
    is_public = models.BooleanField()

    def __str__(self):
        return self.date

    class Meta:
        ordering = ('date', 'shift_id', 'id')
