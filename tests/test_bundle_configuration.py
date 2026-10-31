
"""
Projeto: Forja de Dados - ETL End to End - FinOps - IA
Arquivo: tests/test_bundle_configuration.py

Objetivo:
    Validar a configuracao declarativa dos Databricks Bundles.

Validacoes:
    - Identificador oficial do projeto.
    - Existencia dos targets DEV, HML e PRD.
    - Configuracao de DEV para automacao.
    - Protecoes de desenvolvimento via presets.
    - Modos de implantacao de HML e PRD.
    - Isolamento logico dos catalogos.
    - Persistencia dos caminhos de deployment.
    - Formato Databricks Notebook Source.

Dependencias:
    pytest
    PyYAML

Execucao:
    python -m pytest tests/test_bundle_configuration.py -v

Observacoes:
    Estes testes complementam o databricks bundle validate.
    Nao executam deploy nem modificam recursos no workspace.

Versionamento:
    GitHub - Forja de Dados.
"""

from pathlib import Path

import pytest
import yaml


# =============================================================================
# 01 - CONFIGURACOES
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BUNDLE_FILE = PROJECT_ROOT / "databricks.yml"

SMOKE_NOTEBOOK = (
    PROJECT_ROOT / "src" / "control" / "smoke_deploy.py"
)

EXPECTED_ROOT_PATH = (
    "/Workspace/Users/michel.laboratorios@gmail.com"
    "/.bundle/${bundle.name}/${bundle.target}"
)


# =============================================================================
# 02 - FIXTURE
# =============================================================================

@pytest.fixture(scope="module")
def bundle_config():
    """Carrega a configuracao principal do Databricks Bundle."""
    with BUNDLE_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# =============================================================================
# 03 - VALIDACAO DO BUNDLE
# =============================================================================

def test_bundle_name(bundle_config):
    """Verifica o identificador oficial do projeto."""
    assert bundle_config["bundle"]["name"] == "forja_de_dados"


def test_required_targets(bundle_config):
    """Verifica a existencia dos tres ambientes."""
    targets = bundle_config["targets"]

    assert set(targets) == {"dev", "hml", "prd"}


# =============================================================================
# 04 - VALIDACAO DO AMBIENTE DEV
# =============================================================================

def test_development_target(bundle_config):
    """
    Verifica se DEV e o target padrao e nao exige
    isolamento individual pelo modo development.
    """
    dev = bundle_config["targets"]["dev"]

    assert dev["default"] is True
    assert "mode" not in dev


def test_development_presets(bundle_config):
    """Verifica as protecoes declarativas do ambiente DEV."""
    presets = bundle_config["targets"]["dev"]["presets"]

    assert presets["pipelines_development"] is True
    assert presets["trigger_pause_status"] == "PAUSED"
    assert presets["jobs_max_concurrent_runs"] == 1


# =============================================================================
# 05 - VALIDACAO DOS AMBIENTES ESTAVEIS
# =============================================================================

@pytest.mark.parametrize("target", ["hml", "prd"])
def test_stable_targets(bundle_config, target):
    """Verifica o modo de implantacao de HML e PRD."""
    config = bundle_config["targets"][target]

    assert config["mode"] == "production"


# =============================================================================
# 06 - ISOLAMENTO DOS CATALOGOS
# =============================================================================

@pytest.mark.parametrize("target", ["dev", "hml", "prd"])
def test_catalog_isolation(bundle_config, target):
    """Verifica o isolamento logico por ambiente."""
    variables = bundle_config["targets"][target]["variables"]

    expected = {
        "catalog_lakehouse": f"forja_lakehouse_{target}",
        "catalog_platform": f"forja_platform_{target}",
        "catalog_analytics": f"forja_analytics_{target}",
    }

    assert variables == expected


# =============================================================================
# 07 - PERSISTENCIA DO ESTADO DOS DEPLOYMENTS
# =============================================================================

@pytest.mark.parametrize("target", ["dev", "hml", "prd"])
def test_fixed_root_paths(bundle_config, target):
    """Verifica os caminhos fixos dos deployments."""
    root_path = bundle_config["targets"][target]["workspace"][
        "root_path"
    ]

    assert root_path == EXPECTED_ROOT_PATH


# =============================================================================
# 08 - FORMATO DO NOTEBOOK DATABRICKS
# =============================================================================

def test_notebook_source_format():
    """Verifica o marcador obrigatorio do Notebook Source."""
    assert SMOKE_NOTEBOOK.is_file(), (
        f"Notebook nao encontrado: {SMOKE_NOTEBOOK}"
    )

    content = SMOKE_NOTEBOOK.read_bytes()

    expected_header = b"# Databricks notebook source"

    first_line = content.splitlines()[0] if content else b""

    assert first_line == expected_header, (
        "O notebook deve iniciar com o marcador "
        "'# Databricks notebook source', sem linhas "
        "vazias ou caracteres anteriores."
    )
