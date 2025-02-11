from django.urls import path, include

from .views import *


app_name = 'base'

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
