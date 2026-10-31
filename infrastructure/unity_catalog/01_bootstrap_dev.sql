
-- =============================================================================
-- PROJETO: Forja de Dados - ETL End to End - FinOps - IA
-- ARQUIVO: 01_bootstrap_dev.sql
-- CAMADA: Infrastructure / Unity Catalog
-- AMBIENTE: DEV
--
-- OBJETIVO:
--   Provisionar os catalogos e schemas do ambiente de desenvolvimento.
--
-- ARQUITETURA:
--   1. Plano de Dados
--   2. Plano de Controle, Governanca e Observabilidade
--   3. Produtos de Dados e Consumo
--
-- CARACTERISTICAS:
--   - Operacoes idempotentes (IF NOT EXISTS).
--   - Nao remove catalogos ou schemas existentes.
--   - Nao altera dados do Lakeflow Connect.
--   - Nao cria tabelas ou executa cargas.
--   - Utiliza armazenamento gerenciado pelo Unity Catalog.
--
-- PRE-REQUISITOS:
--   - Unity Catalog habilitado.
--   - Privilegio CREATE CATALOG no metastore.
--   - Armazenamento gerenciado padrao disponivel.
--
-- EXECUCAO:
--   Databricks SQL Editor, utilizando um SQL Warehouse.
--
-- VERSIONAMENTO:
--   GitHub / Forja de Dados
-- =============================================================================


-- =============================================================================
-- 01 - PLANO DE DADOS
-- =============================================================================

CREATE CATALOG IF NOT EXISTS forja_lakehouse_dev
COMMENT 'Forja de Dados - Plano de Dados - DEV';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_dev.landing
COMMENT 'Recepcao logica de dados das origens';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_dev.bronze
COMMENT 'Dados brutos com preservacao e rastreabilidade';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_dev.silver_technical
COMMENT 'Tratamento, normalizacao e validacao tecnica';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_dev.silver_analytics
COMMENT 'Integracao e enriquecimento de entidades de negocio';

CREATE SCHEMA IF NOT EXISTS forja_lakehouse_dev.gold
COMMENT 'Modelo dimensional, fatos e dimensoes';


-- =============================================================================
-- 02 - PLANO DE CONTROLE, GOVERNANCA E OBSERVABILIDADE
-- =============================================================================

CREATE CATALOG IF NOT EXISTS forja_platform_dev
COMMENT 'Forja de Dados - Plataforma e Governanca - DEV';

CREATE SCHEMA IF NOT EXISTS forja_platform_dev.control
COMMENT 'Execucoes, checkpoints e controle operacional';

CREATE SCHEMA IF NOT EXISTS forja_platform_dev.quality
COMMENT 'Regras e resultados de qualidade dos dados';

CREATE SCHEMA IF NOT EXISTS forja_platform_dev.quarantine
COMMENT 'Quarentenas tecnicas e analiticas';

CREATE SCHEMA IF NOT EXISTS forja_platform_dev.observability
COMMENT 'Metricas, auditoria e observabilidade';

CREATE SCHEMA IF NOT EXISTS forja_platform_dev.reprocessing
COMMENT 'Controle de replay, backfill e reprocessamentos';


-- =============================================================================
-- 03 - PLANO DE PRODUTOS DE DADOS
-- =============================================================================

CREATE CATALOG IF NOT EXISTS forja_analytics_dev
COMMENT 'Forja de Dados - Produtos Analiticos - DEV';

CREATE SCHEMA IF NOT EXISTS forja_analytics_dev.marts
COMMENT 'Data marts e produtos analiticos';

CREATE SCHEMA IF NOT EXISTS forja_analytics_dev.semantic
COMMENT 'Camada semantica para consumo e IA';


-- =============================================================================
-- 04 - VALIDACAO DA ESTRUTURA
-- =============================================================================

SHOW SCHEMAS IN forja_lakehouse_dev;

SHOW SCHEMAS IN forja_platform_dev;

SHOW SCHEMAS IN forja_analytics_dev;
