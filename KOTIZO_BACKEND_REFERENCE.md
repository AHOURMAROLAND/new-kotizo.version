# KOTIZO v4.2 — REFERENCE BACKEND COMPLETE

## Derniere mise a jour : Mars 2026

---

## STRUCTURE DU PROJET

```
kotizo-backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── core/
│   ├── logger.py        KotizoLogger JSON custom
│   ├── middleware.py
│   ├── decorators.py    @require_verified, @throttle_cotisation
│   ├── permissions.py   IsAdminKotizo, IsVerified, HasStaffPermission
│   ├── utils.py         calculer_frais, generer_code, detecter_operateur
│   ├── email_router.py
│   ├── whatsapp.py
│   └── tasks.py
├── users/
├── cotisations/
├── paiements/
├── quickpay/
├── notifications/
├── agent_ia/
├── admin_panel/
├── run.py
├── .env
└── docker-compose.yml
```

---

## MODELES PRINCIPAUX

### User (users/models.py)
```python
id                    UUID primary key
email                 unique
pseudo                unique, max 20 chars
nom, prenom           requis, verrouilles apres verification
telephone             +228XXXXXXXXX
whatsapp_numero       +228XXXXXXXXX
whatsapp_verifie      bool
email_verifie         bool
niveau                basique | verifie | business
identite_verifiee     bool
numero_cni_hash       SHA256 (jamais en clair)
code_parrainage       8 chars unique
admin_role            null | super_admin | moderateur | support | finance | verification | lecteur
date_inscription      datetime
last_login            datetime
theme_preference      vert | violet | bleu (defaut: vert)
cotisations_creees_fenetre  int
nb_parrainages_actifs int
ville_approx          string
pays                  code ISO 2
fcm_token             push notifications
is_active             bool
is_staff              bool
```

### StaffPermission (admin_panel/models.py) — NOUVEAU v4.2
```python
id                    int
staff_user            FK User (is_staff=True)
section               dashboard | users | verifications |
                      transactions | remboursements | alertes |
                      sanctions | tickets | notifications |
                      whatsapp | statistics | staff | configuration
permission_level      read | write | full
actif                 bool
cree_par              FK User (super admin)
date_creation         datetime
```

### Cotisation (cotisations/models.py)
```python
id                    UUID
createur              FK User
nom                   max 100
description           text optionnel
montant_unitaire      Decimal(10,2)
nombre_participants   int
participants_payes    int
montant_collecte      Decimal
nb_jours              int (3,7,14,21,30)
date_creation         datetime
date_expiration       datetime
statut                active | complete | expiree | stoppee
slug                  KTZ-XXXXXXXXXXXX unique
deep_link             kotizo.app/c/{slug}
est_recurrente        bool
config_recurrence     JSON
numero_receveur       +228XXXXXXXXX
prix_modifiable       bool (defaut False)
paydunya_invoice_url  string
supprime              bool
date_suppression      datetime null
supprime_par          FK User null
```

### Participation (cotisations/models.py)
```python
id                    UUID
cotisation            FK Cotisation
participant           FK User
montant               Decimal
nb_unites             int
montant_par_unite     Decimal (peut differ si prix modifie)
statut                en_attente | paye | rembourse
date_participation    datetime
rang_paiement         int
paydunya_token        string
supprime              bool
date_suppression      datetime null
```

### QuickPay (quickpay/models.py)
```python
id                    UUID
createur              FK User
code                  QP-XXXXXXXX unique
mode                  lien | direct                  (NOUVEAU v4.2)
montant               Decimal
montant_avec_frais    Decimal
frais_kotizo          Decimal
numero_receveur       +228XXXXXXXXX (createur)
numero_payeur         +228XXXXXXXXX (rempli apres paiement pour Mode 1
                                     ou saisi par createur pour Mode 2)
description           text optionnel
statut                actif | paye | expire | timeout (NOUVEAU v4.2)
date_creation         datetime
date_expiration       datetime (creation + 1h pour Mode 1)
timeout_direct        bool (defaut False — Mode 2 uniquement)
paydunya_token        string null
```

### Transaction (paiements/models.py)
```python
id                    UUID
user                  FK User
type_transaction      payin | payout | remboursement
montant               Decimal
frais_kotizo          Decimal
frais_paydunya        Decimal
statut                en_attente | complete | echoue
canal                 MOOV_TOGO | MIXX_TOGO | TMONEY_TOGO
paydunya_token        string
paydunya_reference    string
date_creation         datetime
```

### Notification (notifications/models.py)
```python
id                    int
user                  FK User
type_notification     paiement_recu | cotisation_complete |
                      cotisation_expiree | quickpay_expire |
                      verification_approuvee | verification_rejetee |
                      sanction | remboursement | ambassadeur |
                      promo_verification | systeme |
                      whatsapp_panne | rappel
titre                 max 200
message               text
lue                   bool
data                  JSON
date_creation         datetime
supprime              bool
date_suppression      datetime null
```

---

## ENDPOINTS API PRINCIPAUX

### Auth
```
POST /api/auth/inscription/
POST /api/auth/connexion/
POST /api/auth/token/refresh/
POST /api/auth/verification-email/
POST /api/auth/verification-wa/
POST /api/auth/mot-de-passe-oublie/
POST /api/auth/changer-mot-de-passe/
POST /api/auth/confirmer-action/
GET  /api/auth/verifier-cni/
```

### Users
```
GET   /api/users/moi/
PATCH /api/users/moi/
PATCH /api/users/moi/theme/              (NOUVEAU — changer theme)
DELETE /api/users/moi/
GET   /api/users/stats/
GET   /api/users/stats/financieres/
GET   /api/users/parrainage/stats/
POST  /api/users/verification/soumettre/
GET   /api/users/sessions/
DELETE /api/users/sessions/{id}/
POST  /api/users/demande-business/
POST  /api/users/reclamations/
```

### Cotisations
```
GET    /api/cotisations/
POST   /api/cotisations/
GET    /api/cotisations/{slug}/
POST   /api/cotisations/{slug}/rejoindre/
POST   /api/cotisations/{slug}/payer/
POST   /api/cotisations/{slug}/stopper/
DELETE /api/cotisations/{slug}/
POST   /api/cotisations/{slug}/rappel/
GET    /api/cotisations/mes-participations/
GET    /api/cotisations/mes-stats/
GET    /api/cotisations/participations/{id}/
POST   /api/cotisations/{slug}/commentaire/
```

### Quick Pay
```
GET   /api/quickpay/
POST  /api/quickpay/                     (mode: lien | direct)
GET   /api/quickpay/{id}/
POST  /api/quickpay/{id}/payer/          (Mode 1 uniquement)
POST  /api/quickpay/{id}/direct/         (Mode 2 — envoie SoftPay)
GET   /api/quickpay/recus/
GET   /api/quickpay/stats/
```

### Paiements
```
GET  /api/paiements/historique/
GET  /api/paiements/statut/{part_id}/
```

### Notifications
```
GET    /api/notifications/
GET    /api/notifications/non-lues/
POST   /api/notifications/tout-lire/
POST   /api/notifications/{id}/lire/
DELETE /api/notifications/{id}/
POST   /api/notifications/admin/envoyer/
```

### Agent IA
```
GET  /api/agent-ia/historique/
POST /api/agent-ia/message/
```

### Webhooks
```
POST /api/webhooks/paydunya/cotisation/
POST /api/webhooks/paydunya/quickpay/
POST /api/webhooks/paydunya/payout/
POST /api/whatsapp/webhook/
```

---

## REGLES CRITIQUES

### PayDunya webhooks
```python
# TOUJOURS request.POST — JAMAIS json.loads(request.body)
statut = request.POST.get('data[status]', '')
token  = request.POST.get('data[invoice_token]', '')

import hashlib
hash_recu    = request.POST.get('data[hash]', '')
hash_calcule = hashlib.sha512(settings.PAYDUNYA_MASTER_KEY.encode()).hexdigest()
if hash_recu != hash_calcule:
    return HttpResponse(status=400)
```

### PayDunya SoftPay Mode Direct (Quick Pay)
```python
import requests

def envoyer_softpay_direct(operateur, phone_number, payment_token, nom_client=''):
    endpoints = {
        'MOOV_TOGO' : 'https://app.paydunya.com/api/v1/softpay/moov-togo',
        'MIXX_TOGO' : 'https://app.paydunya.com/api/v1/softpay/mixx-togo',
        'TMONEY_TOGO': 'https://app.paydunya.com/api/v1/softpay/t-money-togo',
    }
    url = endpoints[operateur]
    payload = {
        'phone_number'  : phone_number,
        'payment_token' : payment_token,
        'customer_name' : nom_client,
    }
    headers = {
        'PAYDUNYA-MASTER-KEY' : settings.PAYDUNYA_MASTER_KEY,
        'PAYDUNYA-PUBLIC-KEY' : settings.PAYDUNYA_PUBLIC_KEY,
        'PAYDUNYA-PRIVATE-KEY': settings.PAYDUNYA_PRIVATE_KEY,
        'PAYDUNYA-TOKEN'      : settings.PAYDUNYA_TOKEN,
        'Content-Type'        : 'application/json',
    }
    response = requests.post(url, json=payload, headers=headers, timeout=35)
    return response.json()
    # Si success=False apres 30s -> statut QuickPay = 'timeout'
```

### Detection operateur
```python
# core/utils.py
def detecter_operateur(telephone):
    numero = telephone.replace('+228', '').replace(' ', '')
    prefixe = int(numero[:2])
    moov  = [90,91,92,93,94,95,96,97]
    mixx  = [70,71,72,79]
    tmoney= [98,99]
    if prefixe in moov:   return 'MOOV_TOGO'
    if prefixe in mixx:   return 'MIXX_TOGO'
    if prefixe in tmoney: return 'TMONEY_TOGO'
    raise ValueError(f"Operateur inconnu pour le prefixe {prefixe}")
```

### Frais Kotizo
```python
# core/utils.py
def calculer_frais_kotizo(montant):
    return round(float(montant) * 0.005, 0)

def calculer_total_participant(montant):
    return round(float(montant) * 1.05, 0)

def calculer_montant_net(montant):
    return round(float(montant) - calculer_frais_kotizo(montant), 0)
```

### Bot WhatsApp
```python
import random, time
time.sleep(random.uniform(3, 6))  # JAMAIS delai fixe
```

### Fenetre glissante 7j
```python
from django.utils import timezone
il_y_a_7j = timezone.now() - timezone.timedelta(days=7)
nb = Cotisation.objects.filter(
    createur=user,
    date_creation__gte=il_y_a_7j
).count()
```

### Compteurs IA (Redis uniquement)
```python
from django.core.cache import cache
from django.utils import timezone
date_today = timezone.now().date().strftime('%Y-%m-%d')
key = f'ia_msgs_{user.id}_{date_today}'
count = cache.get(key, 0)
```

### Permission staff
```python
# core/permissions.py
class HasStaffPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        section = getattr(view, 'required_section', None)
        level   = getattr(view, 'required_level', 'read')
        if request.user.admin_role == 'super_admin':
            return True
        perm = StaffPermission.objects.filter(
            staff_user=request.user,
            section=section,
            actif=True
        ).first()
        if not perm:
            return False
        levels = {'read': 1, 'write': 2, 'full': 3}
        return levels.get(perm.permission_level, 0) >= levels.get(level, 1)
```

---

## VARIABLES D'ENVIRONNEMENT (.env)

```bash
# Django
SECRET_KEY=django-insecure-[GENERER_UNE_CLE_FORTE]
DEBUG=True
ALLOWED_HOSTS=*

# Base de donnees
DATABASE_URL=sqlite:///db.sqlite3

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379/0

# PayDunya (Sandbox)
PAYDUNYA_MASTER_KEY=
PAYDUNYA_PUBLIC_KEY=
PAYDUNYA_PRIVATE_KEY=
PAYDUNYA_TOKEN=
PAYDUNYA_MODE=test

# Evolution API (WhatsApp)
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=kotizo-evolution-key-2026
EVOLUTION_INSTANCE=kotizo

# Gemini IA
GEMINI_API_KEY=

# Firebase FCM
FCM_SERVER_KEY=

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Email principal
GMAIL_USER=
GMAIL_APP_PASSWORD=

# Emails secondaires
BREVO_API_KEY=
MAILJET_API_KEY=
MAILJET_SECRET_KEY=
RESEND_API_KEY=

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8081

# Sentry
SENTRY_DSN=
```

---

## DOCKER COMPOSE

```yaml
services:
  kotizo_redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  kotizo_evolution:
    image: atendai/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      - EVOLUTION_API_KEY=kotizo-evolution-key-2026
      - WEBHOOK_GLOBAL_URL=http://host.docker.internal:8000/api/whatsapp/webhook/
    restart: unless-stopped
```

---

## LANCEMENT EN DEVELOPPEMENT

```powershell
# 1 — Docker
cd "E:\kotizo-v4.2"
docker compose up -d

# 2 — Backend Django
cd "E:\kotizo-v4.2\kotizo-backend"
.\venv\Scripts\activate
python run.py runserver 0.0.0.0:8000

# 3 — Celery Worker
cd "E:\kotizo-v4.2\kotizo-backend"
.\venv\Scripts\activate
celery -A config worker --loglevel=info --pool=solo

# 4 — Celery Beat
cd "E:\kotizo-v4.2\kotizo-backend"
.\venv\Scripts\activate
celery -A config beat --loglevel=info

# 5 — Admin Web
cd "E:\kotizo-v4.2\kotizo-admin"
npm start

# 6 — Mobile Expo
cd "E:\kotizo-v4.2\kotizo-mobile"
npx expo start --tunnel

# 7 — ngrok (si mobile via partage connexion)
ngrok http 8000
```

---

## run.py (Windows asyncio fix)

```python
import asyncio, sys, os
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
```
