
"""
Projeto: Forja de Dados - ETL End to End - FinOps - IA
Arquivo: tests/test_bundle_configuration.py

Objetivo:
    Validar a estrutura declarativa do Databricks Bundle.

Escopo:
    - Nome do projeto.
    - Existencia dos ambientes DEV, HML e PRD.
    - Modos de implantacao.
    - Separacao dos catalogos.
    - Caminhos fixos de HML e PRD.

Dependencias:
    pytest
    PyYAML

Execucao:
    python -m pytest tests/test_bundle_configuration.py -v

Observacao:
    Estes testes validam convencoes do projeto, nao substituindo
    a validacao oficial da Databricks CLI.
"""

from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_FILE = PROJECT_ROOT / "databricks.yml"


@pytest.fixture(scope="module")
def bundle_config():
    """Carrega a configuracao principal do Databricks Bundle."""
    with BUNDLE_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_bundle_name(bundle_config):
    """Verifica o identificador oficial do projeto."""
    assert bundle_config["bundle"]["name"] == "forja_de_dados"


def test_required_targets(bundle_config):
    """Verifica a existencia dos tres ambientes."""
    targets = bundle_config["targets"]

    assert set(targets) == {"dev", "hml", "prd"}


def test_development_target(bundle_config):
    """Verifica se DEV e o ambiente padrao."""
    dev = bundle_config["targets"]["dev"]

    assert dev["default"] is True
    assert dev["mode"] == "development"


@pytest.mark.parametrize("target", ["hml", "prd"])
def test_stable_targets(bundle_config, target):
    """Verifica o modo de implantacao de HML e PRD."""
    config = bundle_config["targets"][target]

    assert config["mode"] == "production"

    root_path = config["workspace"]["root_path"]

    assert "${bundle.name}" in root_path
    assert "${bundle.target}" in root_path


@pytest.mark.parametrize("target", ["dev", "hml", "prd"])
def test_catalog_isolation(bundle_config, target):
    """Verifica os catalogos especificos de cada ambiente."""
    variables = bundle_config["targets"][target]["variables"]

    expected = {
        "catalog_lakehouse": f"forja_lakehouse_{target}",
        "catalog_platform": f"forja_platform_{target}",
        "catalog_analytics": f"forja_analytics_{target}",
    }

    assert variables == expected
