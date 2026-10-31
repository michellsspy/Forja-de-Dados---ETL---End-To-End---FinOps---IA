"""Testes de seguranca do CD DEV.

Projeto: Forja de Dados - ETL End to End - FinOps - IA.
Arquivo: tests/test_plan_policy.py
Objetivo: validar permissoes e bloqueios do verificador de planos.
Execucao: python -m pytest tests/test_plan_policy.py -v
Dependencia: pytest; modulo local scripts/ci/validate_bundle_plan.py.
"""

import importlib.util
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1] / "scripts/ci/validate_bundle_plan.py"
SPEC = importlib.util.spec_from_file_location("validate_bundle_plan", FILE)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


def plan(resource=None):
    """Monta plano compativel com o mecanismo Direct."""
    return {"plan_version": 2, "plan": resource or {}}


def resource(action="create", kind="jobs", name="forja_dev_teste"):
    """Monta um recurso sintetico para testes unitarios."""
    value = {"name": name}
    if kind == "pipelines":
        value["catalog"] = "forja_lakehouse_dev"
    item = {"action": action, "new_state": {"value": value}}
    if action == "update":
        item["remote_state"] = {
            "job_id" if kind == "jobs" else "pipeline_id": "id-existente"
        }
    return item


def test_no_changes():
    """Um Bundle sem diffs e valido."""
    assert policy.validate_plan(plan()) == {"create": 0, "update": 0, "skip": 0}


def test_create_job():
    """Criacao de Job DEV e permitida."""
    key = "resources.jobs.job_novo"
    assert policy.validate_plan(plan({key: resource()}))["create"] == 1


def test_update_pipeline():
    """Atualizacao de Pipeline com ID remoto e permitida."""
    key = "resources.pipelines.bronze"
    assert policy.validate_plan(plan({key: resource("update", "pipelines")}))["update"] == 1


def test_delete_blocked():
    """Exclusoes sao sempre bloqueadas."""
    key = "resources.jobs.job_novo"
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: resource("delete")}))


def test_wrong_type_blocked():
    """Criacoes de catalogos exigem revisao da politica."""
    key = "resources.catalogs.outro"
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: resource()}))


def test_cross_environment_catalog_blocked():
    """Pipeline nao pode publicar em HML ou PRD."""
    key = "resources.pipelines.bronze"
    p = resource(kind="pipelines")
    p["new_state"]["value"]["catalog"] = "forja_lakehouse_prd"
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: p}))


def test_update_without_remote_id_blocked():
    """Nao atualiza recurso que nao foi encontrado no estado remoto."""
    key = "resources.jobs.job_existente"
    p = resource("update")
    p["remote_state"] = {"name": "forja_dev_teste"}
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: p}))


def test_foreign_metadata_blocked():
    """Rejeita estado de outro ambiente ou outro Bundle."""
    key = "resources.jobs.job_existente"
    p = resource("update")
    p["remote_state"]["deployment"] = {
        "metadata_file_path": "/Workspace/.bundle/forja_de_dados/prd/state/metadata.json"
    }
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: p}))


def test_run_as_unknown_blocked(monkeypatch):
    """Rejeita mudanca inesperada de identidade de execucao."""
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "id-dev")
    key = "resources.jobs.job_existente"
    p = resource("update")
    p["new_state"]["value"]["run_as"] = {"service_principal_name": "id-prd"}
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(plan({key: p}))


def test_skip_recurso_inalterado():
    """Recurso sincronizado e aceito como no-op sem deploy."""
    key = "resources.jobs.job_smoke_deploy"
    result = policy.validate_plan(plan({
        key: {"action": "skip", "remote_state": {
            "job_id": 962077507374725,
            "name": "forja_dev_smoke_deploy",
        }}
    }))
    assert result == {"create": 0, "update": 0, "skip": 1}


def test_skip_com_create_no_mesmo_plano():
    """Um skip nao impede criar um novo Job no mesmo plano."""
    p = plan({
        "resources.jobs.job_smoke_deploy": {"action": "skip"},
        "resources.jobs.job_novo": resource(),
    })
    assert policy.validate_plan(p) == {"create": 1, "update": 0, "skip": 1}


def test_skip_com_diferenca_ativa_bloqueado():
    """Skip nao pode ocultar campo com mudanca efetiva."""
    key = "resources.jobs.job_smoke_deploy"
    p = plan({key: {
        "action": "skip",
        "changes": {"name": {"action": "update"}},
    }})
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(p)


def test_skip_com_metadata_estrangeiro_bloqueado():
    """Mesmo no-op deve rejeitar estado de outro Bundle."""
    key = "resources.jobs.job_smoke_deploy"
    p = plan({key: {"action": "skip", "remote_state": {
        "deployment": {"metadata_file_path":
            "/Workspace/.bundle/forja_de_dados/prd/state/metadata.json"}
    }}})
    with pytest.raises(policy.PlanRejected):
        policy.validate_plan(p)
