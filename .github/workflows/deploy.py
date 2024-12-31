import os
import json
import zipfile
import requests

# Constants
datapack_prefix = "purpurpack_"
datapack_folder = "packs"
modrinth_post_version_route = "https://api.modrinth.com/v2/version"
modrinth_token = os.getenv('MODRINTH_TOKEN')

if not modrinth_token:
    print("The required environment variable MODRINTH_TOKEN is not set.")
    exit(1)

def fetch_modrinth_info(project_id):
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
        return None

def get_latest_version(versions):
    """Extracts the latest version number from a JSON array of version data."""
    for version_data in versions:
        if "datapack" in version_data.get("loaders", []):
            return version_data.get("version_number")
    return None

def main():
    for datapack_path in os.listdir(datapack_folder):
        full_datapack_path = os.path.join(datapack_folder, datapack_path)
        modrinth_file_path = os.path.join(full_datapack_path, "modrinth.json")

        # Continue if not a directory
        if not os.path.isdir(full_datapack_path):
            continue

        # Continue if datapack folder does not include modrinth.json
        if not os.path.exists(modrinth_file_path):
            print(f"No modrinth.json file located in {full_datapack_path}")
            continue

        print(f"Processing {datapack_path}...")

        with open('modrinth.json') as base_file, open(modrinth_file_path) as datapack_file:
            base_json = json.load(base_file)
            datapack_json = json.load(datapack_file)
            modrinth_json = {**base_json, **datapack_json}

        project_id = modrinth_json["project_id"]
        current_version = modrinth_json["version_number"]

        versions = fetch_modrinth_info(project_id)
        if versions is None:
            continue

        latest_version = get_latest_version(versions)
        if latest_version is None or latest_version == current_version:
            print(f"No new version available for project {project_id}. Skipping...")
            continue

        zipped_file_name = f"{datapack_prefix}{datapack_path}_{current_version}.zip"
        dist_dir = os.path.join(full_datapack_path, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        zipped_file_path = os.path.join(dist_dir, zipped_file_name)

        with zipfile.ZipFile(zipped_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(full_datapack_path):
                for file in files:
                    if file != 'modrinth.json' and 'dist' not in root:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), full_datapack_path))

        print(f"Datapack located at: {zipped_file_path}")

        files = {
            'data': (None, json.dumps(modrinth_json), 'application/json'),
            'file': (zipped_file_name, open(zipped_file_path, 'rb'), 'application/zip')
        }
        response = requests.post(modrinth_post_version_route, headers={"Authorization": modrinth_token}, files=files)
        upload_response = response.json()

        if 'error' not in upload_response:
            print(f"Successfully uploaded version {current_version} for {project_id}! Output:\n{upload_response}")
        else:
            print(f"Failed to upload {datapack_path}. Output:\n{upload_response}")

if __name__ == "__main__":
    main()