# KOTIZO v4.2 — ADMIN WEB COMPLET

## Derniere mise a jour : Mars 2026
## URL : admin.kotizo.app | Dev : http://localhost:3001
## Total : 14 pages

---

## STACK TECHNIQUE

```
Framework    : React 18 + Vite 5
Style        : Tailwind CSS 3
Graphiques   : Recharts
Carte        : React Simple Maps + GeoJSON
State        : Zustand
HTTP         : Axios
Auth         : JWT (endpoint separe admin)
```

---

## SECURITE ADMIN

### Login separe
```
Endpoint : POST /api/admin-panel/auth/login/
Verification cote serveur : is_staff = True OBLIGATOIRE
Si user normal -> HTTP 403 "Acces refuse"
Token stocke dans localStorage (admin_token)
```

### Roles et permissions
```
Super Admin  : Acces complet a toutes les sections
               Seul a pouvoir acceder a /staff
               Ne peut pas etre suspendu

Autres staff : Acces uniquement aux sections accordees
               Permissions definies dans StaffPermission
               3 niveaux par section :
               - read       : voir seulement
               - write      : voir + modifier
               - full       : voir + modifier + supprimer
```

---

## SIDEBAR

### Menu complet (14 pages)
```
Dashboard      -> /
Utilisateurs   -> /users
Verifications  -> /verifications
Transactions   -> /transactions
Remboursements -> /remboursements
Alertes fraude -> /alertes
Sanctions      -> /sanctions
Tickets        -> /tickets
Notifications  -> /notifications
WhatsApp       -> /whatsapp
Statistics     -> /statistics     (NOUVEAU v4.2)
Staff          -> /staff          (NOUVEAU v4.2 — Super Admin uniquement)
Configuration  -> /configuration
```

### Comportement sidebar
```
Plie   : 64px (icones uniquement)
Deplie : 240px (icones + labels)
Transition : 300ms smooth
Sections non autorisees : masquees automatiquement selon StaffPermission
```

---

## PAGES IMPLEMENTEES

### Dashboard (/)
```
Stats cards (10) cliquables :
- Nouveaux users aujourd'hui
- Users actifs total
- Transactions aujourd'hui
- Revenus Kotizo aujourd'hui (FCFA)
- Cotisations actives
- Quick Pay actifs
- Verifications en attente
- Remboursements en attente
- Alertes fraude nouvelles
- Tickets ouverts

Alertes urgentes :
- Banner rouge si alertes fraude > 0
- Banner jaune si verifications en attente > 0
- Banner orange si bot WhatsApp hors service

NOUVELLES SECTIONS v4.2 :

Revenus en temps reel :
- Gain Kotizo du jour (0.5%)
- Gain semaine / mois
- Comparaison mois precedent (+X%)

Repartition operateurs :
- Donut chart Moov / T-Money / Mixx
- Montants par operateur

Taux de succes paiements :
- Gauge chart global (%)
- Par operateur

Funnel inscription :
- Inscrits -> Verifies email/WA -> CNI soumis -> CNI approuves
- Barres horizontales avec pourcentages

Heatmap activite :
- Grille 7j x 24h
- Couleurs selon volume transactions
- Montre les heures de pointe

Top 10 cotisations actives :
- Nom, createur, montant collecte/objectif, progression

Suivi Quick Pay :
- QP crees aujourd'hui
- QP expires sans paiement (taux abandon)
- Repartition Mode Lien / Mode Direct
- Montant total transfere

Carte Togo detaillee :
- Repartition par ville (Lome, Kpalime, Sokode...)
- Couleur intensite selon nombre d'users

Suivi parrainage :
- Codes utilises ce mois
- Top parrains
- Progression vers ambassadeurs

Sante du systeme :
- Uptime bot WhatsApp (%)
- Temps reponse API moyen
- File attente Celery
- Redis memoire utilisee

Graphiques existants (connectes vraies donnees) :
- Area revenus 6 mois (Recharts)
- Donut repartition niveaux users
- Bar chart nouveaux users
- Line chart volume transactions
```

### Utilisateurs (/users)
```
Filtres : recherche + filtre niveau
Tableau 7 colonnes :
- Utilisateur (avatar initiale + pseudo + email)
- Niveau (badge colore)
- WhatsApp (numero + statut)
- Derniere activite
- Statut (Actif/Suspendu)
- Inscription
- Actions (Voir | Suspendre/Reactiver)

Modal detail : profil complet + code parrainage + ville
```

### Verifications (/verifications)
```
Grid cartes (un dossier par carte)
Chaque carte :
- Pseudo + email
- Photos recto/verso (liens Cloudinary)
- Date soumission
- Boutons [Approuver] [Rejeter]

Modal approbation :
- Prix : 1000 FCFA (Normal) | 500 FCFA (Reduit)
- Note obligatoire si 500 FCFA
```

### Transactions (/transactions)
```
Filtre statut : Tous | Complete | En attente | Echoue
Tableau 6 colonnes :
- Utilisateur, Type, Montant, Frais Kotizo, Statut, Date
Tri par date decroissante, limite 100
```

### Remboursements (/remboursements)
```
Liste demandes en attente
Modal detail :
- Info complete
- Bouton "Valider le remboursement"
- Bouton "Rejeter + signaler arnaque"
```

### Alertes fraude (/alertes)
```
Types avec couleurs :
- multi_comptes      : rouge
- signalements_multi : orange
- creation_rapide    : jaune
- numero_suspect     : violet
- fraude_paydunya    : rouge
- injection_ia       : bleu

Bouton "Faux positif" sur alertes nouvelles
```

### Sanctions (/sanctions)
```
Formulaire :
- ID utilisateur
- Niveau 0-5 (radio avec description)
- Raison (obligatoire)
- Bouton "Appliquer" (rouge)
```

### Tickets (/tickets)
```
Barre coloree priorite gauche
Priorites : urgente | haute | normale | faible
Badge "Via IA" si cree par agent
Bouton "Fermer" -> modal note resolution
```

### Notifications (/notifications)
```
Formulaire envoi notification globale :
- Titre (max 100 chars)
- Message (max 500 chars avec compteur)
- Canal : WhatsApp+InApp | WhatsApp | InApp
- Cibler : Tous | Basique | Verifie | Business
- Apercu temps reel
```

### WhatsApp (/whatsapp)
```
3 stats : Total | Actifs verifies | Inactifs
Tableau 5 colonnes :
- Utilisateur, Numero, Statut, Derniere activite, Actions
```

### Statistics (/statistics) — NOUVEAU v4.2
```
Filtre global : [Aujourd'hui] [7j] [30j] [90j] [Personnalise]

Onglet 1 — Finances :
- Revenus Kotizo (0.5%) -> Line chart
- Volume total transactions -> Area chart
- Repartition pay-in / pay-out -> Stacked bar
- Frais PayDunya generes -> Bar chart
- Montant moyen par transaction -> Line chart
- Taux de succes paiements -> Gauge (%)

Onglet 2 — Utilisateurs :
- Nouveaux inscrits -> Area chart
- Repartition niveaux -> Donut
- Funnel inscription -> Horizontal bar
- Taux verification CNI -> Gauge
- Croissance cumulative -> Line chart
- Repartition par pays -> Bar horizontal
- Heatmap activite 7j x 24h -> Grille coloree

Onglet 3 — Cotisations :
- Creees vs completees -> Grouped bar
- Taux de completion -> Gauge
- Montant moyen collecte -> Line chart
- Durees les plus utilisees -> Donut
- Recurrentes vs one-shot -> Donut
- Top createurs -> Tableau classement

Onglet 4 — Quick Pay :
- Crees vs payes vs expires -> Stacked bar
- Taux d'abandon -> Gauge
- Volume transfere -> Area chart
- Repartition Mode Lien vs Mode Direct -> Donut
- Montant moyen -> Line chart

Onglet 5 — Operateurs :
- Repartition Moov / T-Money / Mixx -> Donut
- Taux de succes par operateur -> Grouped bar
- Volume par operateur -> Area chart
- Transactions echouees par operateur -> Bar chart
```

### Staff (/staff) — NOUVEAU v4.2
```
ACCES : Super Admin uniquement

Liste membres staff :
Tableau : Membre | Email | Sections | Permission | Statut | Actions
Actions : Modifier | Suspendre/Reactiver

Formulaire ajout membre :
- Prenom *, Nom *
- Email *, Mot de passe *
- Sections accessibles (cases a cocher) :
  [ ] Dashboard       [ ] Utilisateurs
  [ ] Verifications   [ ] Transactions
  [ ] Remboursements  [ ] Alertes
  [ ] Sanctions       [ ] Tickets
  [ ] Notifications   [ ] WhatsApp
  [ ] Statistics      [ ] Configuration
- Niveau de permission par section :
  O Lecture seule
  O Lecture + Ecriture
  O Lecture + Ecriture + Suppression
- Bouton [Creer le compte]

Regles :
- Un staff ne voit que les sections cochees dans sa sidebar
- Super Admin : acces total, ne peut pas etre suspendu
- Suspension -> plus de connexion possible
```

### Configuration (/configuration)
```
Section "Promo verification" :
- Select duree (1/3/7/14/30 jours)
- Bouton "Lancer promo 500 FCFA"
- Bouton "Arreter"

Section "Bot WhatsApp admin" :
- Numero WhatsApp admin
- PIN (min 6 chiffres)

Section "Changer numero bot users" :
- Nouveau numero + Cle API Evolution

Section "Limites messages IA" :
- Messages/jour Basique (configurable)
- Messages/jour Verifie (= 2x Basique)
```

---

## ENDPOINTS BACKEND ADMIN

```
POST /api/admin-panel/auth/login/
GET  /api/admin-panel/dashboard/
GET  /api/admin-panel/stats-graphiques/
GET  /api/admin-panel/statistics/           (NOUVEAU — 5 onglets)
GET  /api/admin-panel/users/
GET  /api/admin-panel/users/{id}/
PATCH /api/admin-panel/users/{id}/
GET  /api/admin-panel/verifications/
POST /api/admin-panel/verifications/{id}/approuver/
POST /api/admin-panel/verifications/{id}/rejeter/
GET  /api/admin-panel/transactions/
GET  /api/admin-panel/remboursements/
POST /api/admin-panel/remboursements/{id}/traiter/
GET  /api/admin-panel/alertes/
PATCH /api/admin-panel/alertes/{id}/
POST /api/admin-panel/sanctions/
GET  /api/admin-panel/tickets/
PATCH /api/admin-panel/tickets/{id}/
GET  /api/admin-panel/whatsapp/numeros/
POST /api/admin-panel/promo-verification/
DELETE /api/admin-panel/promo-verification/
GET  /api/admin-panel/staff/               (NOUVEAU)
POST /api/admin-panel/staff/               (NOUVEAU)
PATCH /api/admin-panel/staff/{id}/         (NOUVEAU)
```
