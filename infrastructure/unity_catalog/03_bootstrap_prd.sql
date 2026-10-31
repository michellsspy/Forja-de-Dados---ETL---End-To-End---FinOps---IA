
-- =============================================================================
-- PROJETO: Forja de Dados - ETL End to End - FinOps - IA
-- ARQUIVO: 03_bootstrap_prd.sql
-- AMBIENTE: PRD
--
-- OBJETIVO:
--   Provisionar a estrutura Unity Catalog de producao.
--
-- CARACTERISTICAS:
--   - DDL idempotente.
--   - Persistencia gerenciada pelo Unity Catalog.
--   - Isolamento logico de DEV e HML.
--   - Sem DROP, DELETE ou alteracao de dados.
--
-- PRE-REQUISITOS:
--   - Homologacao validada.
--   - Unity Catalog e permissoes configurados.
--   - Armazenamento gerenciado disponivel.
--
-- EXECUCAO:
--   Databricks SQL Warehouse.
-- =============================================================================

-- 01. PLANO DE DADOS

CREATE CATALOG IF NOT EXISTS forja_lakehouse_prd
COMMENT 'Forja de Dados - Lakehouse - PRD';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_prd.landing
COMMENT 'Recepcao logica dos dados';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_prd.bronze
COMMENT 'Dados brutos e historico';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_prd.silver_technical
COMMENT 'Tratamento tecnico e normalizacao';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_prd.silver_analytics
COMMENT 'Integracao analitica de negocio';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_prd.gold
COMMENT 'Modelagem dimensional Star Schema';


-- 02. PLANO DE CONTROLE E GOVERNANCA

CREATE CATALOG IF NOT EXISTS forja_platform_prd
COMMENT 'Forja de Dados - Plataforma - PRD';

CREATE SCHEMA IF NOT EXISTS forja_platform_prd.control
COMMENT 'Controle operacional e execucoes';

CREATE SCHEMA IF NOT EXISTS forja_platform_prd.quality
COMMENT 'Regras e resultados de qualidade';

CREATE SCHEMA IF NOT EXISTS forja_platform_prd.quarantine
COMMENT 'Quarentenas tecnicas e analiticas';

CREATE SCHEMA IF NOT EXISTS forja_platform_prd.observability
COMMENT 'Observabilidade e auditoria';

CREATE SCHEMA IF NOT EXISTS forja_platform_prd.reprocessing
COMMENT 'Controle dos reprocessamentos';


-- 03. PRODUTOS ANALITICOS

CREATE CATALOG IF NOT EXISTS forja_analytics_prd
COMMENT 'Forja de Dados - Analytics - PRD';

CREATE SCHEMA IF NOT EXISTS forja_analytics_prd.marts
COMMENT 'Data marts e produtos analiticos';

CREATE SCHEMA IF NOT EXISTS forja_analytics_prd.semantic
COMMENT 'Camada semantica e metricas';


-- 04. VALIDACAO

SHOW SCHEMAS IN forja_lakehouse_prd;
SHOW SCHEMAS IN forja_platform_prd;
SHOW SCHEMAS IN forja_analytics_prd;
