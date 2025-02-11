from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from .settings import STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('', include('apps.landingpage.urls', namespace='landingpage')),
    path('base/', include('apps.base.urls', namespace='base')),
    path('ceo-painel/', admin.site.urls),
    path('ticket/',  include('apps.ticket.urls', namespace='ticket')),
]

urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)