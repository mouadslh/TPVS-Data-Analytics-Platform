-- TPVS Data Warehouse — Star Schema (Phase 1)
-- Applied on first PostgreSQL init and via `manage.py init_dwh`

CREATE SCHEMA IF NOT EXISTS dwh;

-- ---------------------------------------------------------------------------
-- Dimension tables
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_id         SERIAL PRIMARY KEY,
    date            DATE NOT NULL UNIQUE,
    jour            SMALLINT NOT NULL,
    semaine         SMALLINT NOT NULL,
    mois            SMALLINT NOT NULL,
    trimestre       SMALLINT NOT NULL,
    annee           SMALLINT NOT NULL,
    jour_semaine    SMALLINT NOT NULL,
    est_ferie       BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dwh.dim_agent (
    agent_id                UUID PRIMARY KEY,
    matricule               VARCHAR(32) NOT NULL,
    nom                     VARCHAR(100) NOT NULL,
    prenom                  VARCHAR(100) NOT NULL,
    zone_affectation        VARCHAR(100),
    niveau_accreditation    SMALLINT,
    statut                  VARCHAR(20),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.dim_station (
    station_id          UUID PRIMARY KEY,
    nom                 VARCHAR(200) NOT NULL,
    type_station        VARCHAR(30),
    localisation        VARCHAR(200),
    coords_gps          VARCHAR(50),
    statut              VARCHAR(20),
    lignes_desservies   TEXT,
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.dim_machine (
    machine_id      UUID PRIMARY KEY,
    numero_serie    VARCHAR(64) NOT NULL,
    modele          VARCHAR(100),
    type_machine    VARCHAR(30),
    localisation    VARCHAR(200),
    statut          VARCHAR(20),
    batterie        SMALLINT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.dim_mission (
    mission_id          UUID PRIMARY KEY,
    zone_couverture     VARCHAR(100),
    statut              VARCHAR(20),
    description         TEXT,
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.dim_carte (
    carte_type_id   SERIAL PRIMARY KEY,
    type_carte      VARCHAR(30) NOT NULL UNIQUE,
    description     VARCHAR(200)
);

-- ---------------------------------------------------------------------------
-- Fact tables
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dwh.fact_transactions (
    transaction_id      UUID PRIMARY KEY,
    date_id             INTEGER REFERENCES dwh.dim_date(date_id),
    agent_id            UUID REFERENCES dwh.dim_agent(agent_id),
    station_id          UUID REFERENCES dwh.dim_station(station_id),
    machine_id          UUID REFERENCES dwh.dim_machine(machine_id),
    mission_id          UUID REFERENCES dwh.dim_mission(mission_id),
    carte_type_id       INTEGER REFERENCES dwh.dim_carte(carte_type_id),
    montant             NUMERIC(10,2) NOT NULL,
    type_paiement       VARCHAR(20),
    statut_validation   VARCHAR(20),
    statut_sync         VARCHAR(20),
    numero_transaction  VARCHAR(64) NOT NULL,
    loaded_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON dwh.fact_transactions(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_tx_agent ON dwh.fact_transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_fact_tx_station ON dwh.fact_transactions(station_id);
CREATE INDEX IF NOT EXISTS idx_fact_tx_timestamp ON dwh.fact_transactions(loaded_at);

CREATE TABLE IF NOT EXISTS dwh.fact_missions (
    id                      SERIAL PRIMARY KEY,
    mission_id              UUID NOT NULL,
    date_id                 INTEGER REFERENCES dwh.dim_date(date_id),
    agent_id                UUID REFERENCES dwh.dim_agent(agent_id),
    station_id              UUID REFERENCES dwh.dim_station(station_id),
    duree_minutes           INTEGER,
    duree_prevue_minutes    INTEGER,
    taux_completion         NUMERIC(5,4),
    statut                  VARCHAR(20),
    zone_couverture         VARCHAR(100),
    loaded_at               TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.fact_stock (
    id                  SERIAL PRIMARY KEY,
    date_id             INTEGER REFERENCES dwh.dim_date(date_id),
    station_id          UUID REFERENCES dwh.dim_station(station_id),
    carte_type_id       INTEGER REFERENCES dwh.dim_carte(carte_type_id),
    quantite_actuelle   INTEGER,
    quantite_initiale   INTEGER,
    seuil_alerte        INTEGER,
    taux_defectueux     NUMERIC(5,4),
    taux_rotation       NUMERIC(8,4),
    alerte_seuil        BOOLEAN DEFAULT FALSE,
    loaded_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.fact_motos (
    id                  SERIAL PRIMARY KEY,
    moto_id             UUID NOT NULL,
    date_id             INTEGER REFERENCES dwh.dim_date(date_id),
    agent_id            UUID REFERENCES dwh.dim_agent(agent_id),
    kilometrage         NUMERIC(10,2),
    niveau_batterie     SMALLINT,
    latitude            NUMERIC(9,6),
    longitude           NUMERIC(9,6),
    statut_moto         VARCHAR(20),
    loaded_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.fact_performances (
    id                      SERIAL PRIMARY KEY,
    date_id                 INTEGER REFERENCES dwh.dim_date(date_id),
    agent_id                UUID REFERENCES dwh.dim_agent(agent_id),
    nb_transactions         INTEGER DEFAULT 0,
    montant_total           NUMERIC(12,2) DEFAULT 0,
    taux_validation         NUMERIC(5,4) DEFAULT 0,
    score_performance       NUMERIC(8,4) DEFAULT 0,
    nb_missions             INTEGER DEFAULT 0,
    taux_completion         NUMERIC(5,4) DEFAULT 0,
    loaded_at               TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date_id, agent_id)
);

-- ETL watermark tracking
CREATE TABLE IF NOT EXISTS dwh.etl_watermarks (
    pipeline_name   VARCHAR(100) PRIMARY KEY,
    last_loaded_at  TIMESTAMPTZ,
    last_id         VARCHAR(100),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Seed carte types
INSERT INTO dwh.dim_carte (type_carte, description) VALUES
    ('NAVIGO', 'Carte Navigo'),
    ('TICKET_T_PLUS', 'Ticket t+'),
    ('CARTE_JEUNE', 'Carte Jeune'),
    ('CARTE_SENIOR', 'Carte Senior'),
    ('PASS_JOUR', 'Pass Jour')
ON CONFLICT (type_carte) DO NOTHING;
