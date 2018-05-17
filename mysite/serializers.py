#!usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'huang'
from rest_framework import serializers
from mysite.models import *


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'team_id', 'date', 'person_id', 'shift_id', 'is_master', 'is_base', 'is_public')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'is_delete')


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('id', 'name', 'team_id', 'time_start', 'time_end', 'order', 'is_delete')


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'team_id', 'name', 'tel_num', 'email', 'slack_id', 'is_delete')


class MultipleWagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleWages
        fields = ('id', 'date', 'ratio')
