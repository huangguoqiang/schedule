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
from rest_framework import status
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


def multiple_wages(request):
    return render(request, 'multiplewages.html')


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
    multiple_wages_dict = {}
    person_count_dict = {}
    date_before = (datetime.datetime.strptime(date_from, "%Y-%m-%d") + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    schedule_before_set = Schedule.objects.filter(date=date_before).filter(team_id=team_id, is_base=False,
                                                                           is_public=False).all()
    schedule_set = Schedule.objects.filter(date__range=(date_from, date_to)).filter(team_id=team_id, is_base=False,
                                                                                    is_public=False).all()
    shift_set = Shift.objects.filter(team_id=team_id).all()
    person_set = Person.objects.filter(team_id=team_id).all()
    multiple_wages_set = MultipleWages.objects.filter(date__range=(date_from, date_to)).all()

    for obj in shift_set:
        shift_dict[obj.id] = obj

    for obj in person_set:
        person_dict[obj.id] = obj

    for obj in multiple_wages_set:
        multiple_wages_dict[obj.date.strftime("%Y-%m-%d")] = obj.ratio

    for obj in schedule_set:
        if person_count_dict.get(obj.person_id) is None:
            person = person_dict[obj.person_id]
            shift_count_dict = {}
            double_pay = 0
            three_pay = 0
            for k, v in shift_dict.items():
                shift_count_dict[v.name] = 0
            one_shift = shift_dict.get(obj.shift_id)
            # 统计白夜班
            shift_count_dict[one_shift.name] = shift_count_dict[one_shift.name] + 1
            # 统计双薪，三薪
            double_pay, three_pay = calculate_multiple_wages(one_shift, obj, multiple_wages_dict, double_pay, three_pay)
            person_list = [person.name, shift_count_dict, double_pay, three_pay]
            person_count_dict[obj.person_id] = person_list
        else:
            one_shift = shift_dict.get(obj.shift_id)
            # 统计白夜班
            person_count_dict[obj.person_id][1][one_shift.name] = person_count_dict[obj.person_id][1][
                                                                      one_shift.name] + 1
            # 统计双薪，三薪
            person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][3] = calculate_multiple_wages(
                one_shift, obj, multiple_wages_dict, person_count_dict[obj.person_id][2],
                person_count_dict[obj.person_id][3])

    for obj in schedule_before_set:
        if person_count_dict.get(obj.person_id) is None:
            person = person_dict[obj.person_id]
            shift_count_dict = {}
            double_pay = 0
            three_pay = 0
            for k, v in shift_dict.items():
                shift_count_dict[v.name] = 0
            one_shift = shift_dict.get(obj.shift_id)
            # 统计双薪，三薪
            double_pay, three_pay = calculate_multiple_wages(one_shift, obj, multiple_wages_dict, double_pay, three_pay)
            person_list = [person.name, shift_count_dict, double_pay, three_pay]
            person_count_dict[obj.person_id] = person_list
        else:
            one_shift = shift_dict.get(obj.shift_id)
            # 统计双薪，三薪
            person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][3] = calculate_multiple_wages(
                one_shift, obj, multiple_wages_dict, person_count_dict[obj.person_id][2],
                person_count_dict[obj.person_id][3])

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


# MultipleWages view
class MultipleWagesViewSet(viewsets.ModelViewSet):
    queryset = MultipleWages.objects.all().order_by('id')
    serializer_class = MultipleWagesSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'date')

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


# 计算值班人员某个时间段的双薪，三薪
def calculate_multiple_wages(one_shift, schedule_obj, multiple_wages_dict, double_pay, three_pay):
    str_time_start = one_shift.time_start.strftime("%Y-%m-%d %H:%M:%S")
    date_time_start = datetime.datetime.strptime(str_time_start, '%Y-%m-%d %H:%M:%S')
    date_time_start = date_time_start + datetime.timedelta(
        days=(schedule_obj.date.date() - date_time_start.date()).days)
    str_time_end = one_shift.time_end.strftime("%Y-%m-%d %H:%M:%S")
    date_time_end = datetime.datetime.strptime(str_time_end, '%Y-%m-%d %H:%M:%S')
    date_time_end = date_time_end + datetime.timedelta(days=(schedule_obj.date.date() - date_time_end.date()).days)
    if date_time_start > date_time_end:
        date_time_end = date_time_end + datetime.timedelta(days=1)
        str_time_mid = date_time_end.date().strftime("%Y-%m-%d") + " 00:00:00"
        date_time_mid = datetime.datetime.strptime(str_time_mid, '%Y-%m-%d %H:%M:%S')
        if multiple_wages_dict.get(date_time_start.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_mid - date_time_start).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_mid - date_time_start).seconds / (60 * 60))
        if multiple_wages_dict.get(date_time_end.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_end.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_end - date_time_mid).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_end.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_end - date_time_mid).seconds / (60 * 60))
    else:
        if multiple_wages_dict.get(date_time_start.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_end - date_time_start).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_end - date_time_start).seconds / (60 * 60))
    return double_pay, three_pay
