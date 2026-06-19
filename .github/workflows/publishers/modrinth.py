import json

import requests

from build_metadata import build_modrinth_metadata
from config import DRY_RUN, log, modrinth_post_version_route, modrinth_token, user_agent
from loader_classes import (
    DATAPACK_DEFAULTS,
    FABRIC_DEFAULTS,
    FORGE_DEFAULTS,
    NEOFORGE_DEFAULTS,
    QUILT_DEFAULTS,
)
from publishers import Publisher

_LOADER_DEFAULTS = {
    "fabric": FABRIC_DEFAULTS,
    "quilt": QUILT_DEFAULTS,
    "forge": FORGE_DEFAULTS,
    "neoforge": NEOFORGE_DEFAULTS,
}


class ModrinthPublisher(Publisher):
    def __init__(self) -> None:
        self._version_cache: dict[str, set[str]] = {}

    def _fetch_existing_versions(self, project_id: str) -> set[str]:
        if DRY_RUN:
            return set()

        if project_id in self._version_cache:
            return self._version_cache[project_id]

        url = f"https://api.modrinth.com/v2/project/{project_id}/version?include_changelog=false"
        response = requests.get(url, headers={"Authorization": modrinth_token, "User-Agent": user_agent})

        if response.status_code != 200:
            print(f"Failed to fetch versions for project {project_id}: {response.status_code}")
            self._version_cache[project_id] = set()
            return self._version_cache[project_id]

        self._version_cache[project_id] = {
            v["version_number"] for v in response.json() if "version_number" in v
        }
        return self._version_cache[project_id]

    def _version_exists(self, project_id: str, version_number: str) -> bool:
        if version_number in self._fetch_existing_versions(project_id):
            log(f"Skipping {project_id} {version_number}: already exists on Modrinth")
            return True
        return False

    def _post(self, modrinth_data: dict, file_path: str, file_name: str) -> None:
        if DRY_RUN:
            log("Would upload:")
            log(f"  File:          {file_name}")
            log(f"  Project:       {modrinth_data.get('project_id')}")
            log(f"  Version:       {modrinth_data.get('version_number')}")
            log(f"  Loaders:       {modrinth_data.get('loaders')}")
            log(f"  Game versions: {modrinth_data.get('game_versions')}")
            log(f"  Dependencies:  {modrinth_data.get('dependencies')}")
            log("")
            return

        with open(file_path, "rb") as f:
            response = requests.post(
                modrinth_post_version_route,
                headers={"Authorization": modrinth_token, "User-Agent": user_agent},
                files={"file": (file_name, f, "application/zip")},
                data={"data": json.dumps(modrinth_data)},
            )

        try:
            res = response.json()
        except Exception:
            print(f"Invalid Modrinth response for {file_name}")
            return

        if "error" in res:
            print(f"Upload failed for {file_name}: {res}")
        else:
            print(f"Uploaded {file_name} successfully")

    def needs_publish(self, pack_meta: dict) -> bool:
        project_id = pack_meta.get("project_id")
        version_number = pack_meta.get("version_number")
        return not self._version_exists(project_id, version_number)

    def publish_datapack(self, pack_meta: dict, artifact_path: str, artifact_name: str) -> None:
        meta = build_modrinth_metadata(pack_meta, DATAPACK_DEFAULTS)
        if self._version_exists(meta["project_id"], meta["version_number"]):
            return
        self._post(meta, artifact_path, artifact_name)

    def publish_mod(self, pack_meta: dict, artifact_path: str, artifact_name: str, loader: str) -> None:
        defaults = _LOADER_DEFAULTS.get(loader)
        if defaults is None:
            raise ValueError(f"Unknown loader '{loader}'. Valid options: {list(_LOADER_DEFAULTS)}")
        meta = build_modrinth_metadata(pack_meta, defaults)
        if self._version_exists(meta["project_id"], meta["version_number"]):
            return
        self._post(meta, artifact_path, artifact_name)
