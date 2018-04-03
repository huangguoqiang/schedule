from django.test import TestCase
from mysite.models import *
import datetime
# Create your tests here.

oldestdate = datetime.datetime.now()
Schedule.objects.filter(team_id=7).filter(date__gt=oldestdate).delete()