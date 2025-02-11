from django.urls import path, include

from .views import *


app_name = 'landingpage'

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
]
