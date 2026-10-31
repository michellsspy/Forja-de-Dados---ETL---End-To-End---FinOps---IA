-- =============================================================================
-- PROJETO: Forja de Dados - ETL End to End - FinOps - IA
-- ARQUIVO: infrastructure/inventory/01_inventario_databricks.sql
-- OBJETIVO: Inventariar tabelas e colunas visiveis no Unity Catalog.
-- ESCOPO: somente leitura; nao cria ou modifica tabelas.
-- EXECUCAO: Databricks SQL Editor, com SQL Warehouse.
-- OBSERVACAO: resultados dependem das permissoes da identidade.
-- =============================================================================

-- 01. Catalogos, schemas e tabelas visiveis (inspecionar destino Connect).
SELECT
    table_catalog,
    table_schema,
    table_name,
    table_type,
    table_owner
FROM system.information_schema.tables
WHERE table_catalog NOT IN ('system', 'samples')
  AND table_schema <> 'information_schema'
ORDER BY table_catalog, table_schema, table_name;

-- 02. Substituir os dois identificadores pelo destino real do Lakeflow Connect.
--     Exemplo de valores a substituir: CATALOGO_DESTINO, SCHEMA_DESTINO.
SELECT
    table_catalog,
    table_schema,
    table_name,
    ordinal_position,
    column_name,
    full_data_type,
    is_nullable
FROM system.information_schema.columns
WHERE table_catalog = 'CATALOGO_DESTINO'
  AND table_schema = 'SCHEMA_DESTINO'
ORDER BY table_name, ordinal_position;
