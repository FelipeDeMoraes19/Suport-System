import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.contrib.auth import get_user_model

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('O nome de usuário deve ser fornecido.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='Os grupos aos quais este usuário pertence. Um usuário terá todas as permissões concedidas a cada um de seus grupos.',
        related_query_name='customuser',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Permissões específicas para este usuário.',
        related_query_name='customuser',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class DadoAnalise(models.Model):
    data_inicio = models.DateField(null=True, blank=True)
    data_conclusao = models.DateField(null=True, blank=True)
    texto = models.CharField(max_length=2)
    numero = models.PositiveSmallIntegerField(default=0)
    colaborador = models.CharField(max_length=20, null=True, blank=True)
    departamento = models.CharField(max_length=20, null=True, blank=True)
    quantidade_entrada = models.PositiveIntegerField(default=0)
    quantidade_saida = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Dado'

    def __str__(self) -> str:
        return f'{self.data_inicio} - {self.data_conclusao}, ({self.texto} / {self.numero})'


class Porcentagem(models.Model):
    dado = models.OneToOneField(DadoAnalise, on_delete=models.CASCADE)
    porcentagem = models.FloatField()

    def __str__(self):
        return f'{self.dado} - {self.porcentagem}'


class HistoricoTicket(models.Model):
    ticket = models.ForeignKey('Ticket', related_name='historico_entries', on_delete=models.CASCADE)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Histórico do Ticket'
        verbose_name_plural = 'Históricos dos Tickets'

    def __str__(self):
        return f'Histórico de {self.ticket} - {self.data_criacao.strftime("%d/%m/%Y %H:%M:%S")}'


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberto'),
        ('EA', 'Em Análise'),
        ('EE', 'Em Execução'),
        ('C', 'Concluído'),
        ('F', 'Fechado'),
        ('R', 'Reaberto'),
    ]

    PRIORIDADE_CHOICES = [
        ('N', 'Novo'),
        ('B', 'Baixa'),
        ('MB', 'Muito Baixa'),
        ('M', 'Média'),
        ('A', 'Alta'),
        ('MA', 'Muito Alta'),
    ]

    NIVEL_ATENDIMENTO_CHOICES = [
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3', 'N3'),
    ]

    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=100)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    anexo = models.FileField(upload_to='anexos/', blank=True, null=True)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='Novo')
    tipo = models.CharField(max_length=50)
    subtipo = models.CharField(max_length=50, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='A')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    data_conclusao = models.DateField(null=True, blank=True, verbose_name="Data de Conclusão")
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    tecnico = models.ForeignKey(get_user_model(), related_name='tickets_tecnico', on_delete=models.SET_NULL, null=True, blank=True)
    nivel_atendimento = models.CharField(max_length=2, choices=NIVEL_ATENDIMENTO_CHOICES, null=True, blank=True)
    recently_updated = models.BooleanField(default=False)
    conclusao = models.TextField(blank=True, null=True)
    atualizado_colaborador = models.BooleanField(default=False)
    atualizado_tecnico = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'{self.titulo} - {self.status}'

    def add_historico(self, message, usuario):
        HistoricoTicket.objects.create(ticket=self, mensagem=message, usuario=usuario)


class Mensagem(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    autor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    anexo = models.FileField(upload_to='attachments/', blank=True, null=True)

    def __str__(self):
        return f'{self.autor.email}: {self.texto[:20]}'
