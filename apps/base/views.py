from icecream import ic

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import CustomAuthenticationForm


class Login(LoginView):
    template_name = 'base/login/login.html' 
    redirect_authenticated_user = True 
    next_page = reverse_lazy('dashboard:dashboard')
    authentication_form = CustomAuthenticationForm

class LogoutView(LogoutView):
    next_page = reverse_lazy('landingpage:dashboard')