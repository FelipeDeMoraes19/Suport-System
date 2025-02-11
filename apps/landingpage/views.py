from icecream import ic

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.landingpage.models import *


class Dashboard(ListView):
    model = LandingPage
    template_name = 'ticket/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
