# Forja de Dados — Etapas 2.7 e 2.8

## Escopo

Arquivos prontos para copiar **para a raiz do repositório existente** preservando os caminhos internos.
Não substitua todo o repositório por este pacote: ele contém somente arquivos novos/atualizados.

| Arquivo | Ação | Objetivo |
|---|---|---|
| `databricks.yml` | Substituir | Inclui Jobs e Pipelines, preservando root_path e targets existentes |
| `resources/pipelines/_registry.yml` | Criar | Placeholder declarativo vazio; nenhum Pipeline criado |
| `tests/test_pipeline_discovery.py` | Criar | Verifica descoberta de recursos |
| `.github/workflows/deploy-dev.yml` | Substituir | CD automático em DEV após sucesso do CI da `main`; manual também permitido |
| `scripts/ci/validate_bundle_plan.py` | Criar | Verifica plano JSON: Jobs e Pipelines, criação/atualização, sem exclusão |
| `tests/test_plan_policy.py` | Criar | Testes de segurança da política de deployment |
| `infrastructure/inventory/01_inventario_databricks.sql` | Criar | Inventário read-only do Unity Catalog e destino Lakeflow Connect |
| `infrastructure/inventory/02_inventario_neon_postgresql.sql` | Criar | Inventário read-only do Neon PostgreSQL, incluindo PKs |

## Procedimento

1. Criar branch `feature/cd-dev-generalizado` a partir da `main` atualizada.
2. Copiar estes arquivos para os respectivos caminhos.
3. Executar `python -m pytest tests/ -v`, `databricks bundle validate -t dev`, `databricks bundle plan -t dev`.
4. Commit, push e Pull Request; conferir CI. O merge na `main` deverá acionar o CD pelo evento `workflow_run` quando o CI da `main` concluir com sucesso.
5. Conferir `CD - Deploy Databricks DEV` no GitHub Actions. O Job atual deve manter o mesmo ID.
6. Executar o inventário SQL do Databricks no SQL Editor e o inventário PostgreSQL no console SQL do Neon. Registrar resultados sem dados pessoais.

## Políticas do CD

- Permite apenas ações `create` e `update` para `resources.jobs.*` e `resources.pipelines.*`.
- Requer nome `forja_dev_...`.
- Restringe o catálogo de publicação de pipelines aos três catálogos `forja_*_dev`.
- Bloqueia tentativas de exclusão, alterações em tipos de recurso fora da política e execução como identidade diferente daquela do workflow.
- Uma mudança de banco de origem/CDC não é inferida ou realizada por esses arquivos.
- A análise do plano não é substituta da revisão do PR nem da governança de privilégios Unity Catalog.
- Os workflows HML/PRD permanecem fora do escopo.

## Observações sobre ambiente

- Esta etapa preserva o `databricks.yml` validado anteriormente e o Job smoke existente.
- O workflow usa o Databricks CLI já comprovado no GitHub Actions (`databricks/setup-cli@v1.20.0`).
- O controle de acesso do Service Principal ao Catálogo Unity Catalog deve ser configurado antes de criar os primeiros Pipelines.
- A Bronze append-only requer análise da semântica CDC da origem. Uma tabela de destino SCD1 é um estado corrente, não um log histórico completo.
