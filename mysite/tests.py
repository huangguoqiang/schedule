from django.test import TestCase
from mysite.models import *
import datetime
# Create your tests here.

str = (datetime.datetime.strftime('2017-03-13', '%Y-%m-%d') + datetime.timedelta(days=8)).strftime('%Y-%m-%d')
print(str)