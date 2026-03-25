# KOTIZO v4.2 — INTERFACES MOBILE COMPLETES

## Derniere mise a jour : Mars 2026
## Total : 68 ecrans

---

## DESIGN SYSTEM

### Themes (3 options — choix utilisateur)

```
VERT AFRIQUE (defaut)
- Background    : #0A1A0F
- Card          : #0D2B14
- CardSecondary : #1A3A1F
- Primary       : #16A34A
- Accent        : #22C55E

VIOLET PREMIUM
- Background    : #0E0A1F
- Card          : #1A1040
- CardSecondary : #251760
- Primary       : #7C3AED
- Accent        : #A78BFA

BLEU CLASSIC
- Background    : #0A0F1E
- Card          : #111827
- CardSecondary : #1E293B
- Primary       : #2563EB
- Accent        : #3B82F6

COMMUN (tous themes) :
- Border        : rgba(255,255,255,0.06)
- Success       : #22C55E
- Error         : #EF4444
- Warning       : #F59E0B
- TextPrimary   : #FFFFFF
- TextSecondary : rgba(255,255,255,0.6)
- TextTertiary  : rgba(255,255,255,0.3)
```

### Composants communs
```
KButton    : bouton principal + variante secondary
KInput     : champ texte avec label et erreur
KCard      : carte avec variante secondary
KBadge     : badge statut (success/info/warning/error)
KToast     : notification toast animee (remplace Alert natif)
KRecu      : composant recu parametrable (4 types)
```

### Regles UI
- Pas d'emoji nulle part (Ionicons uniquement)
- KToast remplace TOUS les Alert.alert natifs
- Navigation par swipe desactivee (gestureEnabled: false)
- SafeAreaView sur tous les ecrans
- Logo SVG adapte automatiquement au theme actif

---

## FLUX A — ONBOARDING (6 ecrans)

### A1 — SplashScreen
```
Route   : Splash
- Logo Kotizo anime (scale + fade, 2.5s) — couleur selon theme
- Nom "Kotizo" + slogan
- 3 dots en bas
- Lance init() du authStore + themeStore
- Si token valide -> navigate('Main')
- Sinon -> navigate('Tutorial')
```

### A2/A3/A4 — TutorialScreen (3 slides)
```
Route   : Tutorial
- Slide 1 : "Cotisez ensemble"
- Slide 2 : "Partagez facilement"
- Slide 3 : "Quick Pay instantane"
- Bouton "Commencer" -> CGU
```

### A5 — CGUScreen
```
Route   : CGU
- Texte CGU scrollable
- Case "J'accepte les conditions" (requis)
- Case "Consentement position GPS" (optionnel)
- Bouton "Continuer" (disabled si CGU non cochees)
```

### A6 — OnboardingContextuelScreen
```
Route   : OnboardingContextuel
- 3 slides animes post-inscription
- Boutons : Creer ma premiere cotisation / Rejoindre
```

---

## FLUX B — AUTHENTIFICATION (6 ecrans)

### B1 — ConnexionScreen
```
Route   : Connexion
- Pseudo ou Email
- Mot de passe
- Lien "Mot de passe oublie ?"
- Vers : Inscription | MotDePasseOublie
- Apres succes : Main (Dashboard)
```

### B2 — InscriptionScreen
```
Route   : Inscription
Etape 1 — Coordonnees :
- Prenom *, Nom *
- Pseudo unique * (max 20 chars)
- Email *
- Numero WhatsApp * (+228XXXXXXXXX)
- Mot de passe * (min 8 chars, indicateur force)
- Confirmer mot de passe *

Etape 2 — Canal :
- Bouton "Verifier par Email"
- Bouton "Verifier par WhatsApp"
```

### B3 — VerificationScreen
```
Route   : Verification
Canal email :
- 6 champs OTP individuels
- Compte a rebours 2 minutes
- Si expire -> KToast erreur + option ressaisir coordonnees

Canal WhatsApp :
- Affichage message predefini a envoyer
- Bouton ouverture WhatsApp avec lien predefini
- Attente confirmation automatique (polling 3s)
- Indicateur "En attente de confirmation..."
- Si expire -> l'app affiche "Temps expire" (pas le bot)
```

### B4 — MotDePasseOublieScreen
```
Route   : MotDePasseOublie
- Saisie email -> envoi lien reset
```

### B5 — CompteAttenteScreen
```
Route   : CompteAttente
- Icone email pulse animee
- Compte a rebours 48h
- Bouton "Renvoyer l'email"
```

### B6 — EtatZeroScreen
```
Route   : EtatZero
- Message bienvenue avec prenom
- 3 slides rotatifs
- CTA : Creer / Rejoindre
```

---

## FLUX C — DASHBOARD ET COTISATIONS (13 ecrans)

### C1 — DashboardScreen
```
Route   : Accueil (tab)
Header :
  - "Bonjour, @pseudo"
  - Badge niveau
  - Icone chat -> AgentIA
  - Icone cloche -> Notifications

Carte financiere mensuelle :
  - Envoye ce mois : X FCFA
  - Recu ce mois   : X FCFA

Actions rapides : [Creer] [Rejoindre] [Quick Pay] [Historique]
Cotisations actives : liste 3 premieres
Resume du mois : Cotisations | Participations | Parrainages
Refresh : pull-to-refresh
```

### C2 — CotisationsScreen
```
Route   : Cotisations (tab)
- Tabs : [Creees] [Participations]
- Bouton + -> CreerCotisation
- Clic item -> DetailCotisation
```

### C3 — CreerCotisationScreen
```
Route   : CreerCotisation
Champs :
- Nom *
- Description (optionnel)
- Montant unitaire * (200-250000 FCFA)
- Nombre de participants * (min 2)
- Duree : [3j][7j][14j][21j][30j]
- Numero receveur Mobile Money *
- Cotisation recurrente ? (toggle) -> ConfigRecurrenceScreen
- Prix modifiable par les participants ? (toggle, defaut OFF)

Apercu frais en temps reel
Bouton "Continuer" -> ApercuCotisationScreen
```

### C4 — ApercuCotisationScreen
```
Route   : ApercuCotisation
- Affichage OBLIGATOIRE avant creation
- Toutes les coordonnees + detail frais + total
- Boutons : [Modifier] [Confirmer et creer]
```

### C5 — CotisationCreeeScreen
```
Route   : CotisationCreee
- Animation succes
- Code KTZ-XXXXXXXXXXXX avec copie
- Deep link
- Options : [Partager] [Voir la cotisation] [Accueil]
```

### C6 — DetailCotisationScreen
```
Route   : DetailCotisation (params: slug)
Createur voit :
- Progression graphique
- Liste participants (nom/pseudo/rang/heure/montant)
- Menu 3 points -> Envoyer rappel | Stopper | Supprimer
- Bouton "Cotiser a nouveau"

Participant voit :
- Coordonnees cotisation
- Son recu de participation
- Bouton "Cotiser a nouveau"
```

### C7 — RejoindreScreen
```
Route   : Rejoindre
- Zone saisie code/lien
- Support deep link (pre-rempli automatiquement)
- Affiche coordonnees cotisation
- Champ nombre d'unites
- Champ modification montant (si prix_modifiable=True seulement)
- Calcul total en temps reel
- Bouton "Rejoindre" -> ChoixOperateurScreen
```

### C8 — ChoixOperateurScreen
```
Route   : ChoixOperateur
- Detection auto operateur
- 3 operateurs avec logos : moov_money.png | mixx_by_yas.png | tmoney_logo.png
- Resume montant en haut
- Bouton "Payer X FCFA"
```

### C9 — ConfirmationPaiementScreen
```
Route   : ConfirmationPaiement
- Polling statut toutes les 5s (max 12 fois)
- Statuts : en_attente | complete | echoue
- Apres complete -> RecuScreen (type: 'participation')
```

### C10 — RecuScreen
```
Route   : Recu (params: type, data)

Types supportes :
- participation          -> recu participation cotisation
- reversement_cotisation -> recu reversement createur
- quickpay_payeur        -> recu Quick Pay cote payeur
- quickpay_receveur      -> recu Quick Pay cote receveur

Format ticket avec perforations decoratives
Montant en grand au centre
Details selon le type (voir LOGIQUE_METIER section 4)
Options : [Enregistrer image] [Telecharger PDF] [Partager] [Accueil]
```

### C11 — RappelConfirmationScreen
```
Route   : RappelConfirmation
- Info cotisation + heures restantes
- Bouton "Voir la cotisation"
```

### C12 — RappelEnvoyeScreen
```
Route   : RappelEnvoye
- Confirmation envoi rappels
- Nombre de participants notifies
```

### C13 — ConfigRecurrenceScreen
```
Route   : ConfigRecurrence
- Frequence : Hebdomadaire / Mensuel / Trimestriel
- Nombre de cycles : 3, 6, 12, 24
```

---

## FLUX D — QUICK PAY (7 ecrans)

### D1 — QuickPayScreen
```
Route   : QuickPay (tab)
- Tabs : [Envoyes] [Recus]
- Bouton + -> CreerQuickPay
```

### D2 — CreerQuickPayScreen
```
Route   : CreerQuickPay

Toggle MODE en haut :
  [Lien partageable]  [Paiement direct]

Mode Lien partageable :
- Montant * (200-250000 FCFA)
- Note (optionnel)
- Apercu : "Vous recevrez X FCFA / Le payeur versera X FCFA"
- Expiration : 1 heure
- Bouton "Generer le lien"
- Apres generation : code QP + lien + countdown 1h
- Boutons : [Partager] [Voir mes QP]

Mode Paiement direct :
- Montant * (200-250000 FCFA)
- Numero Mobile Money du client * (+228XXXXXXXXX)
- Note (optionnel)
- Detection auto operateur par prefixe
- Apercu frais
- Bouton "Envoyer la demande"
- Apres envoi -> QuickPayDirectScreen
```

### D3 — QuickPayDirectScreen (NOUVEAU v4.2)
```
Route   : QuickPayDirect
- Icone operateur detecte
- Montant + infos
- Message : "Demande envoyee sur le telephone du client"
- Spinner + "En attente de validation..."
- Countdown 30 secondes
- Polling statut toutes les 3s
- Si succes -> RecuScreen (type: 'quickpay_receveur')
- Si timeout -> KToast "Le client n'a pas valide a temps"
               + Bouton "Renvoyer la demande"
```

### D4 — DetailQuickPayScreen
```
Route   : DetailQuickPay (params: quickpay_id)
- Coordonnees QP
- Statut avec badge
- Lien de paiement si actif
- Mode affiche (Lien / Direct)
```

### D5 — QuickPayExpireScreen
```
Route   : QuickPayExpire
- Icone flash rouge
- Code + montant expire
- Boutons : [Creer nouveau] [Accueil]
```

### D6 — ConfirmationReceptionScreen
```
Route   : ConfirmationReception
- Animation checkmark vert
- "Reversement en cours" avec montant net
- Info : delai max 5 minutes
```

### D7 — HistoriqueQPScreen
```
Inclus dans HistoriqueScreen (E1)
Tabs : QP Envoyes / QP Recus
Mode affiche sur chaque item (Lien / Direct)
```

---

## FLUX E — HISTORIQUE (5 ecrans)

### E1 — HistoriqueScreen
```
Route   : Historique
- 4 tabs : Tout | Cotisations | Quick Pay | Participants
- Filtre par statut et date
```

### E2 — HistoriqueCotCreesScreen
```
Route   : HistoriqueCotCrees
- Filtres : [Tous] [active] [complete] [expiree]
```

### E3 — HistoriqueCotPartScreen
```
Route   : HistoriqueCotPart
- Cotisations rejointes avec statut
```

### E4 — HistoriqueQPEnvoyesScreen
```
Route   : HistoriqueQPEnvoyes
- QP crees par moi
- Badge mode : Lien | Direct
```

### E5 — HistoriqueQPRecusScreen
```
Route   : HistoriqueQPRecus
- QP ou j'ai paye
- Badge "Recu" vert
```

---

## FLUX F — PROFIL (15 ecrans)

### F1 — ProfilScreen
```
Route   : Profil (tab)
- Avatar, pseudo, niveau, badge
Menu :
- Modifier profil
- Verification identite
- Parrainage
- Statistiques
- Notifications
- Agent IA
- Parametres
- Deconnexion
- Toggle theme en bas (3 cercles : vert | violet | bleu)
```

### F2 — ModifierProfilScreen
```
Route   : ModifierProfil
- Pseudo, Numero Mobile Money, Numero WhatsApp
- Non modifiables : Email, Nom/Prenom (apres verif)
```

### F3/F4 — VerificationRectoScreen / VerificationVersoScreen
```
Routes : VerificationRecto / VerificationVerso
- Capture photo (camera ou galerie)
- Preview + conseils qualite
```

### F5 — LivenessCheck -> REPORTE v2

### F6 — AttenteValidationScreen
```
Route : AttenteValidation
- Icone pulsante
- 4 etapes avec progression
- Info notification WA + email
```

### F7 — VerificationApprouveeScreen
```
Route : VerificationApprouvee
- Checkmark vert anime
- Badge "Verifie" + avantages
```

### F8/F9/F10 — Business
```
DemandeBusinessScreen
DemandeBusinessAttenteScreen
BusinessApprouveScreen
```

### F11 — NotificationsScreen
```
Route : NotificationsScreen
- Groupement par date
- Icones colorees par type
- Suppression soft delete
```

### F12a — ParametresScreen
```
Route : Parametres
Sections :
- Compte
- Notifications (toggles push/WA/email/rappels)
- Apparence -> 3 themes (vert | violet | bleu) avec preview logo
- Securite -> ParametresSecurite
- Informations
- Deconnexion (rouge)
```

### F12b — ParametresSecuriteScreen
```
Route : ParametresSecurite
- Changer mot de passe
- Sessions actives
- Supprimer le compte
```

### F13 — ParrainageScreen
```
Route : Parrainage
- Code parrainage + partager
- Stats + barres progression ambassadeur
```

### F14 — SessionsActivesScreen
```
Route : SessionsActives
- Liste appareils + badge "Actuel"
- Bouton "Revoquer"
```

### F15 — ReconfirmationActionScreen
```
Route : ReconfirmationAction
- Saisie mot de passe pour action sensible
```

---

## FLUX G — ETATS SPECIAUX (7 ecrans)

```
G1 : HorsLigneScreen
G2 : ErreurReseauScreen
G3 : LienExpireScreen (type: cotisation|quickpay|verification)
G4 : CotisationNonTrouveeScreen
G5 : MaintenanceScreen
G6 : WhatsAppIndisponibleScreen
G7 : QuickPayExpireScreen
```

---

## FLUX H — AGENT IA (3 ecrans)

```
H1 : AgentIAScreen
     - Interface chat, 100 derniers messages
     - Compteur messages du jour
     - Suggestions questions pre-definies
     - Anti-injection frontend

H2 : MicroDicteeScreen
     - 7 barres animees + bouton micro
     - Countdown 60s max

H3 : ReclamationScreen
     - 5 types de problemes
     - Jusqu'a 3 captures d'ecran
```

---

## FLUX S — STATISTIQUES (5 ecrans)

```
S1 : StatsGlobaleScreen   -> Grid 4 modules
S2 : StatsFinancieresScreen -> Filtre 7j/30j/90j/Tout
S3 : StatsCotisationsScreen -> Compteurs + limites compte
S4 : StatsAmbassadeurScreen -> Barres progression
S5 : StatsQuickPayScreen    -> Grid 4 + volumes
```

---

## FLUX I — POST-INSCRIPTION (2 ecrans)

```
I1 : OnboardingContextuelScreen
I2 : EtatZeroScreen
```

---

## NAVIGATION

### AppNavigator.js
```
Non authentifie : Splash, Tutorial, CGU, Connexion,
                  Inscription, Verification, MotDePasseOublie,
                  CompteAttente, OnboardingContextuel

Authentifie : Main (BottomTabs) + tous ecrans app
```

### MainNavigator.js (Bottom Tabs)
```
4 onglets avec Ionicons :
- Accueil     (home/home-outline)
- Cotisations (wallet/wallet-outline)
- Quick Pay   (flash/flash-outline)
- Profil      (person/person-outline)

Height : 70px | PaddingBottom : 10px
BackgroundColor : colors.card (selon theme actif)
```

---

## ASSETS

```
assets/
├── icon.png
├── splash-icon.png
├── adaptive-icon.png
├── favicon.png
└── logos/
    ├── kotizo_logo.svg        (adaptatif — couleur via theme)
    ├── kotizo_logo_vert.png
    ├── kotizo_logo_violet.png
    ├── kotizo_logo_bleu.png
    ├── moov_money.png
    ├── mixx_by_yas.png
    └── tmoney_logo.png
```

---

## RECAPITULATIF ECRANS

| Flux | Nombre |
|------|--------|
| A — Onboarding | 6 |
| B — Auth | 6 |
| C — Cotisations | 13 |
| D — Quick Pay | 7 (+1 v4.2) |
| E — Historique | 5 |
| F — Profil | 15 |
| G — Etats speciaux | 7 |
| H — Agent IA | 3 |
| S — Statistiques | 5 |
| I — Post-inscription | 2 |
| **TOTAL** | **68** |
