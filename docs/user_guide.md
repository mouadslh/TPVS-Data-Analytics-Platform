# Guide Utilisateur — TPVS Analytics Platform

## Connexion

1. Ouvrir https://localhost (ou http://localhost:3000 en direct)
2. Identifiants par défaut (données de démonstration) :
   - **Super Admin:** `admin` / `changeme123`
   - **Admin Opérationnel (zone Nord):** `op.nord` / `changeme123`
   - **Admin Finance:** `finance` / `changeme123`
   - **Admin Technique:** `tech` / `changeme123`

## Profils et accès

| Profil | Modules accessibles | Périmètre |
|--------|---------------------|-----------|
| Super Admin | Tous | Toutes zones |
| Admin Opérationnel | Dashboard, Missions, Agents (zone) | Sa zone uniquement |
| Admin Finance | Transactions, Rapports financiers | Données financières |
| Admin Technique | Machines, Motos, Stock | Équipements et logistique |

## Modules du tableau de bord

### 1. Dashboard Exécutif
Vue synthétique : CA du jour, transactions validées, agents actifs, machines opérationnelles, graphique CA 30 jours, top agents/stations.

### 2. Analyse Transactions
Filtres temporels, répartition par mode de paiement, heatmap horaire, comparaison N vs N-1, détection d'anomalies Z-score, tableau exportable.

### 3. Performance Agents
Classement par score composite, profil agent avec radar chart, tendances 3/6/12 mois.

### 4. Suivi Missions
KPI complétion, missions en cours/terminées/annulées, tableau détaillé.

### 5. Gestion Stock Cartes
Niveaux par type/station, alertes de seuil, taux de rotation et défectueux.

### 6. État Machines (TPVS)
Disponibilité flotte, alertes batterie <20%, CA par station.

### 7. Suivi Motos & GPS
Carte Leaflet temps réel, kilométrage, statut batterie.

### 8. Rapports & Exports
Génération à la demande (7 types), export PDF/Excel.

### 9. Détection d'Anomalies
6 règles automatiques avec niveau de sévérité.

## Préférences

- **Langue:** FR (défaut) / EN via le menu en-tête
- **Mode sombre:** Toggle dans l'en-tête (persisté localStorage)
- **Filtres:** Persistés en sessionStorage par module

## API Documentation

Swagger UI disponible à : `http://localhost:8000/api/docs/`
