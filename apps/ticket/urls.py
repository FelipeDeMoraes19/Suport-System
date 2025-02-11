from django.urls import path
from .views import (
    CreateTicketView, DashboardView, TicketDetailView, CustomLoginView
)

app_name = 'ticket'

urlpatterns = [
    path('suporte-ticket/', CreateTicketView.as_view(), name='create'),
    path('tickets/', DashboardView.as_view(), name='dashboard'),
    path('tickets/<int:ticket_id>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:ticket_id>/enviar_mensagem/', TicketDetailView.as_view(), name='send_message'),  
    path('login/', CustomLoginView.as_view(), name='login'),
]
