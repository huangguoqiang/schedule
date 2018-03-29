import calendar
import datetime
import time
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets,filters
from rest_framework.decorators import detail_route, list_route
from mysite.serializers import *
# Create your views here.


def index(request):
    return render(request, 'fullcalendar.html')

# schedule view
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('team_id', 'person_id', 'date')

    @list_route()
    def list_by_date(self, request):
        y = int(request.GET['year'])
        print(y)
        m = int(request.GET['month'])
        print(m)
        date_from = datetime.datetime(y, m, 1, 0, 0)
        date_to = datetime.datetime(y, m, calendar.mdays[m], 0, 0)
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

def generate(request):
    mist = [{'team_id': 100, 'date': '2018-03-20', 'person_id': 100, 'person_name': '黄国强', 'shift_id': 10,
             'shift_name':'白班','is_master': True},
            {'team_id': 100, 'date': '2018-03-20', 'person_id': 101, 'person_name': '齐星', 'shift_id': 10,
             'shift_name':'白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-20', 'person_id': 102, 'person_name': '薛超', 'shift_id': 11,
             'shift_name':'夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-20', 'person_id': 103, 'person_name': '薛超2', 'shift_id': 11,
             'shift_name':'白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-21', 'person_id': 104, 'person_name': '黄国强2', 'shift_id': 10,
             'shift_name':'白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-21', 'person_id': 105, 'person_name': '齐星2', 'shift_id': 10,
             'shift_name':'白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-21', 'person_id': 106, 'person_name': '薛超1', 'shift_id': 11,
             'shift_name':'夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-21', 'person_id': 107, 'person_name': '薛超3', 'shift_id': 11,
             'shift_name':'夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-22', 'person_id': 100, 'person_name': '黄国强', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-22', 'person_id': 101, 'person_name': '齐星', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-22', 'person_id': 102, 'person_name': '薛超', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-22', 'person_id': 103, 'person_name': '薛超2', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-23', 'person_id': 104, 'person_name': '黄国强2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-23', 'person_id': 105, 'person_name': '齐星2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-23', 'person_id': 106, 'person_name': '薛超1', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-23', 'person_id': 107, 'person_name': '薛超3', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-24', 'person_id': 100, 'person_name': '黄国强', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-24', 'person_id': 101, 'person_name': '齐星', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-24', 'person_id': 102, 'person_name': '薛超', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-24', 'person_id': 103, 'person_name': '薛超2', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-25', 'person_id': 104, 'person_name': '黄国强2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-25', 'person_id': 105, 'person_name': '齐星2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-25', 'person_id': 106, 'person_name': '薛超1', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-25', 'person_id': 107, 'person_name': '薛超3', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-26', 'person_id': 100, 'person_name': '黄国强', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-26', 'person_id': 101, 'person_name': '齐星', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-26', 'person_id': 102, 'person_name': '薛超', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-26', 'person_id': 103, 'person_name': '薛超2', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-27', 'person_id': 104, 'person_name': '黄国强2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': True},
            {'team_id': 100, 'date': '2018-03-27', 'person_id': 105, 'person_name': '齐星2', 'shift_id': 10,
             'shift_name': '白班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-27', 'person_id': 106, 'person_name': '薛超1', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': False},
            {'team_id': 100, 'date': '2018-03-27', 'person_id': 107, 'person_name': '薛超3', 'shift_id': 11,
             'shift_name': '夜班', 'is_master': True}]
    i = 0
    num = len(mist)
    while i < 4:
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

    return render(request, 'fullcalendar.html')


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
    filter_fields = ('name',)


# shift view
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name',)


# person view
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id','team_id','name')
