from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Ticket, DadoAnalise, CustomUser


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nome de Usuário',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Senha',
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket

        # Incluindo os campos nível de atendimento e técnico
        fields = ['status', 'prioridade', 'data_conclusao', 'nivel_atendimento', 'tecnico']

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select form-select-sm form-select-solid',
                'data-hide-search': 'true',
                'data-control': 'select2',
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select form-select-sm form-select-solid',
                'data-hide-search': 'true',
                'data-control': 'select2',
            }),
            'historico': forms.Textarea(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Histórico de Atualizações',
                'rows': 4
            }),
            'data_conclusao': forms.DateInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
            }),
            'nivel_atendimento': forms.Select(attrs={
                'class': 'form-select form-select-sm form-select-solid',
                'data-hide-search': 'true',
                'data-control': 'select2',
            }),
            'tecnico': forms.Select(attrs={
                'class': 'form-select form-select-sm form-select-solid',
                'data-hide-search': 'true',
                'data-control': 'select2',
            }),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            raise forms.ValidationError("O campo situação é obrigatório.")
        return status

    def clean_prioridade(self):
        prioridade = self.cleaned_data.get('prioridade')
        if not prioridade:
            raise forms.ValidationError("O campo prioridade é obrigatório.")
        return prioridade


class DadoAnaliseForm(forms.ModelForm):
    class Meta:
        model = DadoAnalise
        fields = ['data_inicio', 'data_conclusao', 'texto', 'numero']


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['descricao', 'anexo', 'tipo', 'subtipo', 'tecnico'] 
