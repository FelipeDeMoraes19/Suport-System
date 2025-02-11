# Sistema de Suporte Baseado em Tickets

[![Django](https://img.shields.io/badge/Django-3.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)

Sistema de gerenciamento de tickets de suporte com autenticação de usuários, histórico de alterações e chat integrado.

## Principais Funcionalidades

- **Criação de Tickets**:
  - Formulário com campos dinâmicos
  - Anexo de arquivos com nomeamento automático
  - Classificação por tipo e subtipo
  
- **Gerenciamento de Tickets**:
  - Atualização de status (Aberto, Em Análise, Concluído, etc.)
  - Atribuição de prioridade e técnico responsável
  - Filtragem por status e paginação

- **Sistema de Chat Integrado**:
  - Troca de mensagens entre usuário e técnico
  - Anexo de imagens e arquivos
  - Notificação de novas mensagens

- **Histórico de Alterações**:
  - Registro detalhado de todas as modificações
  - Controle de atualizações recentes

- **Autenticação e Segurança**:
  - Sistema de login customizado
  - Controle de acesso por permissões
  - Proteção contra duplicação de tickets

## 🛠 Tecnologias Utilizadas

- **Backend**:
  - Django 3.2+
  - Python 3.9+

- **Frontend**:
  - HTML
  - CSS
  - JavaScript
  - Bootstrap 5
 
## 🚀 Instalação

1. **Clonar repositório**:
   ```bash
   git clone https://github.com/FelipeDeMoraes19/Suport-System.git
   cd Suport-System
   ```
2. Instalar Dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Coletar arquivos estáticos:
   ```bash
   python manage.py collectstatic
   ```
     



   
   
