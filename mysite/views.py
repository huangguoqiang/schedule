import datetime
import time
import json
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from mysite.serializers import *
import copy


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
    return HttpResponse(json.dumps({'status': 'UP'}), content_type="application/json")


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
        queryset = self.filter_queryset(self.get_queryset().filter(date__range=(date_from, date_to), is_base=False))
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
def auto_generate(request):
    team_id = request.POST['team_id']
    lastest_obj = Schedule.objects.filter(team_id=team_id, is_base=False).order_by('-date').first()
    queryset_base = Schedule.objects.filter(team_id=team_id, is_base=True).all()
    sub = lastest_obj.date - queryset_base[0].date + datetime.timedelta(days=1)
    i = 0
    while i < 11:
        for obj in queryset_base:
            item = copy.copy(obj)
            item.date = item.date + sub + datetime.timedelta(days=i * 8)
            print(item.date)
            new_schedule_obj = Schedule.objects.create(team_id=item.team_id, date=item.date,
                                                       person_id=item.person_id, person_name=item.person_name,
                                                       shift_id=item.shift_id, shift_name=item.shift_name,
                                                       is_master=item.is_master, is_base=False)
            new_schedule_obj.save()
        i = i + 1

    return HttpResponse(request)


@csrf_exempt
def auto_generate_everyday(request):
    queryset_team = Team.objects.all()
    for obj_team in queryset_team:
        lastest_obj = Schedule.objects.filter(team_id=obj_team.id, is_base=False).order_by('-date').first()
        if lastest_obj is not None:
            queryset_base = Schedule.objects.filter(team_id=obj_team.id, is_base=True).all()
            sub = lastest_obj.date - queryset_base[0].date + datetime.timedelta(days=1)
            if sub < datetime.timedelta(days=97):
                for obj in queryset_base:
                    item = copy.copy(obj)
                    item.date = item.date + sub
                    new_schedule_obj = Schedule.objects.create(team_id=item.team_id, date=item.date,
                                                               person_id=item.person_id, person_name=item.person_name,
                                                               shift_id=item.shift_id, shift_name=item.shift_name,
                                                               is_master=item.is_master, is_base=False)
                    new_schedule_obj.save()
    return HttpResponse(request)


@csrf_exempt
def generate(request):
    schedule_list = json.loads(request.body.decode('utf-8'))
    mist = schedule_list['list']
    i = 0
    num = len(mist)
    oldest_date = datetime.datetime.strptime('2099-10-31', '%Y-%m-%d')
    team_id = mist[0]['team_id']
    Schedule.objects.filter(team_id=team_id, is_base=True).delete()
    while i < num:
        mist[i]['date'] = datetime.datetime.strptime(mist[i]['date'], '%Y-%m-%d')
        new_schedule_base_obj = Schedule.objects.create(team_id=mist[i]['team_id'], person_id=mist[i]['person_id'],
                                                        date=mist[i]['date'],
                                                        person_name=mist[i]['person_name'],
                                                        shift_id=mist[i]['shift_id'],
                                                        shift_name=mist[i]['shift_name'],
                                                        is_master=mist[i]['is_master'], is_base=True)
        new_schedule_base_obj.save()
        if oldest_date > mist[i]['date']:
            oldest_date = mist[i]['date']
        i = i + 1
    Schedule.objects.filter(team_id=team_id, is_base=False).filter(date__gte=oldest_date).delete()
    i = 0
    while i < 12:
        j = 0
        while j < num:
            item = mist[j].copy()
            item['date'] = item['date'] + datetime.timedelta(days=i * 8)
            new_schedule_obj = Schedule.objects.create(team_id=item['team_id'], date=item['date'],
                                                       person_id=item['person_id'], person_name=item['person_name'],
                                                       shift_id=item['shift_id'], shift_name=item['shift_name'],
                                                       is_master=item['is_master'], is_base=False)
            new_schedule_obj.save()
            j = j + 1
        i = i + 1
    return HttpResponse(request)


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
