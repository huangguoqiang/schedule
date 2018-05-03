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


def count(request):
    return render(request, 'count.html')


# 获取项目健康状态
def get_health(request):
    return HttpResponse(json.dumps({'status': 'UP'}), content_type="application/json")


# 根據team_id,開始日期，結束日期統計
@csrf_exempt
def get_schedule_count(request):
    team_id = request.POST['team_id']
    date_from = request.POST['date_from']
    date_to = request.POST['date_to']
    person_dict = {}
    shift_dict = {}
    person_count_dict = {}
    schedule_set = Schedule.objects.filter(date__range=(date_from, date_to)).filter(team_id=team_id, is_base=False,
                                                                                    is_public=False).all()
    shift_set = Shift.objects.filter(team_id=team_id).all()
    person_set = Person.objects.filter(team_id=team_id).all()
    for obj in shift_set:
        shift_dict[obj.id] = obj
    for obj in person_set:
        person_dict[obj.id] = obj
    for obj in schedule_set:
        if person_count_dict.get(obj.person_id) is None:
            person = person_dict[obj.person_id]
            shift_count_dict = {}
            for k, v in shift_dict.items():
                shift_count_dict[v.name] = 0
            one_shift = shift_dict.get(obj.shift_id)
            shift_count_dict[one_shift.name] = shift_count_dict[one_shift.name] + 1
            person_list = [person.name, shift_count_dict]
            person_count_dict[obj.person_id] = person_list
        else:
            one_shift = shift_dict.get(obj.shift_id)
            person_count_dict[obj.person_id][1][one_shift.name] = person_count_dict[obj.person_id][1][
                                                                      one_shift.name] + 1
    return HttpResponse(json.dumps(person_count_dict), content_type="application/json")


# 获取当天某个team的值班表
@csrf_exempt
def get_schedule_today(request):
    team_id = int(request.GET['team_id'])
    today = time.strftime("%Y-%m-%d")
    today_list = []
    my_dict = {}
    queryset = Schedule.objects.filter(date=today, team_id=team_id, is_base=False, is_public=False).all()
    for obj in queryset:
        print(obj.date)
        person = Person.objects.filter(id=obj.person_id).first()
        one_shift = Shift.objects.filter(id=obj.shift_id).first()
        my_dict['date'] = today
        my_dict['person_name'] = person.name
        my_dict['shift_name'] = one_shift.name
        my_dict['time_start'] = one_shift.time_start.strftime("%H:%M")
        my_dict['time_end'] = one_shift.time_end.strftime("%H:%M")
        today_list.append(my_dict)
    return HttpResponse(json.dumps(today_list), content_type="application/json")


# schedule view
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'person_id', 'date', 'is_public')

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


# 自动生成下三个月排班
@csrf_exempt
def auto_generate(request):
    team_id = request.POST['team_id']
    is_public = request.POST['is_public']
    lastest_obj = Schedule.objects.filter(team_id=team_id, is_base=False, is_public=is_public).order_by('-date').first()
    queryset_base = Schedule.objects.filter(team_id=team_id, is_base=True, is_public=is_public).all()
    sub = lastest_obj.date - queryset_base[0].date + datetime.timedelta(days=1)
    i = 0
    while i < 11:
        for obj in queryset_base:
            item = copy.copy(obj)
            item.date = item.date + sub + datetime.timedelta(days=i * 8)
            new_schedule_obj = Schedule.objects.create(team_id=item.team_id, date=item.date,
                                                       person_id=item.person_id, shift_id=item.shift_id,
                                                       is_master=item.is_master, is_base=False, is_public=is_public)
            new_schedule_obj.save()
        i = i + 1

    return HttpResponse(request)


# 每天检测排班（通过crontab调用api）是否够三个月，不够自动生成
@csrf_exempt
def auto_generate_everyday(request):
    queryset_team = Team.objects.all()
    for is_public in [True, False]:
        for obj_team in queryset_team:
            lastest_obj = Schedule.objects.filter(team_id=obj_team.id, is_base=False, is_public=is_public).order_by(
                '-date').first()
            if lastest_obj is not None:
                queryset_base = Schedule.objects.filter(team_id=obj_team.id, is_base=True).all()
                sub = lastest_obj.date - queryset_base[0].date + datetime.timedelta(days=1)
                if sub < datetime.timedelta(days=97):
                    for obj in queryset_base:
                        item = copy.copy(obj)
                        item.date = item.date + sub
                        new_schedule_obj = Schedule.objects.create(team_id=item.team_id, date=item.date,
                                                                   person_id=item.person_id, shift_id=item.shift_id,
                                                                   is_master=item.is_master, is_base=False,
                                                                   is_public=is_public)
                        new_schedule_obj.save()

    return HttpResponse(request)


# 生成排班表
@csrf_exempt
def generate(request):
    schedule_list = json.loads(request.body.decode('utf-8'))
    mist = schedule_list['list']
    is_public = schedule_list['is_public']
    print(is_public)
    i = 0
    num = len(mist)
    oldest_date = datetime.datetime.strptime('2099-10-31', '%Y-%m-%d')
    team_id = mist[0]['team_id']
    Schedule.objects.filter(team_id=team_id, is_base=True, is_public=is_public).delete()
    while i < num:
        mist[i]['date'] = datetime.datetime.strptime(mist[i]['date'], '%Y-%m-%d')
        new_schedule_base_obj = Schedule.objects.create(team_id=mist[i]['team_id'], person_id=mist[i]['person_id'],
                                                        date=mist[i]['date'],
                                                        shift_id=mist[i]['shift_id'],
                                                        is_master=mist[i]['is_master'], is_base=True,
                                                        is_public=is_public)
        new_schedule_base_obj.save()
        if oldest_date > mist[i]['date']:
            oldest_date = mist[i]['date']
        i = i + 1
    Schedule.objects.filter(team_id=team_id, is_base=False, is_public=is_public).filter(date__gte=oldest_date).delete()
    i = 0
    while i < 12:
        j = 0
        while j < num:
            item = mist[j].copy()
            item['date'] = item['date'] + datetime.timedelta(days=i * 8)
            new_schedule_obj = Schedule.objects.create(team_id=item['team_id'], date=item['date'],
                                                       person_id=item['person_id'], shift_id=item['shift_id'],
                                                       is_master=item['is_master'], is_base=False,
                                                       is_public=is_public)
            new_schedule_obj.save()
            j = j + 1
        i = i + 1
    return HttpResponse(request)


@csrf_exempt
def send_notification(request):
    return HttpResponse(request)


# team view
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('id')
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'name')


# shift view
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('id')
    serializer_class = ShiftSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'name')


# person view
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('id')
    serializer_class = PersonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'name', 'email')
