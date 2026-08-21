# Agendia

Sistema de agendamento online para pequenos negócios (salões, barbearias, clínicas), com confirmação automática, lembretes por e-mail/WhatsApp e agenda visível para o dono do negócio.

**Projeto acadêmico** desenvolvido com Django, focado em resolver um problema real e recorrente de pequenos negócios no Brasil: a substituição do agendamento manual por WhatsApp por um sistema online completo.

🔗 **Deploy:** https://agendia-jln0.onrender.com

---

## Índice

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura e stack técnica](#arquitetura-e-stack-técnica)
- [Decisões técnicas e por quê](#decisões-técnicas-e-por-quê)
- [Limitações conhecidas e como foram contornadas](#limitações-conhecidas-e-como-foram-contornadas)
- [Como rodar localmente](#como-rodar-localmente)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes automatizados](#testes-automatizados)
- [Roadmap futuro](#roadmap-futuro)

---

## Visão geral

O Agendia resolve um problema muito comum em pequenos negócios de serviço: a agenda inteira sendo controlada manualmente pelo dono via WhatsApp, com risco constante de erro humano, esquecimento e conflito de horário.

O sistema oferece dois fluxos completamente separados:

- **Cliente final**: acessa um link público único do negócio (ex: `/agendar/barbearia-do-ze/`), escolhe um serviço, data e horário, e agenda sem precisar criar conta.
- **Dono do negócio**: se cadastra, gerencia serviços, acompanha a agenda em tempo real e confirma/cancela/conclui atendimentos, tudo isolado dos outros negócios cadastrados no sistema (multi-tenant).

## Funcionalidades

- Cadastro de negócio (auto-serviço, sem precisar de intervenção manual do desenvolvedor)
- CRUD completo de serviços (nome, duração, preço)
- Agendamento público com seleção de data (calendário nativo) e horário em intervalos de 30 minutos
- **Validação automática de conflito de horário**, testada com testes automatizados
- Painel do dono com listagem de agendamentos e ações de confirmar / cancelar / concluir
- Notificação automática por e-mail em três eventos: confirmação, cancelamento e lembrete (24h antes)
- Integração com WhatsApp Business Cloud API implementada no código (ver seção de limitações)
- Isolamento de dados por negócio (um dono nunca acessa dados de outro)
- Link público copiável no painel, para o dono compartilhar com os clientes

## Arquitetura e stack técnica

| Camada | Tecnologia |
|---|---|
| Backend | Django 6.1 |
| Banco de dados | PostgreSQL (produção) / SQLite (dev local) |
| Fila assíncrona (dev) | Celery + Redis |
| Front-end | Django Templates + Bootstrap 5 + Bootstrap Icons |
| E-mail transacional | Brevo API (produção) / SMTP Gmail (dev local) |
| WhatsApp | Meta Cloud API (implementado, ver limitações) |
| Deploy | Render (Web Service + PostgreSQL, free tier) |
| Servidor WSGI | Gunicorn + WhiteNoise (arquivos estáticos) |

### Diagrama de fluxo de notificação

```
Cliente agenda (view pública)
        │
        ▼
appointment.full_clean()  ──► valida conflito de horário
        │
        ▼
appointment.save()
        │
        ▼
run_in_background(send_confirmation_notification, id)
        │
        ├──► send_whatsapp_message()  (Meta Cloud API)
        │
        └──► send_email_via_api()     (Brevo API em prod / SMTP em dev)
```

## Decisões técnicas e por quê

**Modelagem multi-tenant desde o início.** Cada `Business` tem um `owner` (`User`) próprio, e toda query do painel filtra explicitamente por esse dono, nunca confiando apenas na interface para esconder dados de outros negócios. Usuários criados via cadastro público nunca recebem `is_staff`/`is_superuser`, o que bloqueia nativamente o acesso ao Django Admin.

**Validação de conflito de horário no nível do model (`clean()`), não só no formulário.** Regra de negócio crítica nunca deve depender só de validação client-side.

**Celery com `CELERY_TASK_ALWAYS_EAGER` controlado por variável de ambiente.** Em desenvolvimento local, as notificações rodam de forma assíncrona de verdade (worker + broker Redis + Celery Beat para lembretes periódicos), demonstrando a arquitetura de fila completa. Em produção, como não há orçamento para hospedar um worker persistente 24/7, a mesma função roda de forma síncrona (`ALWAYS_EAGER=True`), sem exigir nenhuma mudança de código, apenas uma variável de ambiente diferente.

**Envio de notificação em thread separada (`run_in_background`).** Mesmo em modo síncrono, o envio de e-mail/WhatsApp nunca deve bloquear a resposta ao usuário. Uma thread simples desacopla o tempo de resposta da página do tempo de envio da notificação, evitando timeout do servidor Gunicorn.

## Limitações conhecidas e como foram contornadas

### WhatsApp Business API — restrição de país

A partir de setembro de 2025, a Meta implementou uma restrição temporária de mensagens comerciais entre países envolvendo o Brasil: contas de WhatsApp Business fora do Brasil não conseguem enviar mensagens para números brasileiros. O número de teste (sandbox) fornecido gratuitamente pela Meta é americano, o que impede testar o envio real sem uma linha telefônica brasileira dedicada, o que teria custo mensal recorrente, fora do escopo de um projeto sem orçamento.

**Solução adotada:** a função `send_whatsapp_message()` está implementada e pronta com a chamada HTTP real à Meta Cloud API. Em ausência de credenciais configuradas, ela cai em modo de simulação (log no console), preservando a arquitetura pronta para produção assim que uma linha dedicada estiver disponível. O e-mail assumiu o papel de canal de notificação validado de ponta a ponta.

### SMTP bloqueado em hospedagem gratuita

Provedores de hospedagem gratuita (Render incluso) bloqueiam por padrão conexões de saída SMTP (portas 25/465/587) para prevenir abuso, isso derruba o envio de e-mail via SMTP tradicional em produção, mesmo com credenciais corretas.

**Solução adotada:** notificações por e-mail em produção usam a API HTTP da Brevo (porta 443, não bloqueada), enquanto o ambiente de desenvolvimento local continua usando SMTP simples via Gmail. A função `send_email_via_api()` alterna automaticamente entre os dois modos, dependendo da presença da variável `BREVO_API_KEY`.

### Lembrete automático (Celery Beat) não roda em produção

Como o worker/scheduler do Celery não está hospedado em produção (decisão de custo), o lembrete de 24h antes do agendamento não é disparado automaticamente no ambiente publicado, apenas localmente, onde a demonstração completa foi validada. As notificações de confirmação e cancelamento, que dependem apenas de eventos (não de agendamento periódico), funcionam normalmente em produção.

## Como rodar localmente

```bash
# Clonar o repositório
git clone https://github.com/Alceu-2004/Agendia.git
cd Agendia

# Ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Dependências
pip install -r requirements.txt

# Variáveis de ambiente (.env na raiz)
# EMAIL_HOST_USER=seuemail@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail

# Banco de dados
python manage.py migrate
python manage.py createsuperuser

# Redis (via Docker, necessário para Celery)
docker run -d -p 6379:6379 --name agendia-redis redis

# Rodar em 3 terminais separados:
python manage.py runserver
celery -A core worker --loglevel=info --pool=solo   # Windows
celery -A core beat --loglevel=info
```

Acesse `http://127.0.0.1:8000`.

## Estrutura do projeto

```
Agendia/
├── core/               # Settings, URLs raiz, configuração Celery
├── business/           # Business, Service, cadastro, CRUD de serviços
├── scheduling/         # Appointment, fluxo público, painel, notificações
│   ├── tasks.py        # Tasks Celery (e-mail, WhatsApp, lembretes)
│   ├── utils.py        # Helper de execução em background (threading)
│   └── forms.py        # Formulários com validação de data/hora
├── templates/           # Templates base, home, login, cadastro
└── requirements.txt
```

## Testes automatizados

A regra de negócio mais crítica do sistema, bloqueio de conflito de horário é coberta por testes automatizados:

```bash
python manage.py test
```

## Roadmap futuro

- [ ] Linha telefônica dedicada para ativar WhatsApp real em produção
- [ ] Worker Celery hospedado para reativar lembretes automáticos em produção
- [ ] Edição de dados do próprio negócio (horário de funcionamento, telefone) pelo painel
- [ ] Relatórios de faturamento e histórico de atendimentos concluídos
- [ ] Suporte a múltiplos profissionais por negócio

---

Desenvolvido por Alceu Botelho.
