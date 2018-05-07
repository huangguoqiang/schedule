#!usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'huang'
from rest_framework import routers
from .views import ScheduleViewSet, TeamViewSet, ShiftViewSet, PersonViewSet, MultipleWagesViewSet

router = routers.DefaultRouter()
router.register(r'schedule', ScheduleViewSet)
router.register(r'team', TeamViewSet)
router.register(r'shift', ShiftViewSet)
router.register(r'person', PersonViewSet)
router.register(r'multipleWages', MultipleWagesViewSet)
