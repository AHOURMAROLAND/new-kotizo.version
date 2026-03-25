# KOTIZO v4.2 — SUIVI D'AVANCEMENT

## Derniere mise a jour : Mars 2026
## Statut global : 0/100 (NOUVEAU REPO — REPART DE ZERO)
## Repo : https://github.com/AHOURMAROLAND/kotizo-v4.2.git
## Repertoire local : E:\kotizo-v4.2

---

## NOUVEAUTES v4.2 PAR RAPPORT A v4.1

| Element | v4.1 | v4.2 |
|---------|------|------|
| Quick Pay modes | 1 mode | 2 modes (Lien + Direct) |
| Recus | 1 generique | 4 types parametres |
| Token inscription | 5 min | 2 min |
| Themes | 1 (bleu fixe) | 3 au choix (vert/violet/bleu) |
| Admin pages | 12 | 14 (+Statistics +Staff) |
| Mobile ecrans | 67 | 68 (+QuickPayDirectScreen) |
| Gestion staff | Roles fixes | Permissions granulaires par section |
| Logo | Fixe | Adaptatif selon theme |
| Prix modifiable cotisation | Non documente | Case a cocher explicite |

---

## AVANCEMENT PAR MODULE

| Module | Avancement | Statut |
|--------|-----------|--------|
| Fichiers contexte v4.2 | 100% | COMPLET |
| Setup projet (structure dossiers) | 0% | A FAIRE |
| Models Django | 0% | A FAIRE |
| Core (logger, utils, middleware) | 0% | A FAIRE |
| Auth JWT + double canal | 0% | A FAIRE |
| API Cotisations | 0% | A FAIRE |
| API Paiements | 0% | A FAIRE |
| API Quick Pay (2 modes) | 0% | A FAIRE |
| API Notifications | 0% | A FAIRE |
| Webhook PayDunya | 0% | A FAIRE |
| Agent IA Gemini | 0% | A FAIRE |
| Admin Panel API | 0% | A FAIRE |
| Admin Staff + Permissions | 0% | A FAIRE |
| Bot WhatsApp | 0% | A FAIRE |
| Celery Beat | 0% | A FAIRE |
| Anti-fraude | 0% | A FAIRE |
| Mobile 68 ecrans | 0% | A FAIRE |
| Admin Web 14 pages | 0% | A FAIRE |
| Tests unitaires | 0% | A FAIRE |
| Migration PostgreSQL | 0% | A FAIRE |
| Deploiement | 0% | A FAIRE |

---

## MOBILE — 68 ECRANS A IMPLEMENTER

### Flux A — Onboarding (6)
- [ ] SplashScreen (logo adaptatif theme)
- [ ] TutorialScreen slide 1
- [ ] TutorialScreen slide 2
- [ ] TutorialScreen slide 3
- [ ] CGUScreen
- [ ] OnboardingContextuelScreen

### Flux B — Auth (6)
- [ ] ConnexionScreen
- [ ] InscriptionScreen
- [ ] VerificationScreen (double canal, token 2min)
- [ ] MotDePasseOublieScreen
- [ ] CompteAttenteScreen
- [ ] ReinitialisationMotDePasseScreen

### Flux C — Cotisations (13)
- [ ] DashboardScreen
- [ ] CotisationsScreen
- [ ] CreerCotisationScreen (avec toggle prix_modifiable)
- [ ] ApercuCotisationScreen
- [ ] CotisationCreeeScreen
- [ ] DetailCotisationScreen
- [ ] RejoindreScreen
- [ ] ChoixOperateurScreen
- [ ] ConfirmationPaiementScreen
- [ ] RecuScreen (4 types)
- [ ] RappelConfirmationScreen
- [ ] RappelEnvoyeScreen
- [ ] ConfigRecurrenceScreen

### Flux D — Quick Pay (7)
- [ ] QuickPayScreen
- [ ] CreerQuickPayScreen (toggle Lien/Direct)
- [ ] QuickPayDirectScreen (NOUVEAU v4.2)
- [ ] DetailQuickPayScreen
- [ ] QuickPayExpireScreen
- [ ] ConfirmationReceptionScreen
- [ ] HistoriqueQPScreen

### Flux E — Historique (5)
- [ ] HistoriqueScreen
- [ ] HistoriqueCotCreesScreen
- [ ] HistoriqueCotPartScreen
- [ ] HistoriqueQPEnvoyesScreen
- [ ] HistoriqueQPRecusScreen

### Flux F — Profil (15)
- [ ] ProfilScreen (toggle theme 3 cercles)
- [ ] ModifierProfilScreen
- [ ] VerificationRectoScreen
- [ ] VerificationVersoScreen
- [ ] LivenessCheckScreen (REPORTE v2)
- [ ] AttenteValidationScreen
- [ ] VerificationApprouveeScreen
- [ ] DemandeBusinessScreen
- [ ] DemandeBusinessAttenteScreen
- [ ] BusinessApprouveScreen
- [ ] NotificationsScreen
- [ ] ParametresScreen (section Apparence avec 3 themes)
- [ ] ParametresSecuriteScreen
- [ ] ParrainageScreen
- [ ] SessionsActivesScreen
- [ ] ReconfirmationActionScreen

### Flux G — Etats speciaux (7)
- [ ] HorsLigneScreen
- [ ] ErreurReseauScreen
- [ ] LienExpireScreen
- [ ] CotisationNonTrouveeScreen
- [ ] MaintenanceScreen
- [ ] WhatsAppIndisponibleScreen
- [ ] QuickPayExpireScreen

### Flux H — Agent IA (3)
- [ ] AgentIAScreen
- [ ] MicroDicteeScreen
- [ ] ReclamationScreen

### Flux S — Statistiques (5)
- [ ] StatsGlobaleScreen
- [ ] StatsFinancieresScreen
- [ ] StatsCotisationsScreen
- [ ] StatsAmbassadeurScreen
- [ ] StatsQuickPayScreen

### Flux I — Post-inscription (2)
- [ ] OnboardingContextuelScreen
- [ ] EtatZeroScreen

---

## ADMIN WEB — 14 PAGES A IMPLEMENTER

| Page | Route | Statut |
|------|-------|--------|
| Login | /login | A faire |
| Dashboard (ameliore) | / | A faire |
| Utilisateurs | /users | A faire |
| Verifications CNI | /verifications | A faire |
| Transactions | /transactions | A faire |
| Remboursements | /remboursements | A faire |
| Alertes fraude | /alertes | A faire |
| Sanctions | /sanctions | A faire |
| Tickets | /tickets | A faire |
| Notifications | /notifications | A faire |
| WhatsApp | /whatsapp | A faire |
| Statistics | /statistics | A faire (NOUVEAU) |
| Staff | /staff | A faire (NOUVEAU) |
| Configuration | /configuration | A faire |

---

## ORDRE DE DEVELOPPEMENT RECOMMANDE

### Phase 1 — Backend fondations
```
Etape 1  : Setup projet Django + structure dossiers + .env + Docker
Etape 2  : Models (User, Cotisation, Participation, Transaction, QuickPay, Notification)
Etape 3  : Core (logger, utils, middleware, permissions)
Etape 4  : Auth (inscription double canal 2min, connexion, JWT, session unique)
Etape 5  : API Cotisations completes
Etape 6  : API Paiements + Webhooks PayDunya
Etape 7  : API Quick Pay (Mode Lien + Mode Direct)
Etape 8  : API Notifications
Etape 9  : Celery Beat (toutes les taches planifiees)
Etape 10 : Bot WhatsApp Evolution API
Etape 11 : Agent IA Gemini
Etape 12 : Anti-fraude
Etape 13 : Admin Panel API (+ Staff + Statistics)
```

### Phase 2 — Mobile (apres DIM valide)
```
Etape 14 : Setup Expo + navigation + themeStore + Zustand
Etape 15 : Flux A + B (Onboarding + Auth)
Etape 16 : Flux C (Dashboard + Cotisations)
Etape 17 : Flux D (Quick Pay 2 modes)
Etape 18 : RecuScreen 4 types
Etape 19 : Flux E + F (Historique + Profil + Themes)
Etape 20 : Flux G + H + S + I (Etats speciaux + IA + Stats)
```

### Phase 3 — Admin Web
```
Etape 21 : Setup React + Vite + Tailwind + Zustand
Etape 22 : Login + Sidebar avec permissions
Etape 23 : Dashboard ameliore (toutes nouvelles sections)
Etape 24 : Pages CRUD (Users, Verifications, Transactions...)
Etape 25 : Page Statistics (5 onglets + Recharts)
Etape 26 : Page Staff (gestion permissions granulaires)
```

### Phase 4 — Production
```
Etape 27 : Tests + corrections
Etape 28 : Migration PostgreSQL
Etape 29 : Deploiement Railway/Render + Nginx
Etape 30 : Monitoring Sentry + page statut
```

---

## CONVENTIONS DE DEVELOPPEMENT

```
- Commandes : PowerShell Windows 11 uniquement
- Fichiers  : toujours complets (jamais de diffs partiels)
- Node deps : une commande chainee par etape
- Git       : commit + push apres chaque etape
- Pas d'emoji dans le code ni l'UI
- KToast remplace tous les Alert.alert
- JAMAIS json.loads pour les webhooks PayDunya
- TOUJOURS random.uniform(3,6) pour le bot WhatsApp
- DIM valide AVANT tout code mobile
```

---

## REPO ET CHEMINS

```
Repo GitHub : https://github.com/AHOURMAROLAND/kotizo-v4.2.git
Local       : E:\kotizo-v4.2\
Backend     : E:\kotizo-v4.2\kotizo-backend\
Mobile      : E:\kotizo-v4.2\kotizo-mobile\
Admin       : E:\kotizo-v4.2\kotizo-admin\
```
