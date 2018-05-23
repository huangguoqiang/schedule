"""Schedule URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from mysite.urls import router as mysite_router
from mysite.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # include mysite_router
    url(r'^api/', include(mysite_router.urls)),
    url(r'^$', index),
    url(r'^home/', index),
    url(r'^calendar/', calendar),
    url(r'^shift/', shift),
    url(r'^team/', team),
    url(r'^users/', users),
    url(r'^count/', count),
    url(r'^auto_generate/', auto_generate),
    url(r'^auto_generate_everyday/', auto_generate_everyday),
    url(r'^generate/', generate),
    url(r'^get_health/', get_health),
    url(r'^export_excel/', export_excel),
    url(r'^get_schedule_today/', get_schedule_today),
    url(r'^get_schedule_count/', get_schedule_count),
    url(r'^multiple_wages/', multiple_wages),
]
