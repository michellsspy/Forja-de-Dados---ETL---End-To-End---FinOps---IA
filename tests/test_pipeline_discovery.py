"""Verifica o preparo do Bundle para futuros recursos Lakeflow.

Projeto: Forja de Dados - ETL End to End - FinOps - IA.
Arquivo: tests/test_pipeline_discovery.py.
Objetivo: confirmar registro de Jobs e Pipelines no Bundle.
Execucao: python -m pytest tests/test_pipeline_discovery.py -v.
Dependencias: pytest e PyYAML (requirements-dev.txt).
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_job_and_pipeline_globs():
    """Requer descoberta separada de recursos de Job e Pipeline."""
    data = yaml.safe_load((ROOT / "databricks.yml").read_text(encoding="utf-8"))
    assert "resources/jobs/*.yml" in data.get("include", [])
    assert "resources/pipelines/*.yml" in data.get("include", [])


def test_pipeline_registry_is_empty():
    """Arquivo indexador nao pode publicar recursos antes do inventario."""
    path = ROOT / "resources/pipelines/_registry.yml"
    assert path.is_file()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data == {"resources": {}}
