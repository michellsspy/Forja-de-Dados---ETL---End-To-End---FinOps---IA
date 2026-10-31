"""Valida planos Databricks Bundle antes do CD em DEV.

Projeto: Forja de Dados - ETL End to End - FinOps - IA.
Arquivo: scripts/ci/validate_bundle_plan.py
Objetivo: validar criacao/atualizacao e aceitar recursos sem mudanca (skip).
Entradas: caminho para plano JSON gerado por `databricks bundle plan -t dev -o json`.
Saida: resumo sem credenciais; codigo 0 (aprovado) ou 1 (bloqueado).
Politica: aceitar skip sem alteracoes, bloquear delete, tipos nao autorizados,
         destinos fora de DEV e estado remoto de outro deployment.
Execucao: python scripts/ci/validate_bundle_plan.py /caminho/plan.json
Dependencias: biblioteca padrao Python 3.12+.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

RESOURCE_PATTERN = re.compile(r"^resources\.(jobs|pipelines)\.[A-Za-z0-9_]+$")
ALLOWED_ACTIONS = {"create", "update", "skip"}
ALLOWED_CATALOGS = {
    "forja_lakehouse_dev", "forja_platform_dev", "forja_analytics_dev"
}
METADATA_SUFFIX = "/.bundle/forja_de_dados/dev/state/metadata.json"


class PlanRejected(ValueError):
    """Indica violacao da politica de deploy do laboratorio."""


def check_metadata(state: dict[str, Any], key: str) -> None:
    """Confere o caminho de estado de um recurso, quando presente."""
    metadata = (state.get("deployment") or {}).get("metadata_file_path")
    if metadata is not None and not (
        isinstance(metadata, str) and metadata.endswith(METADATA_SUFFIX)
    ):
        raise PlanRejected(f"{key}: estado remoto de outro deployment.")


def validate_plan(data: dict[str, Any]) -> dict[str, int]:
    """Valida recurso, acao, destino e ligacao ao Bundle DEV sem IDs fixos."""
    if data.get("plan_version") != 2:
        raise PlanRejected("Formato de plano nao reconhecido (esperado version 2).")
    resources = data.get("plan")
    if not isinstance(resources, dict):
        raise PlanRejected("Campo plan ausente ou invalido.")

    counts = {"create": 0, "update": 0, "skip": 0}
    for key, item in resources.items():
        match = RESOURCE_PATTERN.fullmatch(key)
        if not match or not isinstance(item, dict):
            raise PlanRejected(f"Recurso nao permitido: {key}")

        action = item.get("action")
        if action not in ALLOWED_ACTIONS:
            raise PlanRejected(f"{key}: acao '{action}' bloqueada.")

        # Recursos sincronizados podem constar no JSON com action='skip'.
        # Nao criam, modificam nem removem objetos e nao exigem deploy.
        if action == "skip":
            changes = item.get("changes") or {}
            if not isinstance(changes, dict):
                raise PlanRejected(f"{key}: changes invalido em skip.")
            if any(
                not isinstance(change, dict)
                or change.get("action") not in (None, "skip")
                for change in changes.values()
            ):
                raise PlanRejected(f"{key}: skip contem alteracoes de campos.")

            remote = item.get("remote_state") or {}
            planned = (item.get("new_state") or {}).get("value") or {}
            for state in (remote, planned):
                if not isinstance(state, dict):
                    raise PlanRejected(f"{key}: estado invalido em skip.")
                check_metadata(state, key)
                if match.group(1) == "pipelines" and state.get("catalog"):
                    if state["catalog"] not in ALLOWED_CATALOGS:
                        raise PlanRejected(f"{key}: catalogo nao autorizado em skip.")
            counts["skip"] += 1
            continue

        new = (item.get("new_state") or {}).get("value")
        if not isinstance(new, dict):
            raise PlanRejected(f"{key}: new_state.value ausente.")

        name = new.get("name")
        if not isinstance(name, str) or not name.startswith("forja_dev_"):
            raise PlanRejected(f"{key}: nome nao corresponde ao ambiente DEV.")

        # Pipelines devem publicar somente nos catalogos autorizados para DEV.
        if match.group(1) == "pipelines":
            catalog = new.get("catalog")
            if catalog not in ALLOWED_CATALOGS:
                raise PlanRejected(f"{key}: catalogo de pipeline nao autorizado: {catalog}")
            for field in ("schema", "target"):
                target = new.get(field)
                if isinstance(target, str) and ("_hml" in target or "_prd" in target):
                    raise PlanRejected(f"{key}: {field} referencia outro ambiente.")

        run_as = new.get("run_as") or {}
        if run_as:
            expected_client_id = os.environ.get("DATABRICKS_CLIENT_ID")
            actual_client_id = run_as.get("service_principal_name")
            if not expected_client_id or actual_client_id != expected_client_id:
                raise PlanRejected(f"{key}: run_as fora da identidade de DEV.")

        check_metadata(new, key)
        remote = item.get("remote_state") or {}
        if action == "update":
            if not isinstance(remote, dict) or not remote:
                raise PlanRejected(f"{key}: atualizacao sem estado remoto.")
            id_field = "job_id" if match.group(1) == "jobs" else "pipeline_id"
            if not remote.get(id_field):
                raise PlanRejected(f"{key}: ID remoto ausente ({id_field}).")
            check_metadata(remote, key)
        elif remote:
            raise PlanRejected(f"{key}: criacao possui estado remoto inesperado.")

        counts[action] += 1

    return counts


def main() -> int:
    """Le o plano do disco e retorna status apropriado para GitHub Actions."""
    if len(sys.argv) != 2:
        print("Uso: python validate_bundle_plan.py <arquivo.json>", file=sys.stderr)
        return 2
    try:
        plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        result = validate_plan(plan)
    except (OSError, json.JSONDecodeError, PlanRejected) as exc:
        print(f"PLANO BLOQUEADO: {exc}", file=sys.stderr)
        return 1
    print(f"PLANO APROVADO: {result['create']} criacao(oes), "
          f"{result['update']} atualizacao(oes), "
          f"{result['skip']} recurso(s) sem mudanca (skip), nenhuma exclusao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
