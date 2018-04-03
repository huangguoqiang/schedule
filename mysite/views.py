import calendar
import datetime
import time
import json
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from mysite.serializers import *


# Create your views here.


def index(request):
    return render(request, 'calendar.html')


def calendar(request):
    return render(request, 'newcalendar.html')


def shift(request):
    return render(request, 'shift.html')


def users(request):
    return render(request, 'users.html')


def team(request):
    return render(request, 'team.html')


def get_health(request):
    return HttpResponse(json.dumps({'status': 'UP'}))


# schedule view
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'person_id', 'date')

    @list_route()
    def list_by_date(self, request):
        y = int(request.GET['year'])
        m = int(request.GET['month'])
        mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        date_from = datetime.datetime(y, m, 1, 0, 0)
        date_to = datetime.datetime(y, m, mdays[m], 0, 0)
        queryset = self.filter_queryset(self.get_queryset().filter(date__range=(date_from, date_to)))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def list_by_today(self, request):
        today = time.strftime("%Y-%m-%d")
        queryset = self.filter_queryset(self.get_queryset().filter(date=today))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def list_by_today(self, request):
        today = time.strftime("%Y-%m-%d")
        queryset = self.filter_queryset(self.get_queryset().filter(date=today))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@csrf_exempt
def generate(request):
    schedulelist = json.loads(request.body)
    mist = schedulelist['list']
    i = 0
    num = len(mist)
    oldestdate = datetime.datetime.strptime('2099-10-31', '%Y-%m-%d')
    teamid = mist[0]['team_id']

    while i < num:
        item = mist[i].copy()
        item['date'] = datetime.datetime.strptime(item['date'], '%Y-%m-%d')
        if oldestdate > item['date']:
            oldestdate = item['date']
        i = i + 1
    Schedule.objects.filter(team_id=teamid).filter(date__gte=oldestdate).delete()
    i = 0
    while i < 12:
        j = 0
        while j < num:
            item = mist[j].copy()
            item['date'] = datetime.datetime.strptime(item['date'], '%Y-%m-%d') + datetime.timedelta(days=i * 8)
            new_schedule_obj = Schedule.objects.create(team_id=item['team_id'], date=item['date'],
                                                       person_id=item['person_id'], person_name=item['person_name'],
                                                       shift_id=item['shift_id'], shift_name=item['shift_name'],
                                                       is_master=item['is_master'])
            new_schedule_obj.save()
            j = j + 1
        i = i + 1
    return render(request, 'calendar.html')


def get_schedule(request):
    print(request.POST, '*****||||')
    # y = request.POST['year']
    # m = request.POST['month']
    y = 2018
    m = 4
    print(y, m)
    # team_id = request.POST['team_id']
    team_id = 100
    print(team_id)
    date_from = datetime.datetime(int(y), int(m), 1, 0, 0)
    date_to = datetime.datetime(int(y), int(m), calendar.mdays[m], 0, 0)
    return_data_json = serializers.serialize('json', Schedule.objects.filter(team_id=team_id).filter(
        date__range=(date_from, date_to)))
    return HttpResponse(return_data_json)


# team view
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'name')


# shift view
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'name')


# person view
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'name')
