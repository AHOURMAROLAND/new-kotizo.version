const DEV_URL = 'http://192.168.1.100:8000';
const PROD_URL = 'https://api.kotizo.app';

export const API_BASE_URL = __DEV__ ? DEV_URL : PROD_URL;

export const ENDPOINTS = {
  auth: {
    inscription: '/api/auth/inscription/',
    connexion: '/api/auth/connexion/',
    deconnexion: '/api/auth/deconnexion/',
    refresh: '/api/auth/token/refresh/',
    verificationEmail: '/api/auth/verification-email/',
    motDePasseOublie: '/api/auth/mot-de-passe-oublie/',
    changerMotDePasse: '/api/auth/changer-mot-de-passe/',
  },
  users: {
    moi: '/api/users/moi/',
    stats: '/api/users/moi/stats/',
    sessions: '/api/users/sessions/',
    verification: '/api/users/verification/soumettre/',
    statutVerification: '/api/users/verification/statut/',
    parrainage: '/api/users/parrainage/stats/',
    appliquerParrainage: '/api/users/parrainage/appliquer/',
    demandeBusiness: '/api/users/demande-business/',
  },
  cotisations: {
    liste: '/api/cotisations/',
    detail: (slug) => `/api/cotisations/${slug}/`,
    rejoindre: (slug) => `/api/cotisations/${slug}/rejoindre/`,
    stopper: (slug) => `/api/cotisations/${slug}/stopper/`,
    supprimer: (slug) => `/api/cotisations/${slug}/supprimer/`,
    modifier: (slug) => `/api/cotisations/${slug}/modifier/`,
    commentaire: (slug) => `/api/cotisations/${slug}/commentaire/`,
    rappel: (slug) => `/api/cotisations/${slug}/rappel/`,
    participations: '/api/cotisations/mes-participations/',
  },
  paiements: {
    historique: '/api/paiements/historique/',
    payer: (id) => `/api/paiements/payer/${id}/`,
    statut: (id) => `/api/paiements/statut/${id}/`,
    remboursement: '/api/paiements/remboursement/',
  },
  quickpay: {
    liste: '/api/quickpay/',
    recus: '/api/quickpay/recus/',
    stats: '/api/quickpay/stats/',
    parCode: (code) => `/api/quickpay/code/${code}/`,
    payer: (code) => `/api/quickpay/payer/${code}/`,
    detail: (id) => `/api/quickpay/${id}/`,
  },
  notifications: {
    liste: '/api/notifications/',
    nonLues: '/api/notifications/non-lues/',
    toutLire: '/api/notifications/tout-lire/',
    lire: (id) => `/api/notifications/${id}/lire/`,
    supprimer: (id) => `/api/notifications/${id}/`,
  },
  ia: {
    historique: '/api/agent-ia/historique/',
    message: '/api/agent-ia/message/',
  },
};
