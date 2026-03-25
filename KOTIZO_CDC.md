# KOTIZO v4.2 — CAHIER DES CHARGES COMPLET

## Derniere mise a jour : Mars 2026

---

## 1. PRESENTATION DU PRODUIT

### 1.1 Vision
Kotizo est une application mobile de cotisation collective et de transfert d'argent instantane destinee principalement a l'Afrique subsaharienne francophone, avec un focus sur le Togo et les pays voisins. Le nom "Kotizo" signifie "cotiser" en langue locale.

### 1.2 Positionnement
- Public cible : particuliers, groupes d'amis, associations, commercants
- Zone geographique : Togo (prioritaire), Benin, Cote d'Ivoire, Senegal, Cameroun, RD Congo
- Probleme resolu : la gestion manuelle des tontines/cotisations collectives et les transferts d'argent entre proches
- Differenciateur : double canal WhatsApp/in-app, deep links, verification identite, themes personnalisables

### 1.3 Tagline
**"Kotizo — Cotisez Ensemble, Simplement"**

---

## 2. STACK TECHNIQUE

### 2.1 Backend
```
Framework      : Django 5.x + Django REST Framework
Auth           : simplejwt (JWT access + refresh tokens)
Base de donnees: SQLite (dev) -> PostgreSQL (production)
Cache/Queue    : Redis 7 (Docker)
Workers        : Celery + Celery Beat
Logs           : KotizoLogger JSON custom
Monitoring     : Sentry
```

### 2.2 Mobile
```
Framework      : React Native + Expo SDK 55
Navigation     : React Navigation v6 (Stack + Bottom Tabs)
State          : Zustand (auth, theme)
HTTP           : Axios avec intercepteurs JWT
Notifications  : Firebase Cloud Messaging (FCM)
Images         : Cloudinary
```

### 2.3 Admin Web
```
Framework      : React 18 + Vite
Style          : Tailwind CSS 3
Graphiques     : Recharts
Carte          : React Simple Maps + GeoJSON
State          : Zustand
HTTP           : Axios
```

### 2.4 Services externes
```
Paiements      : PayDunya (Moov Money, Mixx by Yas, T-Money)
WhatsApp       : Evolution API (Docker)
IA             : Gemini 2.0 Flash
Push           : Firebase FCM
Emails         : Gmail + Brevo + Mailjet + Resend (1100/jour)
Images         : Cloudinary
```

### 2.5 Infrastructure
```
Conteneurs     : Docker Compose (Redis + Evolution API)
Production     : Nginx + Gunicorn
Deploiement    : Railway.app ou Render.com
```

---

## 3. URLS ET DOMAINES

```
kotizo.app              -> Application mobile (stores)
api.kotizo.app          -> Backend Django API
admin.kotizo.app        -> Dashboard admin
status.kotizo.app       -> Page statut
kotizo.app/c/[CODE]     -> Deep link cotisation
kotizo.app/qp/[CODE]    -> Deep link Quick Pay
kotizo.app/ref/[CODE]   -> Lien parrainage
```

---

## 4. ARCHITECTURE URLS BACKEND

```
/api/auth/              -> Authentification
/api/users/             -> Gestion utilisateurs
/api/cotisations/       -> Cotisations
/api/paiements/         -> Paiements et transactions
/api/quickpay/          -> Quick Pay
/api/notifications/     -> Notifications
/api/agent-ia/          -> Agent IA
/api/admin-panel/       -> Dashboard admin
/api/webhooks/          -> Webhooks PayDunya
/api/whatsapp/          -> Bot WhatsApp Evolution API
```

---

## 5. FONCTIONNALITES PRINCIPALES

### 5.1 Inscription et authentification

**Inscription :**
1. Saisie des coordonnees (prenom, nom, pseudo, email, WhatsApp, mdp)
2. Generation simultanee de tokens email OTP (6 chiffres) et WhatsApp valides 2 minutes
3. Blocage apres 3 tentatives echouees sur le meme numero pendant 24h
4. Choix du canal de verification : Email ou WhatsApp

**Canal Email :**
- OTP a 6 chiffres envoye par email
- Saisie du code dans l'app
- Si expire -> message d'expiration dans l'app + possibilite de recommencer en ressaisissant les coordonnees

**Canal WhatsApp :**
- Lien pre-rempli ouvre WhatsApp avec message predefini contenant le token
- L'utilisateur envoie le message au bot Kotizo
- Le bot valide et ouvre le compte automatiquement
- Si expire -> le bot ne repond pas du tout -> c'est l'APP qui detecte et affiche "temps expire"

**Securite inscription :**
- Blocage applique sur le NUMERO DE TELEPHONE (pas l'IP)
- Countdown visible dans l'app avant deblocage
- Token supprime de Redis apres validation reussie

**Connexion :**
- Identifiant : pseudo OU email
- Mot de passe
- Si numero CNI verifie -> saisie supplementaire du numero de carte (hash compare)

**Session unique :**
- Un compte = une session active a la fois
- Connexion sur nouvel appareil -> notification email + WhatsApp
- Ancienne session invalidee immediatement
- Page de confirmation : "C'est moi" ou "Signaler"
- Si signalement -> compte bloque + alerte admin

### 5.2 Cotisations

**Creation :**
- Nom, description, montant unitaire (200-250000 FCFA)
- Nombre de participants (min 2), duree (3/7/14/21/30 jours)
- Numero Mobile Money receveur
- Option recurrente (hebdomadaire/mensuel/trimestriel)
- Case a cocher : "Le prix peut etre modifie par les participants ?" (par defaut NON)
- Ecran de confirmation OBLIGATOIRE avant validation
- Generation d'un code unique 12 caracteres (KTZ-XXXXXXXXXXXX)
- Deep link unique : kotizo.app/c/[CODE]

**Rejoindre :**
- Saisie code ou lien complet ou deep link
- Deep link in-app : formulaire pre-rempli automatiquement avec coordonnees de la cotisation
- Choix du nombre d'unites (total unites x montant < 25000 FCFA par cotisation)
- Si createur a coche "prix modifiable" -> participant peut augmenter le montant (jamais en dessous du minimum)
- Ecran de confirmation avant paiement
- Recu avec option enregistrer comme image / telecharger PDF

**Regles metier cotisations :**
- Modification possible seulement si 0 participant paye
- Suppression : stopper d'abord -> attendre 48h -> supprimer de l'historique
- Toute suppression est SOFT DELETE (reste en base avec date_suppression)
- Reutilisation du code : 7 jours apres expiration
- Rappel automatique 12h avant expiration (email + WhatsApp)
- Commentaires possibles dans les 2 mois suivant l'adhesion, fermes apres
- Commentaires envoyes a l'admin -> reponse par WhatsApp uniquement (pas in-app)

**Limites par niveau :**
- Basique : 3 cotisations/jour, 12/semaine (fenetre glissante 7j)
- Verifie : 20 cotisations/jour
- Business : illimite

### 5.3 Quick Pay — DEUX MODES

**Mode 1 — Lien partageable (a distance)**

Cas d'usage : paiement a distance via WhatsApp, SMS, etc.

Flux :
1. Createur saisit : montant + note optionnelle
2. Systeme genere : code QP-XXXXXXXX + lien kotizo.app/qp/[CODE] valable 1 heure
3. Createur partage le lien au payeur
4. Payeur ouvre le lien, saisit LUI-MEME son numero Mobile Money
5. Payeur valide avec son PIN sur son telephone
6. PayDunya webhook confirme le pay-in
7. Kotizo declenche automatiquement le payout vers le numero du createur
8. Notifications des deux cotes

**Mode 2 — Paiement direct (presence physique)**

Cas d'usage : boutique, marche, transaction en face a face.

Flux :
1. Createur saisit : montant + numero Mobile Money du client + note optionnelle
2. Systeme envoie une demande PayDunya SoftPay avec le numero pre-rempli
3. Client recoit une notification USSD/SMS sur son telephone
4. Client saisit son PIN pour valider (timeout ~30 secondes)
5. PayDunya webhook confirme le pay-in
6. Kotizo declenche automatiquement le payout vers le numero du createur
7. Notifications des deux cotes
8. Si timeout depasse -> statut 'expire' + notification createur

**Frais Quick Pay (identiques pour les 2 modes) :**
```
Pay-in  (preleve au payeur)  : 2.0% du montant
Pay-out (debite a Kotizo)    : 2.5% du montant
Gain Kotizo                  : 0.5% du montant
Total frais payeur           : 5.0% du montant
Montant net receveur         : montant exact (sans frais)
```

**Regles Quick Pay :**
- On ne peut PAS rejoindre le Quick Pay d'un autre utilisateur
- Seul le createur gere son Quick Pay
- Lien Mode 1 expire en 1 heure
- Mode 2 timeout 30 secondes cote operateur
- Code unique : QP-XXXXXXXX (8 chars)

### 5.4 Reçus — 4 types distincts

**Type 1 — Recu de participation a une cotisation**
Declenche : apres paiement confirme en rejoignant une cotisation
Contient : nom cotisation, createur, ID participation (PART-XXXXXXXX), numero d'ordre, nb unites, prix/unite, sous-total, frais 5%, total paye, operateur, date, reference transaction
Options : enregistrer comme image / telecharger PDF / partager

**Type 2 — Recu de reversement cotisation (createur)**
Declenche : quand cotisation 100% complete, payout recu
Contient : nom cotisation, nb participants, montant collecte, frais Kotizo deduits, montant net recu, numero receveur (masque), operateur, date, reference payout
Options : enregistrer comme image / telecharger PDF / partager

**Type 3 — Recu Quick Pay payeur**
Declenche : apres avoir paye un Quick Pay
Contient : reference QP, pseudo du receveur, note, montant, frais 5%, total paye, operateur, date, reference transaction
Options : enregistrer comme image / telecharger PDF / partager

**Type 4 — Recu Quick Pay receveur (createur)**
Declenche : apres reception payout Quick Pay
Contient : reference QP, numero payeur masque, note, montant brut, frais Kotizo deduits, montant net recu, operateur, date, reference payout
Options : enregistrer comme image / telecharger PDF / partager

**Implementation :** Un seul ecran RecuScreen avec parametre `type` parmi :
participation | reversement_cotisation | quickpay_payeur | quickpay_receveur

### 5.5 Verification d'identite

1. Photo recto CNI/CIE/CNE/carte etudiant
2. Photo verso CNI/CIE/CNE/carte etudiant
3. Saisie manuelle du numero de carte (stocke en hash SHA256, jamais en clair)
4. Attente validation admin (24-48h)
5. Notification approbation/rejet par WhatsApp + email + in-app
6. Apres approbation : nom/prenom verrouilles definitivement

**Prix :**
- Normal : 1000 FCFA
- Promo/etudiant : 500 FCFA (lance par l'admin)

### 5.6 Niveaux utilisateurs

```
BASIQUE (gratuit)
- 3 cotisations/jour, 12/semaine glissante
- Pseudo visible uniquement publiquement
- Limite messages IA/jour

VERIFIE (1000 FCFA ou 500 promo)
- 20 cotisations/jour
- Coche verte sur le profil
- Nom + Prenom visibles sur les recus
- Plus de messages IA/jour

BUSINESS (5000 FCFA/an)
- Cotisations illimitees
- Coche bleue sur le profil
- Support prioritaire
- Statistiques avancees
- Messages IA illimites

AMBASSADEUR VERIFIE GRATUIT
- 50 parrainages OU 25 filleuls ayant fait 3+ cotisations

AMBASSADEUR BUSINESS GRATUIT
- 100 parrainages OU 50 filleuls ayant fait 3+ transactions
```

### 5.7 Themes personnalisables

L'utilisateur peut choisir son theme dans Parametres -> Apparence.
3 themes disponibles :

```
VERT AFRIQUE (defaut)
- Background  : #0A1A0F
- Card        : #0D2B14
- Primary     : #16A34A
- Accent      : #22C55E
- Logo        : version verte

VIOLET PREMIUM
- Background  : #0E0A1F
- Card        : #1A1040
- Primary     : #7C3AED
- Accent      : #A78BFA
- Logo        : version violette

BLEU CLASSIC
- Background  : #0A0F1E
- Card        : #111827
- Primary     : #2563EB
- Accent      : #3B82F6
- Logo        : version bleue

COMMUN (tous themes) :
- Success     : #22C55E
- Error       : #EF4444
- Warning     : #F59E0B
- TextPrimary : #FFFFFF
- TextSecondary: rgba(255,255,255,0.6)
- TextTertiary : rgba(255,255,255,0.3)
- Border      : rgba(255,255,255,0.06)
```

Stockage : AsyncStorage (mobile) / localStorage (admin)
State : Zustand themeStore
Le logo SVG s'adapte automatiquement via la variable primary du theme actif.

### 5.8 Agent IA

- Modele : Gemini 2.0 Flash
- Historique : 100 derniers messages charges
- Reinitialisation compteur : minuit chaque jour
- Synchronisation WhatsApp/in-app : conversations identiques
- Si limite atteinte in-app -> continuer sur WhatsApp
- Anti-injection : 7 couches de filtrage
- Si non verifie : limite messages in-app, reste sur WhatsApp

### 5.9 Tarification

```
Frais Kotizo         : 0.5% du montant
Frais PayDunya PayIn : 2.0% du montant
Frais PayDunya PayOut: 2.5% du montant
Total frais payeur   : 5.0% du montant

Montant minimum      : 200 FCFA
Montant maximum      : 250 000 FCFA par transaction
Limite cotisation    : 25 000 FCFA par participant par cotisation
```

---

## 6. SECURITE

### 6.1 Authentification
- JWT access token (30 min) + refresh token (7 jours)
- Session unique par compte
- Notification connexion nouvel appareil
- Double facteur optionnel (numero CNI)

### 6.2 Paiements
- Hash webhook PayDunya : SHA512(MASTER_KEY)
- TOUJOURS request.POST pour les webhooks PayDunya (jamais json.loads)
- Validation montants cote serveur
- Anti-fraude automatique (Celery toutes les 30 minutes)

### 6.3 Bot WhatsApp
- Delai aleatoire reponses : random.uniform(3, 6) secondes
- Blocage sur numero telephone (pas IP)
- Tokens inscription expires geres par Redis
- Token supprime de Redis apres validation reussie

### 6.4 Admin
- Endpoint login separe : /api/admin-panel/auth/login/
- Verification is_staff cote serveur
- Permissions granulaires par section (StaffPermission)
- Pas d'acces admin possible avec compte utilisateur normal

### 6.5 Donnees
- Soft delete partout
- Logs JSON structures avec timestamp, module, action, duree
- Numero CNI stocke en hash SHA256 (jamais en clair)

---

## 7. SOFT DELETE — PRINCIPE GLOBAL

Toute suppression dans l'app est une suppression LOGIQUE :
- Champ supprime = True
- Champ date_suppression enregistre
- Element invisible dans l'interface utilisateur
- Toujours visible dans le panneau admin
- Jamais efface physiquement de la base de donnees

Concerne : cotisations, participations, notifications,
historiques Quick Pay, commentaires, sessions

---

## 8. DEEP LINKS

```
Format cotisation  : kotizo.app/c/KTZ-XXXXXXXXXXXX
Format Quick Pay   : kotizo.app/qp/QP-XXXXXXXX
Format parrainage  : kotizo.app/ref/[CODE_PARRAINAGE]

Comportement :
- Si app installee -> ouvre directement le formulaire pre-rempli
- Si app non installee -> redirige vers le store
- Le code est pre-rempli dans le champ de saisie
- Les coordonnees de la cotisation s'affichent automatiquement
```

---

## 9. NOTIFICATIONS

### 9.1 Types
- Paiement recu/confirme
- Cotisation complete
- Cotisation expiree (rappel 12h avant)
- Quick Pay paye / expire
- Nouvelle connexion detectee
- Verification identite approuvee/rejetee
- Reponse admin sur commentaire
- Promotion verification
- Messages systeme Kotizo

### 9.2 Canaux
- In-app (notification centre)
- Push FCM
- WhatsApp (si numero verifie)
- Email

### 9.3 Synchronisation WhatsApp/App
Les conversations WhatsApp et in-app sont identiques.
Message in-app -> envoye aussi sur WhatsApp si numero verifie.
Message WhatsApp -> visible dans l'app.

---

## 10. CODES ET IDENTIFIANTS

```
Code cotisation    : KTZ-XXXXXXXXXXXX (12 chars)
Code Quick Pay     : QP-XXXXXXXX (8 chars)
ID participation   : PART-XXXXXXXX
Code parrainage    : 8 chars alphanumeriques

Validite lien cotisation : duree cotisation + 7 jours
Validite lien Quick Pay  : 1 heure (Mode 1)
Timeout Mode Direct QP   : 30 secondes (cote operateur)
Reutilisation code cot.  : 7 jours apres expiration
```

---

## 11. CONTRAINTES TECHNIQUES

### Regles absolues de developpement
- Pas d'emoji dans le code ni l'UI (Ionicons uniquement)
- Commentaires minimalistes dans le code
- Commandes PowerShell Windows 11 copy-paste ready
- Fichiers complets fournis (pas de diffs partiels)
- Toutes les dependances Node en une commande chainee
- DIM valide AVANT tout code mobile
- git add + commit + push integre dans chaque etape

### Environnement de developpement
- OS         : Windows 11
- Repertoire : E:\kotizo-v4.2
- Python     : 3.12
- Node.js    : v24
- Docker Desktop
- IDE        : VS Code
- Expo Go sur Android pour tests
- Repo       : https://github.com/AHOURMAROLAND/kotizo-v4.2.git
```
