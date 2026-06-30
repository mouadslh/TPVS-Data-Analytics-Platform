import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  fr: {
    translation: {
      app_title: 'TPVS Analytics',
      login: 'Connexion',
      logout: 'Déconnexion',
      username: "Nom d'utilisateur",
      password: 'Mot de passe',
      dashboard: 'Tableau de bord',
      transactions: 'Transactions',
      agents: 'Performance Agents',
      missions: 'Suivi Missions',
      stock: 'Gestion Stock',
      machines: 'État Machines',
      motos: 'Suivi Motos & GPS',
      reports: 'Rapports & Exports',
      anomalies: "Détection d'Anomalies",
      dark_mode: 'Mode sombre',
      loading: 'Chargement...',
      ca_jour: 'CA du jour',
      tx_validees: 'Transactions validées',
      agents_actifs: 'Agents actifs',
      machines_op: 'Machines opérationnelles',
      generate_report: 'Générer un rapport',
      export: 'Exporter',
      severity: 'Sévérité',
      rule: 'Règle',
      message: 'Message',
    },
  },
  en: {
    translation: {
      app_title: 'TPVS Analytics',
      login: 'Login',
      logout: 'Logout',
      username: 'Username',
      password: 'Password',
      dashboard: 'Executive Dashboard',
      transactions: 'Transactions',
      agents: 'Agent Performance',
      missions: 'Mission Tracking',
      stock: 'Card Stock',
      machines: 'TPVS Machines',
      motos: 'Moto & GPS Tracking',
      reports: 'Reports & Exports',
      anomalies: 'Anomaly Detection',
      dark_mode: 'Dark mode',
      loading: 'Loading...',
      ca_jour: 'Daily revenue',
      tx_validees: 'Validated transactions',
      agents_actifs: 'Active agents',
      machines_op: 'Operational machines',
      generate_report: 'Generate report',
      export: 'Export',
      severity: 'Severity',
      rule: 'Rule',
      message: 'Message',
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem('tpvs_lang') || 'fr',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;
