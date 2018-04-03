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
    url(r'^generate/', generate),
    url(r'^get_health/', get_health),
]
