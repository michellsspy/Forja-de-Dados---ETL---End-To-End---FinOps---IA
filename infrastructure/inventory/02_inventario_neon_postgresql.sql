-- =============================================================================
-- PROJETO: Forja de Dados - ETL End to End - FinOps - IA
-- ARQUIVO: infrastructure/inventory/02_inventario_neon_postgresql.sql
-- OBJETIVO: Inventariar tabelas, colunas e chaves primarias no Neon PostgreSQL.
-- ESCOPO: somente leitura, usando pg_catalog e information_schema.
-- EXECUCAO: SQL Editor do Neon (NAO no Databricks SQL Editor).
-- SEGURANCA: nao inclui credenciais nem registros de hospedes.
-- =============================================================================

-- 01. Tabelas de negocio.
SELECT
    n.nspname AS schema_origem,
    c.relname AS tabela_origem,
    CASE c.relkind WHEN 'p' THEN 'PARTICIONADA' ELSE 'TABELA' END AS tipo
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'p')
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND n.nspname NOT LIKE 'pg_toast%'
ORDER BY n.nspname, c.relname;

-- 02. Colunas e tipos.
SELECT
    table_schema,
    table_name,
    ordinal_position,
    column_name,
    data_type,
    udt_name,
    is_nullable
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name, ordinal_position;

-- 03. Chaves primarias (inclui chaves compostas e ordem das colunas).
SELECT
    n.nspname AS schema_origem,
    c.relname AS tabela_origem,
    a.attname AS coluna_pk,
    k.posicao AS ordem_pk
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
CROSS JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS k(attnum, posicao)
JOIN pg_catalog.pg_attribute AS a
  ON a.attrelid = c.oid AND a.attnum = k.attnum
WHERE con.contype = 'p'
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY n.nspname, c.relname, k.posicao;
