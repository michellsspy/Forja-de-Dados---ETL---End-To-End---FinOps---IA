"""
Projeto: Forja de Dados - ETL End to End - FinOps - IA
Arquivo: tests/test_bundle_configuration.py

Objetivo:
    Validar as configuracoes do Databricks Bundle
    e a estrutura dos notebooks referenciados.

Validacoes:
    - Identificador do Bundle.
    - Targets DEV, HML e PRD.
    - Modos de implantacao.
    - Isolamento dos catalogos.
    - Caminhos de HML e PRD.
    - Formato Databricks Notebook Source.

Dependencias:
    pytest
    PyYAML

Execucao:
    python -m pytest tests/test_bundle_configuration.py -v

Observacao:
    Complementa, mas nao substitui,
    o comando databricks bundle validate.
"""

from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_FILE = PROJECT_ROOT / "databricks.yml"

SMOKE_NOTEBOOK = (
    PROJECT_ROOT / "src" / "control" / "smoke_deploy.py"
)


@pytest.fixture(scope="module")
def bundle_config():
    """Carrega a configuracao principal do Bundle."""
    with BUNDLE_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_bundle_name(bundle_config):
    """Valida o nome oficial do projeto."""
    assert bundle_config["bundle"]["name"] == "forja_de_dados"


def test_required_targets(bundle_config):
    """Valida os ambientes obrigatorios."""
    targets = bundle_config["targets"]

    assert set(targets) == {"dev", "hml", "prd"}


def test_development_target(bundle_config):
    """Valida a configuracao de desenvolvimento."""
    dev = bundle_config["targets"]["dev"]

    assert dev["default"] is True
    assert dev["mode"] == "development"


@pytest.mark.parametrize("target", ["hml", "prd"])
def test_stable_targets(bundle_config, target):
    """Valida os ambientes de homologacao e producao."""
    config = bundle_config["targets"][target]

    assert config["mode"] == "production"

    root_path = config["workspace"]["root_path"]

    assert "${bundle.name}" in root_path
    assert "${bundle.target}" in root_path


@pytest.mark.parametrize("target", ["dev", "hml", "prd"])
def test_catalog_isolation(bundle_config, target):
    """Valida o isolamento logico por catalogos."""
    variables = bundle_config["targets"][target]["variables"]

    expected = {
        "catalog_lakehouse": f"forja_lakehouse_{target}",
        "catalog_platform": f"forja_platform_{target}",
        "catalog_analytics": f"forja_analytics_{target}",
    }

    assert variables == expected


def test_notebook_source_format():
    """
    Valida o formato Databricks Notebook Source.

    O arquivo precisa iniciar diretamente com o marcador
    esperado, sem BOM ou comentarios anteriores.
    """
    assert SMOKE_NOTEBOOK.is_file(), (
        f"Notebook nao encontrado: {SMOKE_NOTEBOOK}"
    )

    content = SMOKE_NOTEBOOK.read_bytes()

    expected_header = b"# Databricks notebook source"

    first_line = content.splitlines()[0] if content else b""

    assert first_line == expected_header, (
        "O arquivo smoke_deploy.py nao possui o marcador "
        "Databricks notebook source na primeira linha, "
        "ou contem caracteres invisiveis antes dele."
    )
