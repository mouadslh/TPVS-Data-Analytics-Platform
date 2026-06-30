# TPVS Data Warehouse — Data Dictionary

## Schema: `dwh`

### dim_date

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| date_id | SERIAL | PK | Surrogate key |
| date | DATE | NOT NULL, UNIQUE | Calendar date |
| jour | SMALLINT | NOT NULL | Day of month (1-31) |
| semaine | SMALLINT | NOT NULL | ISO week number |
| mois | SMALLINT | NOT NULL | Month (1-12) |
| trimestre | SMALLINT | NOT NULL | Quarter (1-4) |
| annee | SMALLINT | NOT NULL | Year |
| jour_semaine | SMALLINT | NOT NULL | ISO weekday (1=Mon) |
| est_ferie | BOOLEAN | NOT NULL, DEFAULT false | French public holiday flag |

### dim_agent

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| agent_id | UUID | PK | Agent identifier (from OLTP) |
| matricule | VARCHAR(32) | NOT NULL | Employee badge number |
| nom | VARCHAR(100) | NOT NULL | Last name |
| prenom | VARCHAR(100) | NOT NULL | First name |
| zone_affectation | VARCHAR(100) | | Assigned geographic zone |
| niveau_accreditation | SMALLINT | | Accreditation level 1-5 |
| statut | VARCHAR(20) | | ACTIF, INACTIF, SUSPENDU |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last ETL sync |

### dim_station

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| station_id | UUID | PK | Station identifier |
| nom | VARCHAR(200) | NOT NULL | Station name |
| type_station | VARCHAR(30) | | TRAM, BUS, METRO, HUB |
| localisation | VARCHAR(200) | | Human-readable location |
| coords_gps | VARCHAR(50) | | lat,lng pair |
| statut | VARCHAR(20) | | OUVERTE, FERMEE, etc. |
| lignes_desservies | TEXT | | Served transit lines (JSON string) |

### dim_machine

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| machine_id | UUID | PK | TPVS terminal identifier |
| numero_serie | VARCHAR(64) | NOT NULL | Serial number |
| modele | VARCHAR(100) | | Hardware model |
| type_machine | VARCHAR(30) | | Station type context |
| localisation | VARCHAR(200) | | Physical location |
| statut | VARCHAR(20) | | DISPONIBLE, EN_PANNE, etc. |
| batterie | SMALLINT | | Battery level 0-100 |

### dim_mission

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| mission_id | UUID | PK | Mission identifier |
| zone_couverture | VARCHAR(100) | | Coverage zone |
| statut | VARCHAR(20) | | PLANIFIEE, EN_COURS, TERMINEE, ANNULEE |
| description | TEXT | | Mission description |

### dim_carte

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| carte_type_id | SERIAL | PK | Card type surrogate key |
| type_carte | VARCHAR(30) | NOT NULL, UNIQUE | NAVIGO, TICKET_T_PLUS, etc. |
| description | VARCHAR(200) | | Human-readable label |

### fact_transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| transaction_id | UUID | PK | Transaction identifier |
| date_id | INTEGER | FK → dim_date | Transaction date |
| agent_id | UUID | FK → dim_agent | Processing agent |
| station_id | UUID | FK → dim_station | Station |
| machine_id | UUID | FK → dim_machine | TPVS terminal |
| mission_id | UUID | FK → dim_mission | Associated mission |
| carte_type_id | INTEGER | FK → dim_carte | Card type sold |
| montant | NUMERIC(10,2) | NOT NULL | Transaction amount (EUR) |
| type_paiement | VARCHAR(20) | | CB, TRANSPORT, ESPECES, MOBILE |
| statut_validation | VARCHAR(20) | | EN_ATTENTE, VALIDEE, REJETEE |
| statut_sync | VARCHAR(20) | | SYNC, EN_ATTENTE, ECHEC |
| numero_transaction | VARCHAR(64) | NOT NULL | Unique transaction number |
| loaded_at | TIMESTAMPTZ | DEFAULT NOW() | ETL load timestamp |

### fact_missions

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Surrogate key |
| mission_id | UUID | Mission reference |
| date_id | INTEGER FK | Mission start date |
| agent_id | UUID FK | Assigned agent |
| station_id | UUID FK | Station |
| duree_minutes | INTEGER | Actual duration |
| duree_prevue_minutes | INTEGER | Planned duration |
| taux_completion | NUMERIC(5,4) | Completion ratio |
| statut | VARCHAR(20) | Mission status |
| zone_couverture | VARCHAR(100) | Zone |

### fact_stock

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Surrogate key |
| date_id | INTEGER FK | Snapshot date |
| station_id | UUID FK | Station |
| carte_type_id | INTEGER FK | Card type |
| quantite_actuelle | INTEGER | Current stock level |
| quantite_initiale | INTEGER | Initial stock |
| seuil_alerte | INTEGER | Alert threshold |
| taux_defectueux | NUMERIC(5,4) | Defect rate |
| taux_rotation | NUMERIC(8,4) | Rotation rate |
| alerte_seuil | BOOLEAN | Below threshold flag |

### fact_motos

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Surrogate key |
| moto_id | UUID | Moto identifier |
| date_id | INTEGER FK | Snapshot date |
| agent_id | UUID FK | Assigned agent |
| kilometrage | NUMERIC(10,2) | Odometer reading |
| niveau_batterie | SMALLINT | Battery % |
| latitude | NUMERIC(9,6) | GPS latitude |
| longitude | NUMERIC(9,6) | GPS longitude |
| statut_moto | VARCHAR(20) | Status |

### fact_performances

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Surrogate key |
| date_id | INTEGER FK | Performance date |
| agent_id | UUID FK | Agent |
| nb_transactions | INTEGER | Transaction count |
| montant_total | NUMERIC(12,2) | Total revenue |
| taux_validation | NUMERIC(5,4) | Validation rate |
| score_performance | NUMERIC(8,4) | Composite score |
| nb_missions | INTEGER | Mission count |
| taux_completion | NUMERIC(5,4) | Mission completion rate |

### etl_watermarks

| Column | Type | Description |
|--------|------|-------------|
| pipeline_name | VARCHAR(100) PK | ETL pipeline identifier |
| last_loaded_at | TIMESTAMPTZ | Last successful load timestamp |
| last_id | VARCHAR(100) | Optional cursor |
| updated_at | TIMESTAMPTZ | Last update |
