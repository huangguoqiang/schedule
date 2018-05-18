#!usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import time
import json
import io
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
import math
import openpyxl
import xlwt


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


# 导出某月的excel排班表
@csrf_exempt
def export_excel(request):
    is_public = request.POST['is_public']
    y = int(request.POST['year'])
    m = int(request.POST['month'])
    mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    date_from = datetime.datetime(y, m, 1, 0, 0)
    date_to = datetime.datetime(y, m, mdays[m], 0, 0)
    person_dict = {}
    shift_dict = {}
    team_dict = {}
    schedule_dict = {}
    queryset_list = []
    shift_set = Shift.objects.all()
    person_set = Person.objects.all()
    team_set = Team.objects.filter(is_delete=False).all()

    for obj in shift_set:
        shift_dict[obj.id] = obj

    for obj in person_set:
        person_dict[obj.id] = obj
        schedule_dict[obj.id] = {}

    for obj in team_set:
        team_dict[obj.id] = obj
        queryset = Schedule.objects.filter(date__range=(date_from, date_to), team_id=obj.id, is_base=False,
                                           is_public=is_public).all()
        queryset_list.append(queryset)

    for my_list in queryset_list:
        for obj in my_list:
            if schedule_dict.get(obj.person_id) is not None:
                schedule_dict[obj.person_id][str(obj.date)] = obj

    value_team = []
    shift_name_dict = {'Day': 'A', 'Night': 'B', 'All-Day': 'Duty'}
    for team_obj in team_set:
        queryset = Person.objects.filter(team_id=team_obj.id, is_delete=False).all()
        if team_obj.name == 'Leaders':
            team_name = team_obj.name
        else:
            team_name = team_obj.name + "  Team"
        title_list = [team_name]
        for j in range(1, (date_to - date_from).days + 2):
            title_list.append(str(m) + "/" + str(j))
        value_team.append(title_list)
        for person_obj in queryset:
            p_list = [person_obj.name]
            for n in range(0, len(title_list) - 1):
                if schedule_dict.get(person_obj.id) is not None:
                    tt_dict = schedule_dict[person_obj.id]
                    if tt_dict.get(str(date_from + datetime.timedelta(days=n))) is not None:
                        schedule_obj = tt_dict[str(date_from + datetime.timedelta(days=n))]
                        shift_obj = shift_dict[schedule_obj.shift_id]
                        shift_name_key = shift_obj.name
                        p_list.append(shift_name_dict[shift_name_key])
                    else:
                        if team_obj.name == 'Leaders':
                            p_list.append('Off')
                        else:
                            p_list.append('休')
            value_team.append(p_list)
        value_team.append([])
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet("排班表")
    # 设置cell的style
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平居中
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 垂直居中
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style0 = xlwt.easyxf('pattern: pattern solid, fore_colour 17;')  # green
    style1 = xlwt.easyxf('pattern: pattern solid, fore_colour 48;')  # blue
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour 22;')  # grey
    style3 = xlwt.easyxf('pattern: pattern solid, fore_colour 1')  # white
    style4 = xlwt.easyxf('pattern: pattern solid, fore_colour 52')  # yellow
    style0.alignment = alignment
    style1.alignment = alignment
    style2.alignment = alignment
    style3.alignment = alignment
    style4.alignment = alignment
    style0.borders = borders
    style1.borders = borders
    style2.borders = borders
    style3.borders = borders
    style4.borders = borders
    sheet.write_merge(0, 0, 0, 5, 'A', style0)
    sheet.write_merge(0, 0, 6, 11, 'Day Shift', style0)
    sheet.write_merge(0, 0, 12, 17, '8:00~20:00', style0)
    sheet.write_merge(1, 1, 0, 5, 'B', style1)
    sheet.write_merge(1, 1, 6, 11, 'Night Shift', style1)
    sheet.write_merge(1, 1, 12, 17, '20:00~8:00', style1)
    sheet.write_merge(2, 2, 0, 5, '', style3)
    sheet.write_merge(2, 2, 6, 11, 'Normal', style3)
    sheet.write_merge(2, 2, 12, 17, '8:30~17:30', style3)
    sheet.write_merge(3, 3, 0, 5, '休', style2)
    sheet.write_merge(3, 3, 6, 11, 'Vacation', style2)
    sheet.write_merge(3, 3, 12, 17, '----', style2)
    # 添加cell内容
    for i in range(0, len(value_team)):
        for j in range(0, len(value_team[i])):
            if value_team[i][j] == 'A':
                sheet.write(i + 6, j + 1, value_team[i][j], style0)
            elif value_team[i][j] == 'B':
                sheet.write(i + 6, j + 1, value_team[i][j], style1)
            elif value_team[i][j] == '休':
                sheet.write(i + 6, j + 1, value_team[i][j], style2)
            elif value_team[i][j] == 'Duty':
                sheet.write(i + 6, j + 1, value_team[i][j], style4)
            elif value_team[i][j] == 'Off':
                sheet.write(i + 6, j + 1, value_team[i][j], style2)
            else:
                if j == 0:
                    sheet.write_merge(i + 6, i + 6, 0, 1, value_team[i][j], style3)
                else:
                    sheet.write(i + 6, j + 1, value_team[i][j], style3)

    # 返回文件流到浏览端下载，浏览端必须以form提交方式方能下载成功！
    bio = io.BytesIO()

    wb.save(bio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
    response = HttpResponse()

    response['Content-Type'] = 'application/vnd.ms-excel'  # 文件类型
    response['Content-Disposition'] = 'attachment;filename={0}'.format("Excel.xls")

    bio.seek(0)  # 保存流
    response.write(bio.getvalue())
    print("写入数据成功！")
    return response
    # return HttpResponse(json.dumps({'status': 'UP'}), content_type="application/json")


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
            if person_dict.get(obj.person_id) is not None:
                person = person_dict[obj.person_id]
                # shift_count_dict = {}
                night_shift_num = 0
                double_pay = 0
                three_pay = 0
                # for k, v in shift_dict.items():
                #     shift_count_dict[v.name] = 0
                one_shift = shift_dict.get(obj.shift_id)
                # 统计白夜班
                # shift_count_dict[one_shift.name] = shift_count_dict[one_shift.name] + 1
                # 统计双薪，三薪
                night_shift_num, double_pay, three_pay = calculate_multiple_wages(one_shift, obj, multiple_wages_dict,
                                                                                  night_shift_num, double_pay,
                                                                                  three_pay)
                person_list = [person.name, night_shift_num, double_pay, three_pay]
                person_count_dict[obj.person_id] = person_list
        else:
            one_shift = shift_dict.get(obj.shift_id)
            # 统计白夜班
            # person_count_dict[obj.person_id][1][one_shift.name] = person_count_dict[obj.person_id][1][
            #                                                           one_shift.name] + 1
            # 统计双薪，三薪
            person_count_dict[obj.person_id][1], person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][
                3] = calculate_multiple_wages(one_shift, obj, multiple_wages_dict, person_count_dict[obj.person_id][1],
                                              person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][3])
    # 统计每月最后一天到每月1号那个班次的三薪
    for obj in schedule_before_set:
        if person_count_dict.get(obj.person_id) is None:
            if person_dict.get(obj.person_id) is not None:
                person = person_dict[obj.person_id]
                # shift_count_dict = {}
                night_shift_num = 0
                double_pay = 0
                three_pay = 0
                # for k, v in shift_dict.items():
                #     shift_count_dict[v.name] = 0
                one_shift = shift_dict.get(obj.shift_id)
                # 统计双薪，三薪
                night_shift_num, double_pay, three_pay = calculate_multiple_wages(one_shift, obj, multiple_wages_dict,
                                                                                  night_shift_num, double_pay,
                                                                                  three_pay)
                person_list = [person.name, 0, double_pay, three_pay]
                person_count_dict[obj.person_id] = person_list
        else:
            one_shift = shift_dict.get(obj.shift_id)
            night_shift_num = 0
            # 统计双薪，三薪
            night_shift_num, person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][
                3] = calculate_multiple_wages(one_shift, obj, multiple_wages_dict, night_shift_num,
                                              person_count_dict[obj.person_id][2], person_count_dict[obj.person_id][3])

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
        person = Person.objects.filter(id=obj.person_id).first()
        one_shift = Shift.objects.filter(id=obj.shift_id).first()
        my_dict['date'] = today
        my_dict['person_name'] = person.name
        my_dict['shift_name'] = one_shift.name
        my_dict['time_start'] = one_shift.time_start.strftime("%H:%M")
        my_dict['time_end'] = one_shift.time_end.strftime("%H:%M")
        today_list.append(my_dict)
    return HttpResponse(json.dumps(today_list), content_type="application/json")


# 自动生成下三个月排班
@csrf_exempt
def auto_generate(request):
    team_id = request.POST['team_id']
    is_public = request.POST['is_public']
    lastest_obj = Schedule.objects.filter(team_id=team_id, is_base=False, is_public=is_public).order_by('-date').first()
    oldest_obj = Schedule.objects.filter(team_id=team_id, is_base=True, is_public=is_public).order_by('date').first()
    queryset_base = Schedule.objects.filter(team_id=team_id, is_base=True, is_public=is_public).all()
    # 计算当前最新排班的日期与最老基础排班的日期之间差的天数
    sub = lastest_obj.date - oldest_obj.date + datetime.timedelta(days=1)
    # 计算一共有几天基础排班
    oldest_date = datetime.datetime.strptime('2099-10-31', '%Y-%m-%d')
    newest_date = datetime.datetime.strptime('1900-10-31', '%Y-%m-%d')
    for obj in queryset_base:
        if oldest_date > obj.date:
            oldest_date = obj.date
        if newest_date < obj.date:
            newest_date = obj.date
    base_days = (newest_date - oldest_date).days + 1
    # 添加新的排班
    i = 0
    while i < math.ceil(90 / base_days):
        for obj in queryset_base:
            item = copy.copy(obj)
            item.date = item.date + sub + datetime.timedelta(days=i * base_days)
            new_schedule_obj = Schedule.objects.create(team_id=item.team_id, date=item.date,
                                                       person_id=item.person_id, shift_id=item.shift_id,
                                                       is_master=item.is_master, is_base=False, is_public=is_public)
            new_schedule_obj.save()
        i = i + 1

    return HttpResponse(request)


# 每天检测排班（通过crontab调用api）是否够三个月，不够自动生成
@csrf_exempt
def auto_generate_everyday(request):
    queryset_team = Team.objects.filter(is_delete=False).all()
    for is_public in [True, False]:
        for obj_team in queryset_team:
            lastest_obj = Schedule.objects.filter(team_id=obj_team.id, is_base=False, is_public=is_public).order_by(
                '-date').first()
            oldest_obj = Schedule.objects.filter(team_id=obj_team.id, is_base=True, is_public=is_public).order_by(
                'date').first()
            if lastest_obj is not None:
                queryset_base = Schedule.objects.filter(team_id=obj_team.id, is_base=True, is_public=is_public).all()
                sub = lastest_obj.date - oldest_obj.date + datetime.timedelta(days=1)
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
    newest_date = datetime.datetime.strptime('1900-10-31', '%Y-%m-%d')
    team_id = mist[0]['team_id']
    Schedule.objects.filter(team_id=team_id, is_base=True, is_public=is_public).delete()
    # 存储基础排班，并计算基础排班的天数
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
        if newest_date < mist[i]['date']:
            newest_date = mist[i]['date']
        i = i + 1
    base_days = (newest_date - oldest_date).days + 1

    Schedule.objects.filter(team_id=team_id, is_base=False, is_public=is_public).filter(date__gte=oldest_date).delete()
    i = 0
    while i < math.ceil(90 / base_days):
        j = 0
        while j < num:
            item = mist[j].copy()
            item['date'] = item['date'] + datetime.timedelta(days=i * base_days)
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


# team view
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('id')
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'name', 'is_delete')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Schedule.objects.filter(team_id=instance.id, is_base=True).delete()
        bool_list = [True, False]
        for x in bool_list:
            Schedule.objects.filter(team_id=instance.id, is_base=False, is_public=x).filter(
                date__gt=datetime.datetime.now().strftime('%Y-%m-%d')).delete()
        Shift.objects.filter(team_id=instance.id).update(is_delete=True)
        Person.objects.filter(team_id=instance.id).update(is_delete=True)
        Team.objects.filter(id=instance.id).update(is_delete=True)
        # self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# shift view
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('id')
    serializer_class = ShiftSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'name', 'is_delete')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Schedule.objects.filter(shift_id=instance.id, is_base=True).delete()
        bool_list = [True, False]
        for x in bool_list:
            Schedule.objects.filter(shift_id=instance.id, is_base=False, is_public=x).filter(
                date__gt=datetime.datetime.now().strftime('%Y-%m-%d')).delete()
        # self.perform_destroy(instance)
        Shift.objects.filter(id=instance.id).update(is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


# person view
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('id')
    serializer_class = PersonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'team_id', 'name', 'email', 'slack_id', 'is_delete')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Schedule.objects.filter(person_id=instance.id, is_base=True).delete()
        bool_list = [True, False]
        for x in bool_list:
            Schedule.objects.filter(person_id=instance.id, is_base=False, is_public=x).filter(
                date__gt=datetime.datetime.now().strftime('%Y-%m-%d')).delete()
        # self.perform_destroy(instance)
        Person.objects.filter(id=instance.id).update(is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
def calculate_multiple_wages(one_shift, schedule_obj, multiple_wages_dict, night_shift_num, double_pay, three_pay):
    str_time_start = one_shift.time_start.strftime("%Y-%m-%d %H:%M:%S")
    date_time_start = datetime.datetime.strptime(str_time_start, '%Y-%m-%d %H:%M:%S')
    date_time_start = date_time_start + datetime.timedelta(
        days=(schedule_obj.date.date() - date_time_start.date()).days)
    str_time_end = one_shift.time_end.strftime("%Y-%m-%d %H:%M:%S")
    date_time_end = datetime.datetime.strptime(str_time_end, '%Y-%m-%d %H:%M:%S')
    date_time_end = date_time_end + datetime.timedelta(days=(schedule_obj.date.date() - date_time_end.date()).days)
    if date_time_start >= date_time_end:
        night_shift_num = night_shift_num + 1
        date_time_end = date_time_end + datetime.timedelta(days=1)
        str_time_mid = date_time_end.date().strftime("%Y-%m-%d") + " 00:00:00"
        date_time_mid = datetime.datetime.strptime(str_time_mid, '%Y-%m-%d %H:%M:%S')
        if multiple_wages_dict.get(date_time_start.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_mid - date_time_start).days) * 24 + int(
                    (date_time_mid - date_time_start).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_mid - date_time_start).days) * 24 + int(
                    (date_time_mid - date_time_start).seconds / (60 * 60))
        if multiple_wages_dict.get(date_time_end.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_end.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_end - date_time_mid).days) * 24 + int(
                    (date_time_end - date_time_mid).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_end.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_end - date_time_mid).days) * 24 + int(
                    (date_time_end - date_time_mid).seconds / (60 * 60))
    else:
        if multiple_wages_dict.get(date_time_start.date().strftime("%Y-%m-%d")) is not None:
            if multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 2:
                double_pay = double_pay + int((date_time_end - date_time_start).days) * 24 + int(
                    (date_time_end - date_time_start).seconds / (60 * 60))
            elif multiple_wages_dict[date_time_start.date().strftime("%Y-%m-%d")] == 3:
                three_pay = three_pay + int((date_time_end - date_time_start).days) * 24 + int(
                    (date_time_end - date_time_start).seconds / (60 * 60))
    return night_shift_num, double_pay, three_pay
