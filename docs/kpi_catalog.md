# TPVS Analytics — KPI Catalog

| KPI | Formula | Source Tables | Refresh |
|-----|---------|---------------|---------|
| CA total | `SUM(montant) WHERE statut_validation='VALIDEE'` | `transaction`, `fact_transactions` | Hourly (ETL) / 60s (API cache) |
| CA par agent | `SUM(montant) GROUP BY agent_id` | `transaction`, `fact_transactions` | Hourly |
| CA par station | `SUM(montant) GROUP BY station_id` | `transaction` | Hourly |
| CA par zone | `SUM(montant) GROUP BY agent.zone_affectation` | `transaction` + `utilisateur` | Hourly |
| CA par machine | `SUM(montant) GROUP BY machine_id` | `transaction` | Hourly |
| Ticket moyen | `CA total / COUNT(validated)` | `transaction` | Real-time API |
| Volume transactions | `COUNT(*)` | `transaction` | Real-time API |
| Taux validation | `COUNT(VALIDEE) / COUNT(*)` | `transaction` | Real-time API |
| Taux rejet | `COUNT(REJETEE) / COUNT(*)` | `transaction` | Real-time API |
| Transactions en attente | `COUNT(*) WHERE statut_validation='EN_ATTENTE'` | `transaction` | Real-time API |
| Répartition paiement | `COUNT(*) GROUP BY type_paiement` | `transaction` | Real-time API |
| Taux complétion missions | `COUNT(TERMINEE) / COUNT(*)` | `mission`, `fact_missions` | 30 min (ETL) |
| Durée moyenne mission | `AVG(date_fin - date_debut)` minutes | `mission` | 30 min |
| Missions par agent | `COUNT(*) GROUP BY agent_id, period` | `mission` | 30 min |
| Score performance composite | `CA×0.5 + volume×0.3 + taux_completion×100×0.2` | `transaction`, `mission` | Daily 00:00 |
| Taux activité agents | `agents_with_tx / agents_actifs` | `transaction`, `utilisateur` | Daily |
| Missions annulées | `COUNT(ANNULEE) / COUNT(*)` | `mission` | 30 min |
| Couverture géographique | `DISTINCT zone_couverture` | `mission` | 30 min |
| Niveau stock | `quantite_actuelle` per type/station | `stock_carte`, `fact_stock` | 2×/day |
| Taux rotation stock | `(initiale - actuelle) / initiale` | `stock_carte` | 2×/day |
| Taux défectueux | `taux_defectueux` | `stock_carte` | 2×/day |
| Alertes seuil | `quantite_actuelle < seuil_alerte` | `stock_carte` | 2×/day |
| Prévision rupture | Linear regression on daily consumption | `fact_stock` | 2×/day |
| Taux disponibilité machines | `COUNT(DISPONIBLE) / COUNT(*)` | `machine` | Real-time API |
| MTTR | `AVG(repair_duration)` from maintenance events | `machine` (derived) | Daily |
| Batterie moyenne | `AVG(batterie)` | `machine` | Real-time API |
| CA par machine | `SUM(montant) GROUP BY machine_id` | `transaction` | Hourly |
| Kilométrage total motos | `SUM(kilometrage)` | `moto`, `fact_motos` | 15 min |
| Positions GPS temps réel | Latest `latitude, longitude, timestamp` | `moto` | 15 min |
| Prévision maintenance moto | Threshold on `kilometrage` (>12000 km) | `moto` | 15 min |
| Comparaison N vs N-1 | `(CA_mois_N - CA_mois_N1) / CA_mois_N1 × 100` | `fact_transactions` | Real-time API |
| Heatmap horaire | `COUNT(*) GROUP BY EXTRACT(HOUR FROM timestamp)` | `transaction` | Real-time API |
| Saisonnalité | `CA GROUP BY mois` over 12 months | `fact_transactions` + `dim_date` | Hourly ETL |

## Anomaly Rules

| Rule | Condition | Severity |
|------|-----------|----------|
| TRANSACTION_3SIGMA | `|z-score(montant)| > 3` | HIGH |
| ZERO_TX_COMPLETED_MISSION | Mission TERMINEE with 0 transactions | MEDIUM |
| MACHINE_HIGH_REJECTION | Rejection rate > 20% (min 10 tx) | HIGH |
| STOCK_BELOW_THRESHOLD | `quantite < seuil_alerte` | MEDIUM |
| MISSION_OVERRUN | Actual duration > 150% planned | MEDIUM |
| SYNC_STALE | `statut_sync != SYNC` and age > 2h | HIGH |
