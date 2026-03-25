# KOTIZO v4.2 — LOGIQUE METIER COMPLETE

## Derniere mise a jour : Mars 2026

---

## 1. INSCRIPTION ET AUTHENTIFICATION

### 1.1 Flux inscription complet

```
ETAPE 1 — Saisie coordonnees
Input  : prenom, nom, pseudo, email, telephone_whatsapp, password, cgu_acceptees
Valide : pseudo unique, email unique, telephone format +228XXXXXXXXX
Genere : code_parrainage (8 chars unique)

ETAPE 2 — Generation tokens simultanees
Redis key email   : inscription_email_{email}      TTL: 120 secondes (2 min)
Redis key whatsapp: inscription_wa_{telephone}      TTL: 120 secondes (2 min)
Valeur            : OTP 6 chiffres ou token unique

ETAPE 3 — Choix canal
Option A : Email OTP -> l'utilisateur saisit le code dans l'app
Option B : WhatsApp -> lien ouvre WA avec message predefini contenant le token

ETAPE 4 — Validation
Si OTP email correct ET dans les 2 min -> compte cree + email_verifie=True
Si token WA recu par bot ET valide -> compte cree + whatsapp_verifie=True
Si expire -> message d'expiration dans l'app + ressaisir les coordonnees pour recommencer
Apres validation -> supprimer la cle Redis du token

BLOCAGE SECURITE
Redis key : inscription_tentatives_{telephone}      TTL: 86400 secondes (24h)
Logique   : si tentatives >= 3 -> BlockageException
Message   : "Ce numero est bloque pendant {X}h {Y}min"
```

### 1.2 Flux connexion

```
ETAPE 1
Input  : pseudo OU email + password
Valide : credentials corrects + is_active = True

ETAPE 2 — Si CNI verifie
Si user.identite_verifiee = True :
  -> Page saisie numero_cni
  -> hash(numero_saisi) == user.numero_cni_hash -> OK
  -> Sinon -> erreur

ETAPE 3 — Session unique
Invalide tous les tokens JWT existants du user
Si last_login_device != device_actuel :
  -> Envoie notification email + WhatsApp
  -> Nouveau token genere
  -> Redirect page confirmation "C'est moi / Signaler"

ETAPE 4 — Tokens JWT
access_token  : expire 30 minutes
refresh_token : expire 7 jours
Stockage      : AsyncStorage (mobile) / localStorage (admin)
```

### 1.3 Refresh token

```
Si 401 sur une requete :
  1. Recupere refresh_token du storage
  2. POST /api/auth/token/refresh/ avec {refresh}
  3. Si 200 -> nouveau access_token stocke -> requete relancee
  4. Si 400/401 -> deconnexion forcee + redirect login
```

---

## 2. COTISATIONS

### 2.1 Creation

```
Validation :
- nom : requis, max 100 chars
- montant_unitaire : 200 <= montant <= 250000 FCFA
- nombre_participants : min 2
- nb_jours : 3, 7, 14, 21 ou 30
- numero_receveur : format +228XXXXXXXXX
- est_recurrente : bool
- prix_modifiable : bool (defaut False)

Calculs automatiques :
- date_expiration = datetime.now() + timedelta(days=nb_jours)
- slug = generer_slug_unique() -> KTZ-XXXXXXXXXXXX (12 chars)
- deep_link = f"kotizo.app/c/{slug}"

Verification limites utilisateur :
- Basique  : cotisations_creees_aujourd_hui < 3
             cotisations_creees_fenetre_7j  < 12
- Verifie  : cotisations_creees_aujourd_hui < 20
- Business : pas de limite
```

### 2.2 Rejoindre une cotisation

```
Validation :
- slug doit exister et statut = 'active'
- date_expiration > now()
- pas encore participe a cette cotisation
- nb_unites >= 1
- nb_unites x montant_unitaire <= 25000 FCFA

Si modification montant par unite (prix_modifiable=True) :
- montant_modifie doit etre >= montant_unitaire_base
- Sinon : erreur "Le montant doit etre superieur ou egal a {base} FCFA"
- Si prix_modifiable=False : champ modification desactive dans l'UI

Frais calcules :
- frais_kotizo   = montant_total x 0.005
- frais_paydunya = montant_total x 0.025 (payin)
- total_payeur   = montant_total x 1.05

Apres paiement confirme (webhook) :
- Participation.statut = 'paye'
- Cotisation.participants_payes += 1
- Cotisation.montant_collecte += montant_unitaire x nb_unites
- Si participants_payes == nombre_participants -> tache finaliser_cotisation
- Recu type 'participation' genere
```

### 2.3 Progression et completion

```
progression (%) = (participants_payes / nombre_participants) x 100

Si cotisation complete (100%) :
1. statut = 'complete'
2. Calcul montant net = montant_collecte - frais_kotizo_total
3. PayDunya payout vers numero_receveur
4. Recu type 'reversement_cotisation' genere pour le createur
5. Notification createur : "Felicitations ! Reversement en cours."
6. Notification tous participants : "La cotisation [nom] est complete"
```

### 2.4 Suppression et soft delete

```
Regles :
1. Cotisation active -> pas de suppression directe
2. Createur doit d'abord STOPPER la collecte
3. Apres STOP -> attendre 48 heures
4. Apres 48h -> option "Supprimer de l'historique"

Soft delete :
- cotisation.supprime = True
- cotisation.date_suppression = datetime.now()
- cotisation.supprime_par = user.id
- Invisible dans l'app
- Visible dans l'admin Kotizo

Modification :
- participants_payes = 0 -> modification possible (nom, description, montant)
- participants_payes >= 1 -> modification impossible
```

### 2.5 Reutilisation du code

```
Code cotisation valide pendant : duree_cotisation + 7 jours
Apres 7 jours post-expiration  : code disponible pour nouvelle cotisation
```

### 2.6 Rappels automatiques (Celery Beat)

```
Toutes les 6 heures, verifier :
- Cotisations expirant dans les 12 prochaines heures
- participants_manquants > 0

Actions :
- Email au createur + participants non payes
- WhatsApp si numero verifie
- Notification in-app
```

### 2.7 Commentaires sur cotisation

```
Conditions :
- Utilisateur a rejoint la cotisation (participation existante)
- date_adhesion + 60 jours > now()
- Sinon : "Commentaires fermes (plus de 2 mois)"

Flux :
- Commentaire envoye -> stocke en base -> alerte admin
- Admin repond depuis le panneau admin
- Reponse envoyee PAR WHATSAPP uniquement
- Notification double : in-app + WhatsApp
```

---

## 3. QUICK PAY — DEUX MODES

### 3.1 Mode 1 — Lien partageable

```
Input (par le createur) :
- montant : 200 <= montant <= 250000 FCFA
- note : optionnel

Calculs :
- montant_avec_frais = montant x 1.05
- frais_kotizo = montant x 0.005
- Code : QP-XXXXXXXX (8 chars)
- Expiration : 1 heure apres creation
- Lien : kotizo.app/qp/QP-XXXXXXXX

Flux paiement :
1. Payeur ouvre le lien
2. Saisit LUI-MEME son numero Mobile Money
3. Choisit son operateur (auto-detecte par prefixe)
4. Valide le paiement sur son telephone (PIN)
5. Webhook PayDunya confirme -> pay-in traite
6. Kotizo declenche payout vers createur
7. Recu type 'quickpay_payeur' pour le payeur
8. Recu type 'quickpay_receveur' pour le createur

Si expire (1h) :
- statut = 'expire'
- Notification au createur
- QuickPayExpireScreen dans l'app
```

### 3.2 Mode 2 — Paiement direct (boutique)

```
Input (par le createur) :
- montant : 200 <= montant <= 250000 FCFA
- numero_client : numero Mobile Money du client (+228XXXXXXXXX)
- note : optionnel

Flux paiement :
1. Systeme detecte l'operateur du client par prefixe
2. Appel API PayDunya SoftPay avec numero_client pre-rempli :
   POST https://app.paydunya.com/api/v1/softpay/{operateur}-togo
   Body : { phone_number, payment_token, customer_name }
3. Client recoit notification USSD/SMS sur son telephone
4. Client saisit son PIN pour valider
5. Timeout operateur : ~30 secondes
   - Si succes -> webhook confirme -> pay-in traite
   - Si timeout -> statut = 'expire' + notif createur
6. Kotizo declenche payout vers createur
7. Recus generes

Detection operateur par prefixe :
- 90,91,92,93,94,95,96,97 -> MOOV_TOGO
- 70,71,72,79             -> MIXX_TOGO
- 98,99                   -> TMONEY_TOGO
```

### 3.3 Frais (identiques pour les 2 modes)

```
pay_in  (preleve au payeur)  : 2.0% du montant
pay_out (debite a Kotizo)    : 2.5% du montant
gain_kotizo                  : 0.5% du montant
total_frais_payeur           : 5.0% du montant

montant_payeur   = montant x 1.05
montant_receveur = montant (net, sans frais)
frais_kotizo     = montant x 0.005
```

---

## 4. RECUS — 4 TYPES

### 4.1 Type participation (cotisation)

```
Champs :
- type         : 'participation'
- cotisation_nom
- createur_pseudo
- participation_id  : PART-XXXXXXXX
- rang_paiement     : Xeme participant
- nb_unites
- prix_unite
- sous_total
- frais_pct    : 5%
- frais_montant
- total_paye
- operateur
- date_heure
- reference_txn

Options UI : enregistrer image | telecharger PDF | partager | retour accueil
```

### 4.2 Type reversement_cotisation (createur)

```
Champs :
- type              : 'reversement_cotisation'
- cotisation_nom
- nb_participants
- montant_collecte
- frais_kotizo_deduits
- montant_net_recu
- numero_receveur   : masque (+228 XX** **** )
- operateur
- date_heure
- reference_payout

Options UI : enregistrer image | telecharger PDF | partager | retour accueil
```

### 4.3 Type quickpay_payeur

```
Champs :
- type             : 'quickpay_payeur'
- qp_code          : QP-XXXXXXXX
- receveur_pseudo
- note
- montant
- frais_pct        : 5%
- frais_montant
- total_paye
- operateur
- date_heure
- reference_txn

Options UI : enregistrer image | telecharger PDF | partager | retour accueil
```

### 4.4 Type quickpay_receveur (createur)

```
Champs :
- type             : 'quickpay_receveur'
- qp_code          : QP-XXXXXXXX
- payeur_numero    : masque (+228 XX** ****)
- note
- montant_brut
- frais_kotizo_deduits
- montant_net_recu
- operateur
- date_heure
- reference_payout

Options UI : enregistrer image | telecharger PDF | partager | retour accueil
```

---

## 5. PAIEMENTS ET TRANSACTIONS

### 5.1 Operateurs Mobile Money Togo

```
MOOV MONEY
- Prefixes : 90,91,92,93,94,95,96,97
- Canal PayDunya : MOOV_TOGO
- Endpoint SoftPay : /api/v1/softpay/moov-togo
- Couleur : #FF6600

MIXX BY YAS
- Prefixes : 70,71,72,79
- Canal PayDunya : MIXX_TOGO
- Endpoint SoftPay : /api/v1/softpay/mixx-togo
- Couleur : #003087

T-MONEY
- Prefixes : 98,99
- Canal PayDunya : TMONEY_TOGO
- Endpoint SoftPay : /api/v1/softpay/t-money-togo
- Couleur : #E31E24

Detection automatique :
- Extraire les 2 premiers chiffres apres +228
- Trouver l'operateur correspondant
- Pre-selectionner dans l'UI
```

### 5.2 Webhooks PayDunya

```
REGLE ABSOLUE : Toujours request.POST — JAMAIS json.loads(request.body)

Validation hash :
- hash_recu    = request.POST.get('data[hash]')
- hash_calcule = sha512(PAYDUNYA_MASTER_KEY).hexdigest()
- Si hash_recu != hash_calcule -> HTTP 400

Endpoints webhooks :
- POST /api/webhooks/paydunya/cotisation/
- POST /api/webhooks/paydunya/quickpay/
- POST /api/webhooks/paydunya/payout/

Statuts PayDunya :
- 'completed' -> traiter le paiement
- Autre -> ignorer (logged)
```

### 5.3 Gestion des remboursements

```
Si cotisation expiree avec participants partiels :
- Participations payees mais cotisation incomplete :
  -> Calcul : montant_paye - frais_kotizo
  -> PayDunya payout vers numero_payeur
  -> Transaction type='remboursement' creee

Demande manuelle :
- L'utilisateur soumet via l'app
- Passe par l'admin pour validation
- Traitement dans 24-72h
```

---

## 6. VERIFICATION D'IDENTITE

```
ETAPE 1 — Photo recto
ETAPE 2 — Photo verso
ETAPE 3 — Saisie numero carte -> hash SHA256 en base
ETAPE 4 — Soumission -> statut 'en_attente' -> alerte admin
ETAPE 5 — Decision admin
  Si APPROUVE :
  - user.niveau = 'verifie'
  - user.identite_verifiee = True
  - user.nom verrouille, user.prenom verrouille
  - Paiement 1000 FCFA (ou 500 si promo)
  - Notification email + WhatsApp + in-app
  Si REJETE :
  - Raison communiquee
  - Peut soumettre a nouveau
```

---

## 7. FENETRE GLISSANTE 7 JOURS

```
Principe :
- PAS de reset le lundi minuit
- Compte les cotisations creees dans les 7 derniers jours (168h exactes)
- Mis a jour par Celery Beat toutes les heures

Stockage :
- Compte en temps reel depuis la BDD
- Cache Redis pour les verifications frequentes
```

---

## 8. AGENT IA

### 8.1 Limites par niveau

```
Basique  : X messages/jour (configurable en settings)
Verifie  : 2X messages/jour
Business : Illimite

Stockage compteur :
- Redis uniquement — PAS en base de donnees
- Cle : ia_msgs_{user_id}_{date}
- TTL : 86400 secondes
- Reset : Celery Beat tous les jours a minuit
```

### 8.2 Synchronisation WhatsApp/App

```
- Conversation in-app = conversation WhatsApp (meme historique)
- Message in-app -> envoye aussi sur WhatsApp si numero verifie
- Message WhatsApp -> stocke et visible dans l'app
- Si limite in-app atteinte :
  -> Message : "Limite atteinte. Continuez sur WhatsApp."
  -> Lien direct vers WhatsApp avec message predefini
```

### 8.3 Anti-injection

```
7 couches de filtrage :
1. Longueur max du message
2. Mots-cles interdits
3. Patterns suspects (HTML, SQL, code...)
4. Caracteres speciaux en exces
5. Repetition anormale
6. Tentative de role override
7. Score de risque global

Si score > seuil -> message refuse + alerte admin
```

---

## 9. BOT WHATSAPP

```
Delai aleatoire : random.uniform(3, 6) secondes (jamais fixe)

Commandes utilisateur :
AIDE    -> Menu des commandes
SOLDE   -> Transactions du mois
COTISER -> Instructions cotisation
PAYER   -> Instructions Quick Pay
STAT    -> Resume statistiques
SUPPORT -> Creer un ticket
STOP    -> Desactiver notifications WA

Gestion panne :
- Ping toutes les 5 minutes (Celery Beat)
- Apres 3 pings echoues -> statut 'hors_service'
- Email alerte admin
- Notifications basculees vers email uniquement
- WhatsAppIndisponibleScreen dans l'app
```

---

## 10. ANTI-FRAUDE

```
Detection automatique (Celery toutes les 30 min) :
- creation_rapide    : >= 8 cotisations en 24h
- multi_comptes      : meme numero sur plusieurs comptes
- signalements_multi : >= 3 signalements recus
- numero_suspect     : numero dans liste noire
- fraude_paydunya    : anomalie webhook
- injection_ia       : tentative injection detectee

Niveaux de sanction :
0 -> Avertissement
1 -> Restriction legere (3j)
2 -> Restriction moyenne (7j)
3 -> Degradation niveau (30j)
4 -> Fermeture temporaire
5 -> Bannissement permanent
```

---

## 11. CELERY BEAT — TACHES PLANIFIEES

```
Toutes les 5 min  : Expirer Quick Pay expires
                  : Ping bot WhatsApp

Toutes les 30 min : Detection fraude automatique

Toutes les heures : Expirer cotisations
                  : Mettre a jour fenetre glissante 7j
                  : Supprimer comptes non verifies 48h

Toutes les 6h    : Envoyer rappels cotisations expirant dans 12h

Tous les jours
  a 20h          : Rapport journalier
  a minuit       : Reset compteurs email
                 : Reset compteurs messages IA

Timezone : Africa/Lome (GMT+0)
```

---

## 12. EMAILS MULTI-FOURNISSEURS

```
1. Gmail   : 500 emails/jour (prioritaire)
2. Brevo   : 300 emails/jour
3. Mailjet : 200 emails/jour
4. Resend  : 100 emails/jour
Total      : 1100 emails/jour

Logique :
- Compter les emails envoyes par fournisseur (Redis)
- Si fournisseur sature -> passer au suivant
- Reset compteur tous les jours a minuit (Celery Beat)
```

---

## 13. PARRAINAGE AMBASSADEUR

```
AMBASSADEUR VERIFIE GRATUIT
Condition A : 50 parrainages actifs
OU
Condition B : 25 filleuls ayant realise 3+ cotisations

AMBASSADEUR BUSINESS GRATUIT
Condition A : 100 parrainages actifs
OU
Condition B : 50 filleuls ayant realise 3+ transactions

Parrainage valide quand :
- Filleul s'inscrit avec le code parrainage
- Filleul effectue au moins 1 cotisation/paiement
```
