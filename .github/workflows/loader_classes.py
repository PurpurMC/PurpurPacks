from dataclasses import dataclass
import json
import os
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


DEFAULTS_DIR = os.path.dirname(__file__)


@dataclass
class LoaderDefaults:
    """Modrinth API payload defaults and version suffix for one loader type."""
    suffix: str | None
    defaults: dict


@dataclass
class LoaderTemplates:
    """Describes one loader manifest template and where to write it."""
    manifest_path: Path
    output_path: str
    version_suffix: str
    is_toml: bool = False


DATAPACK_DEFAULTS = LoaderDefaults(
    suffix=None,
    defaults=load_json(os.path.join(DEFAULTS_DIR, "templates", "datapack-modrinth.json")),
)

FABRIC_DEFAULTS = LoaderDefaults(
    suffix="fabric",
    defaults=load_json(os.path.join(DEFAULTS_DIR, "templates", "mod-fabric-modrinth.json")),
)

QUILT_DEFAULTS = LoaderDefaults(
    suffix="quilt",
    defaults=load_json(os.path.join(DEFAULTS_DIR, "templates", "mod-quilt-modrinth.json")),
)

FORGE_DEFAULTS = LoaderDefaults(
    suffix="forge",
    defaults=load_json(os.path.join(DEFAULTS_DIR, "templates", "mod-forge-modrinth.json")),
)

NEOFORGE_DEFAULTS = LoaderDefaults(
    suffix="neoforge",
    defaults=load_json(os.path.join(DEFAULTS_DIR, "templates", "mod-neoforge-modrinth.json")),
)

_MANIFESTS = Path(DEFAULTS_DIR) / "mod-manifests"

FABRIC_TEMPLATE = LoaderTemplates(
    manifest_path=_MANIFESTS / "fabric.mod.json",
    output_path="fabric.mod.json",
    version_suffix="+fabric_quilt",
)

QUILT_TEMPLATE = LoaderTemplates(
    manifest_path=_MANIFESTS / "quilt-mod.json",
    output_path="quilt.mod.json",
    version_suffix="+fabric_quilt",
)

FORGE_TEMPLATE = LoaderTemplates(
    manifest_path=_MANIFESTS / "META-INF" / "mods.toml",
    output_path=os.path.join("META-INF", "mods.toml"),
    version_suffix="+forge_neoforge",
    is_toml=True,
)

NEOFORGE_TEMPLATE = LoaderTemplates(
    manifest_path=_MANIFESTS / "META-INF" / "neoforge.mods.toml",
    output_path=os.path.join("META-INF", "neoforge.mods.toml"),
    version_suffix="+forge_neoforge",
    is_toml=True,
)

ALL_LOADER_TEMPLATES = [FABRIC_TEMPLATE, QUILT_TEMPLATE, FORGE_TEMPLATE, NEOFORGE_TEMPLATE]
