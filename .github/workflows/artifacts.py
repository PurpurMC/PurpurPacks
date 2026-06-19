import os
import zipfile

from config import distro_folder
from constants import (
    ALWAYS_EXCLUDED,
    ALL_LOADER_METADATA,
    FABRIC_METADATA_FILES,
    QUILT_METADATA_FILES,
    FORGE_METADATA_FILES,
    NEOFORGE_METADATA_FILES,
)


_LOADER_GROUPS: dict[str, set[str]] = {
    "fabric": FABRIC_METADATA_FILES,
    "quilt": QUILT_METADATA_FILES,
    "forge": FORGE_METADATA_FILES,
    "neoforge": NEOFORGE_METADATA_FILES,
}


def _artifact_name(root: str, pack_root: str, version: str, suffix: str) -> str:
    relative = os.path.relpath(root, pack_root)
    base = relative.replace(os.sep, "_")
    return f"{base}_v{version}{suffix}"


def _write_archive(root: str, dest_path: str, excluded: set[str]) -> None:
    os.makedirs(distro_folder, exist_ok=True)
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(root):
            for file in files:
                if file in excluded:
                    continue
                full = os.path.join(dirpath, file)
                z.write(full, arcname=os.path.relpath(full, root))


def build_datapack_zipfile(root: str, pack_root: str, version: str) -> tuple[str, str]:
    name = _artifact_name(root, pack_root, version, ".zip")
    path = os.path.join(distro_folder, name)
    _write_archive(root, path, ALWAYS_EXCLUDED | ALL_LOADER_METADATA)
    return path, name


def build_mod_jar(root: str, pack_root: str, version: str, loader: str, source_dir: str | None = None) -> tuple[str, str]:
    if loader not in _LOADER_GROUPS:
        raise ValueError(f"Unknown loader group '{loader}'. Valid options: {list(_LOADER_GROUPS)}")
    name = _artifact_name(root, pack_root, version, f"-{loader}.jar")
    path = os.path.join(distro_folder, name)
    own_files = _LOADER_GROUPS[loader]
    excluded = ALWAYS_EXCLUDED | (ALL_LOADER_METADATA - own_files)
    _write_archive(source_dir or root, path, excluded)
    return path, name
