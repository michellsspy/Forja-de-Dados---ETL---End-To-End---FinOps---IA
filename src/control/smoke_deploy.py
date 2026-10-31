# Databricks notebook source
"""
Projeto: Forja de Dados - ETL End to End - FinOps - IA
Arquivo: src/control/smoke_deploy.py
Modulo: Controle / Validacao de Deployment

Objetivo:
    Validar a execucao de um Lakeflow Job implantado
    utilizando Databricks Declarative Automation Bundles.

Parametros:
    ambiente (str):
        Ambiente de execucao: dev, hml ou prd.

Processamento:
    1. Recuperar o parametro do Job.
    2. Validar o ambiente informado.
    3. Registrar o horario UTC.
    4. Apresentar o resultado da execucao.

Persistencia:
    Nenhuma. Nao cria, modifica ou remove dados.

Dependencias:
    Databricks Runtime / Serverless.
    Python Standard Library.

Execucao:
    Lakeflow Jobs via Databricks Bundle.

Formato:
    Databricks Notebook Source (.py).

Versionamento:
    GitHub - Forja de Dados.
"""

# COMMAND ----------

from datetime import datetime, timezone


# =============================================================================
# 01 - PARAMETROS
# =============================================================================

dbutils.widgets.text("ambiente", "dev")

ambiente = dbutils.widgets.get("ambiente").strip().lower()


# =============================================================================
# 02 - VALIDACAO
# =============================================================================

AMBIENTES_PERMITIDOS = {"dev", "hml", "prd"}

if ambiente not in AMBIENTES_PERMITIDOS:
    raise ValueError(
        f"Ambiente invalido: {ambiente}. "
        f"Permitidos: {sorted(AMBIENTES_PERMITIDOS)}"
    )


# =============================================================================
# 03 - RESULTADO
# =============================================================================

executado_em = datetime.now(timezone.utc).isoformat()

print("=" * 60)
print("FORJA DE DADOS - VALIDACAO DE DEPLOYMENT")
print("=" * 60)

print(f"Ambiente: {ambiente.upper()}")
print(f"Executado em UTC: {executado_em}")
print("Plataforma: Databricks")
print("Orquestracao: Lakeflow Jobs")
print("Deployment: Databricks Bundles")
print("Status: SUCCESS")

print("=" * 60)
