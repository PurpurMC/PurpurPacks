import json
import os
import shutil
import tempfile

from artifacts import build_datapack_zipfile, build_mod_jar
from config import CI_SKIP, datapack_folder, log
from loader_files import generate_loader_files
from publishers.modrinth import ModrinthPublisher


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    if CI_SKIP:
        print("CI-Skip detected, returning.")
        return

    publishers = [ModrinthPublisher()]

    if not os.path.isdir(datapack_folder):
        log(f"Directory '{datapack_folder}' does not exist")
        return

    log(f"Starting scan of '{datapack_folder}'")

    for root, _, files in os.walk(datapack_folder):
        if "pack.mcmeta" not in files:
            continue
        if "pack-meta.json" not in files:
            log(f"Skipping {root}: missing pack-meta.json")
            continue

        pack_meta = _load_json(os.path.join(root, "pack-meta.json"))
        version = pack_meta.get("version_number")
        log(f"Found valid pack at {root}")

        if not version:
            print(f"{root} has no version_number, skipping")
            continue

        if not pack_meta.get("project_id"):
            log(f"Skipping {root}: no project_id (pack not yet on Modrinth)")
            continue

        active_publishers = [p for p in publishers if p.needs_publish(pack_meta)]
        if not active_publishers:
            continue

        dp_path, dp_name = build_datapack_zipfile(root, datapack_folder, version)
        for publisher in active_publishers:
            publisher.publish_datapack(pack_meta, dp_path, dp_name)

        if pack_meta.get("has_loader_distribution", True):
            with tempfile.TemporaryDirectory() as staging:
                shutil.copytree(root, staging, dirs_exist_ok=True)
                generate_loader_files(staging, pack_meta)

                for loader in ("fabric", "quilt", "forge", "neoforge"):
                    jar_path, jar_name = build_mod_jar(root, datapack_folder, version, loader, source_dir=staging)
                    for publisher in active_publishers:
                        publisher.publish_mod(pack_meta, jar_path, jar_name, loader)

    log("Finished scan")


if __name__ == "__main__":
    main()
