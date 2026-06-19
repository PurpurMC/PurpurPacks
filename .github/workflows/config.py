import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

datapack_folder = os.getenv("PACKS_DIR") or os.path.join(REPO_ROOT, "packs")
distro_folder = os.getenv("DISTRO_DIR") or os.path.join(REPO_ROOT, "distribute")

user_agent = "Deploy/Purpur/PurpurPacks (https://purpurmc.org/)"
modrinth_post_version_route = "https://api.modrinth.com/v2/version"
modrinth_token = os.getenv('MODRINTH_TOKEN')
DRY_RUN = os.getenv("DRY_RUN") == "true"
CI_SKIP = os.getenv("SKIP_CI") == "true"


def log(msg: str) -> None:
    prefix = "[DRY RUN] " if DRY_RUN else ""
    print(prefix + msg)
