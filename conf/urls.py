from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.shortcuts import redirect
from .settings import STATIC_URL, STATIC_ROOT

from apps.ticket.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'), 

    path('base/', include('apps.base.urls', namespace='base')),
    path('ceo-painel/', admin.site.urls),
    path('ticket/',  include('apps.ticket.urls', namespace='ticket')),
]

urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
