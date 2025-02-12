import os
import locale
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, CreateView, ListView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.text import slugify

from .models import HistoricoTicket, Ticket, Mensagem
from .forms import TicketForm, TicketStatusForm

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
CustomUser = get_user_model()

def resolve_user(user):
    if isinstance(user, CustomUser):
        return user
    return CustomUser.objects.get(pk=user.pk)

@method_decorator(login_required, name='dispatch')
class CreateTicketView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket/create.html'
    success_url = reverse_lazy('ticket:dashboard')

    def form_valid(self, form):
        if self.request.session.get('ticket_saved'):
            return redirect(self.success_url)
        
        ticket = form.save(commit=False)
        ticket.usuario = self.request.user
        ticket.save()
        
        messages.success(self.request, 'Ticket criado com sucesso!')

        if 'anexo' in self.request.FILES:
            file_extension = os.path.splitext(self.request.FILES['anexo'].name)[1]
            new_filename = f"{ticket.pk}_{slugify(ticket.usuario.get_full_name())}_" \
                           f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            self.request.FILES['anexo'].name = new_filename
            ticket.anexo = self.request.FILES['anexo']
            ticket.url = ticket.anexo

        ticket.save()
        self.request.session['ticket_saved'] = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['referer'] = self.request.META.get('HTTP_REFERER', '/')
        return context

    def get(self, request, *args, **kwargs):
        request.session['ticket_saved'] = False
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DashboardView(ListView):
    model = Ticket
    template_name = 'ticket/dashboard.html'
    context_object_name = 'tickets'
    paginate_by = 6  # Define o número padrão para paginação

    def get_queryset(self):
        # Obtém o status do filtro
        status = self.request.GET.get('status', 'T')
        
        # Filtra os tickets pelo status
        tickets = Ticket.objects.all() if status == 'T' else Ticket.objects.filter(status=status)
        tickets = tickets.order_by('-criado_em')

        # Marca os tickets atualizados recentemente
        recentemente = timezone.now() - timezone.timedelta(days=7)
        for ticket in tickets:
            ticket.recently_updated = ticket.atualizado_em >= recentemente
            ticket.save(update_fields=['recently_updated'])

        return tickets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém os tickets filtrados
        tickets = self.get_queryset()

        # Adiciona paginação
        paginator = Paginator(tickets, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Adiciona o filtro de status e outras informações ao contexto
        context['tickets'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['selected_status'] = self.request.GET.get('status', 'T')
        context['referer'] = self.request.META.get('HTTP_REFERER', '/')

        # Mantém o filtro nos links de paginação
        context['pagination_params'] = f"&status={context['selected_status']}"

        return context

    
@method_decorator(login_required, name='dispatch')
class TicketDetailView(View):

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.tecnico == request.user and ticket.atualizado_tecnico:
            ticket.atualizado_tecnico = False
        elif ticket.usuario == request.user and ticket.atualizado_colaborador:
            ticket.atualizado_colaborador = False
        ticket.save(update_fields=['atualizado_tecnico', 'atualizado_colaborador'])

        form = TicketStatusForm(instance=ticket)
        mensagens = Mensagem.objects.filter(ticket=ticket).order_by('criado_em')
        historico_list = HistoricoTicket.objects.filter(ticket=ticket).order_by('data_criacao')

        context = self.get_context_data(ticket, form, historico_list, mensagens)
        return render(request, 'ticket/ticket_detail.html', context)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)

        # Captura os valores anteriores
        status_anterior = ticket.status
        prioridade_anterior = ticket.prioridade
        nivel_anterior = ticket.nivel_atendimento
        tecnico_anterior = ticket.tecnico

        # Inicializa o formulário apenas se 'confirmar_btn' estiver no POST
        form = TicketStatusForm(request.POST, instance=ticket) if 'confirmar_btn' in request.POST else None
        if form and form.is_valid():
            # Passa os valores anteriores ao chamar form_valid
            return self.form_valid(form, ticket, request, status_anterior, prioridade_anterior, nivel_anterior, tecnico_anterior)
        
        return self.handle_ticket_actions(request, ticket)


    def form_valid(self, form, ticket, request, status_anterior, prioridade_anterior, nivel_anterior, tecnico_anterior):
        ticket = form.save(commit=False)

        # Obter os valores atuais após a alteração
        status_atual = ticket.get_status_display()
        prioridade_atual = ticket.get_prioridade_display()
        nivel_atual = ticket.get_nivel_atendimento_display()
        tecnico_atual = ticket.tecnico

        # Obter os nomes dos valores anteriores
        status_anterior_nome = dict(Ticket.STATUS_CHOICES).get(status_anterior, status_anterior)
        prioridade_anterior_nome = dict(Ticket.PRIORIDADE_CHOICES).get(prioridade_anterior, prioridade_anterior)
        nivel_anterior_nome = dict(Ticket.NIVEL_ATENDIMENTO_CHOICES).get(nivel_anterior, nivel_anterior)

        # Variável para armazenar o histórico e mensagens de notificação
        novo_historico = []
        agora = timezone.now().strftime("%d/%m/%Y %H:%M:%S")

        # Verificação de alterações e adição ao histórico e às mensagens
        if status_anterior != ticket.status:
            novo_historico.append(
                f'Status do ticket alterado de "{status_anterior_nome}" para "{status_atual}" em {agora}'
            )
            messages.success(request, f'Status do ticket alterado para "{status_atual}".')

        if prioridade_anterior != ticket.prioridade:
            novo_historico.append(
                f'Prioridade do ticket alterada de "{prioridade_anterior_nome}" para "{prioridade_atual}" em {agora}'
            )
            messages.success(request, f'Prioridade do ticket alterada para "{prioridade_atual}".')

        if nivel_anterior != ticket.nivel_atendimento:
            novo_historico.append(
                f'Nível de atendimento alterado de "{nivel_anterior_nome}" para "{nivel_atual}" em {agora}'
            )
            messages.success(request, f'Nível de atendimento alterado para "{nivel_atual}".')

        if tecnico_anterior != tecnico_atual:
            novo_historico.append(
                f'Técnico responsável alterado de "{tecnico_anterior}" para "{tecnico_atual}" em {agora}'
            )
            messages.success(request, f'Técnico responsável alterado para "{tecnico_atual}".')

        # Adicionar histórico ao ticket
        for entry in novo_historico:
            ticket.add_historico(entry, request.user)

        # Atualizar o campo de atualização recente e flags de colaboração
        ticket.atualizado_em = timezone.now()
        if ticket.tecnico == request.user:
            ticket.atualizado_colaborador = True
        else:
            ticket.atualizado_tecnico = True

        # Salvar as mudanças no ticket
        ticket.save(update_fields=[
            'status',
            'prioridade',
            'nivel_atendimento',
            'tecnico',
            'atualizado_em',
            'atualizado_tecnico',
            'atualizado_colaborador'
        ])

        return redirect('ticket:ticket_detail', ticket_id=ticket.id)
    
    def atualiza_detalhes(self, request, ticket):
        form = TicketStatusForm(instance=ticket)
        mensagens = Mensagem.objects.filter(ticket=ticket).order_by('criado_em')
        historico_list = HistoricoTicket.objects.filter(ticket=ticket).order_by('data_criacao')

        context = self.get_context_data(ticket, form, historico_list, mensagens)
        return render(request, 'ticket/ticket_detail.html', context)

    def handle_ticket_actions(self, request, ticket):
        action = request.POST.get('action')
        is_tecnico = request.user == ticket.tecnico  # Determina se o usuário é o técnico responsável

        if ticket.status == 'F':  # Bloqueia envio de mensagens para tickets fechados
            if action == 'encerrar' or action == 'ativar':
                return self.ativar_ticket(request, ticket, is_tecnico)
            elif 'confirmar_btn' in request.POST:  # Permitir alterações via formulário
                form = TicketStatusForm(request.POST, instance=ticket)
                if form.is_valid():
                    return self.form_valid(form, ticket, request, ticket.status, ticket.prioridade, ticket.nivel_atendimento, ticket.tecnico)
                else:
                    messages.warning(request, 'Não foi possível salvar as alterações. Verifique os dados.')
                    return redirect('ticket:ticket_detail', ticket_id=ticket.id)
            else:
                messages.warning(request, 'Mensagens não podem ser enviadas para tickets fechados.')
                return redirect('ticket:ticket_detail', ticket_id=ticket.id)

        if action == 'encerrar':
            return self.encerrar_ticket(request, ticket, is_tecnico)
        elif action == 'ativar':
            return self.ativar_ticket(request, ticket, is_tecnico)
        elif 'enviar_mensagem' in request.POST:
            return self.enviar_mensagem(request, ticket)

        return redirect('ticket:ticket_detail', ticket_id=ticket.id)



    def encerrar_ticket(self, request, ticket, is_tecnico):
        novo_comentario = request.POST.get('conclusao')
        if novo_comentario:
            agora = timezone.now().strftime("%d/%m/%Y %H:%M:%S")
            novo_comentario_formatado = f"-----------------\n[{agora}]\n{novo_comentario}".strip()
            
            # Adiciona o novo comentário à conclusão anterior, se houver
            comentario_anterior = ticket.conclusao or ''
            if comentario_anterior:
                ticket.conclusao = f"{comentario_anterior}\n{novo_comentario_formatado}"
            else:
                ticket.conclusao = novo_comentario_formatado

            # Adiciona ao histórico do ticket
            ticket.add_historico(f'Conclusão: {novo_comentario}', request.user)
            
            # Atualiza os campos do ticket para indicar conclusão
            ticket.data_conclusao = timezone.now()
            ticket.ativo = False
            ticket.status = 'C'

            # Verifica o tipo de usuário para definir flags de atualização
            if is_tecnico:
                ticket.atualizado_colaborador = True
            else:
                ticket.atualizado_tecnico = True

            # Salva as mudanças
            ticket.save(update_fields=['conclusao', 'data_conclusao', 'ativo', 'status', 'atualizado_tecnico', 'atualizado_colaborador'])
            
            # Adiciona uma mensagem de sucesso para o Toastr
            messages.success(request, 'Ticket concluído com sucesso!')

        return redirect('ticket:dashboard')



    def ativar_ticket(self, request, ticket, is_tecnico):
        ticket.data_conclusao = None
        ticket.ativo = True
        ticket.status = 'R'
        
        # Adiciona um histórico indicando que o ticket foi reativado
        ticket.add_historico("Ticket reativado", request.user)
        
        # Define flags de atualização com base no tipo de usuário
        if is_tecnico:
            ticket.atualizado_colaborador = True
        else:
            ticket.atualizado_tecnico = True

        # Salva as mudanças no ticket
        ticket.save(update_fields=['data_conclusao', 'ativo', 'status', 'atualizado_tecnico', 'atualizado_colaborador'])
        
        # Adiciona uma mensagem de sucesso para o Toastr
        messages.success(request, 'Ticket reativado com sucesso!')

        return redirect('ticket:dashboard')


    def enviar_mensagem(self, request, ticket):
        texto = request.POST.get('texto')
        if texto:
            # Cria a mensagem associada ao ticket
            Mensagem.objects.create(ticket=ticket, autor=request.user, texto=texto)
            
            # Marca o ticket como atualizado recentemente
            ticket.atualizado_em = timezone.now()
            ticket.recently_updated = True
            
            # Define as flags `atualizado_tecnico` ou `atualizado_colaborador` com base no usuário atual
            if request.user == ticket.tecnico:
                ticket.atualizado_colaborador = True
                ticket.atualizado_tecnico = False  # Resetando para evitar duplicidade
            elif request.user == ticket.usuario:
                ticket.atualizado_tecnico = True
                ticket.atualizado_colaborador = False  # Resetando para evitar duplicidade
            
            # Adiciona a mensagem de sucesso para o Toastr
            messages.success(request, 'Mensagem enviada com sucesso!')
            
            # Salva as mudanças no ticket
            ticket.save(update_fields=['atualizado_em', 'recently_updated', 'atualizado_tecnico', 'atualizado_colaborador'])
        else:
            messages.warning(request, 'A mensagem não pode estar vazia.')
        
        return redirect('ticket:ticket_detail', ticket_id=ticket.id)


    def get_context_data(self, ticket, form, historico_list, mensagens):
        return {
            'ticket': ticket,
            'form': form,
            'mensagens': mensagens,
            'historico_list': historico_list,
            'is_closed': ticket.status == 'F',  # Indica se o ticket está fechado
        }

class CustomLoginView(LoginView):
    template_name = 'ticket/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')
