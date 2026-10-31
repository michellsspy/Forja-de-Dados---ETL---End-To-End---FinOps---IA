
-- =============================================================================
-- PROJETO: Forja de Dados - ETL End to End - FinOps - IA
-- ARQUIVO: 02_bootstrap_hml.sql
-- AMBIENTE: HML
--
-- OBJETIVO:
--   Provisionar a estrutura Unity Catalog de homologacao.
--
-- CARACTERISTICAS:
--   - DDL idempotente.
--   - Persistencia gerenciada pelo Unity Catalog.
--   - Sem alteracao de dados existentes.
--   - Sem dependencias de armazenamento externo.
--
-- PRE-REQUISITOS:
--   - Unity Catalog configurado.
--   - Permissoes de criacao de catalogos e schemas.
--   - Armazenamento gerenciado disponivel.
--
-- EXECUCAO:
--   Databricks SQL Warehouse.
-- =============================================================================

-- 01. PLANO DE DADOS

CREATE CATALOG IF NOT EXISTS forja_lakehouse_hml
COMMENT 'Forja de Dados - Lakehouse - HML';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_hml.landing
COMMENT 'Recepcao logica dos dados';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_hml.bronze
COMMENT 'Dados brutos e historico';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_hml.silver_technical
COMMENT 'Tratamento tecnico e normalizacao';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_hml.silver_analytics
COMMENT 'Integracao analitica de negocio';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_hml.gold
COMMENT 'Modelagem dimensional Star Schema';


-- 02. PLANO DE CONTROLE E GOVERNANCA

CREATE CATALOG IF NOT EXISTS forja_platform_hml
COMMENT 'Forja de Dados - Plataforma - HML';

CREATE SCHEMA IF NOT EXISTS forja_platform_hml.control
COMMENT 'Controle operacional e execucoes';

CREATE SCHEMA IF NOT EXISTS forja_platform_hml.quality
COMMENT 'Regras e resultados de qualidade';

CREATE SCHEMA IF NOT EXISTS forja_platform_hml.quarantine
COMMENT 'Quarentenas tecnicas e analiticas';

CREATE SCHEMA IF NOT EXISTS forja_platform_hml.observability
COMMENT 'Observabilidade e auditoria';

CREATE SCHEMA IF NOT EXISTS forja_platform_hml.reprocessing
COMMENT 'Controle dos reprocessamentos';


-- 03. PRODUTOS ANALITICOS

CREATE CATALOG IF NOT EXISTS forja_analytics_hml
COMMENT 'Forja de Dados - Analytics - HML';

CREATE SCHEMA IF NOT EXISTS forja_analytics_hml.marts
COMMENT 'Data marts e produtos analiticos';

CREATE SCHEMA IF NOT EXISTS forja_analytics_hml.semantic
COMMENT 'Camada semantica e metricas';


-- 04. VALIDACAO

SHOW SCHEMAS IN forja_lakehouse_hml;
SHOW SCHEMAS IN forja_platform_hml;
SHOW SCHEMAS IN forja_analytics_hml;
