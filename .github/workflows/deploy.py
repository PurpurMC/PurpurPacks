import os
import json
import zipfile
import requests

# Constants
datapack_prefix = "purpurpack_"
datapack_folder = "packs"
user_agent = "Deploy/Purpur/PurpurPacks (https://purpurmc.org/)"
modrinth_post_version_route = "https://api.modrinth.com/v2/version"
modrinth_token = os.getenv('MODRINTH_TOKEN')

if not modrinth_token:
    print("The required environment variable MODRINTH_TOKEN is not set.")
    exit(1)


def fetch_versions_json(project_id):
    """Fetches information about available versions of a project from Modrinth."""
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    headers = {
        "Authorization": modrinth_token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch info for project ID: {project_id} (HTTP {response.status_code})")
        return []


def get_latest_modrinth_version(project_id):
    versions = fetch_versions_json(project_id)
    if not versions:
        print(f"No versions found for project ID: {project_id}")
        return None
    for version_data in versions:
        if "datapack" in version_data.get("loaders", []):
            return version_data.get("version_number")
    return None


def get_datapack_info(modrinth_json_path):
    with open(modrinth_json_path, "r") as modrinth_file:
        file_info = json.load(modrinth_file)
        return file_info


def get_current_version(json_file):
    return json_file.get("version_number", None)


def get_project_id(json_file):
    return json_file.get("project_id", None)


def get_dependencies(json_file):
    return json_file.get("dependencies", [])


def should_update_pack(modrinth_json):
    if modrinth_json is None:
        print("Modrinth JSON is empty or missing, skipping")
        return False

    project_id = get_project_id(modrinth_json)
    current_version = get_current_version(modrinth_json)

    if current_version is None:
        print("Pack does not have a version number, skipping")
        return False

    if project_id is None:
        print("Pack does not have a project ID, skipping")
        return False

    latest_version = get_latest_modrinth_version(project_id)
    if latest_version is None:
        print("Pack does not have a version number, skipping")
        return False

    if latest_version >= current_version:
        print("Pack does not need to be updated, skipping")
        return False

    return True


def zip_and_post(modrinth_info, root):
    version = get_current_version(modrinth_info)
    relative_path = os.path.relpath(root, datapack_folder)
    datapack_name = f"{relative_path.replace(os.sep, '_')}_v{version}.zip"
    dist_dir = os.path.join(datapack_folder, "dist")  # Corrected path
    os.makedirs(dist_dir, exist_ok=True)
    zipped_file_path = os.path.join(dist_dir, datapack_name)

    with zipfile.ZipFile(zipped_file_path, "w", zipfile.ZIP_DEFLATED) as zipped_file:
        for pack_root, dirs, files in os.walk(root):
            for file in files:
                if file == 'modrinth.json':
                    continue
                zipped_file.write(os.path.join(pack_root, file),
                                  arcname=os.path.relpath(os.path.join(pack_root, file), root))
        print(f"Zipped {datapack_name}")

    if not os.path.isfile(zipped_file_path):
        print(f"File {zipped_file_path} does not exist. Skipping upload.")
        return

    post(modrinth_info, datapack_name, zipped_file_path)


def post(modrinth_info, datapack_name, zipped_file_path):
    version = get_current_version(modrinth_info)
    project_id = get_project_id(modrinth_info)
    dependencies = get_dependencies(modrinth_info)
    ver_name = modrinth_info["name"]
    changelog = modrinth_info.get("changelog", "")
    supported_versions = modrinth_info["game_versions"]
    release_type = modrinth_info["version_type"]

    # Open the file in binary mode
    with open(zipped_file_path, 'rb') as file:
        files = {
            'file': (datapack_name, file, 'application/zip')
        }

        # Prepare the payload
        payload = {
            "name": ver_name,
            "version_number": version,
            "changelog": changelog,
            "dependencies": dependencies,
            "game_versions": supported_versions,
            "version_type": release_type,
            "loaders": ['datapack'],
            "featured": False,
            "project_id": project_id,
            "file_parts": ["file"]
        }

        # Convert payload to JSON string
        payload_json = json.dumps(payload)

        # Headers for the request
        headers = {
            "Authorization": modrinth_token,
            "User-Agent": user_agent
        }

        # Perform the POST request
        response = requests.post(
            modrinth_post_version_route,
            headers=headers,
            files=files,
            data={'data': payload_json}
        )

        # Parse the response
        try:
            upload_response = response.json()
        except json.JSONDecodeError:
            print("Failed to decode JSON response")
            return

        # Check for errors in the response
        if 'error' not in upload_response:
            print(f"Successfully uploaded version {version} for {project_id}! Output:\n{upload_response}")
        else:
            print(f"Failed to upload {datapack_name}. Output:\n{upload_response}")


def main():
    for root, dirs, files in os.walk(datapack_folder):
        if 'pack.mcmeta' not in files:
            print(f"{root} is not a pack directory, skipping")
            continue
        if 'modrinth.json' not in files:
            print(f"{root} does not have a modrinth json file, skipping")
            continue
        datapack_info = get_datapack_info(os.path.join(root, "modrinth.json"))
        if not should_update_pack(datapack_info):
            continue
        zip_and_post(datapack_info, root)


if __name__ == "__main__":
    main()
