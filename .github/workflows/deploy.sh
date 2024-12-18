#!/bin/bash

datapack_prefix="purpurpack_"
datapack_folder="packs"
modrinth_POST_version_route="https://api.modrinth.com/v2/version"

convert_json_to_query_param() {
    echo $(jq --raw-output '[to_entries[] | (@uri "\(.key)" + "=" + @uri "\(.value)")] | join("&")' <<< $1)
}

modrinth_GET_versions_route() {
    echo "https://api.modrinth.com/v2/project/$1/version"
}

if [ -z "$MODRINTH_TOKEN" ]; then
    echo "The required environment variable MODRINTH_TOKEN is not set."
    exit 1
fi

find "$datapack_folder" -type f -name "modrinth.json" | while read -r modrinth_file_path; do

  datapack_path=$(dirname "$modrinth_file_path")

  echo "modrinth.json found in directory $datapack_path"

    # packs/<datapack> -> <datapack>
    datapack_name=$(cut -d'/' -f2 <<< $datapack_path)

    # continue if the changed files do not include the datapack name
    if [ -z $(jq "map(select(contains(\"${datapack_name}\")))|unique[]" <<< $ALL_CHANGED_FILES) ]; then
        continue
    fi

    echo "Processing $datapack_name..."

    # combine modrinth.json with <datapack>/modrinth.json (datapack file overrides base file values)
    modrinth_json=$(jq --compact-output -s '.[0] * .[1]' modrinth.json "$modrinth_file_path") || {
        echo "Failed to parse JSON for $datapack_path. Skipping...";
        continue;
    }

    echo -e "Output of modrinth_json: \n ${modrinth_json}"

    project_id=$(jq --raw-output '.project_id' <<< "$modrinth_json")
    if [ -z "$project_id" ]; then
        echo "Project ID missing in $datapack_path. Skipping..."
        continue
    fi

    if ! jq empty <<< "$all_versions_curl_output" 2>/dev/null; then
        echo "Invalid JSON response from Modrinth API. Skipping $project_id..."
        continue
    fi

    echo -e "Output of project_id: \n ${project_id}"

    echo -e "Output of 'modrinth_GET_versions_route \$project_id' :\n$(modrinth_GET_versions_route $project_id)"
    echo -e "Output of 'convert_json_to_query_param \$modrinth_json' :\n$(convert_json_to_query_param "$modrinth_json")"


    all_versions_curl_output=$(curl -s -G -H "Authorization: $MODRINTH_TOKEN" $(modrinth_GET_versions_route $project_id) --data $(convert_json_to_query_param "$modrinth_json") 2>&1)
    echo -e "Curl output when attempting to get previous versions...\n${all_versions_curl_output}"
    all_versions_curl_error=$(jq 'try .error catch null' <<< $all_versions_curl_output)
    if [ $all_versions_curl_error != "null" ]; then
        echo -e "Could not retrieve project ${project_id}'s versions. Skipping... Output:\n$(jq <<< $all_versions_curl_output)"
        continue
    fi

    project_version_number=$(jq --raw-output '.version_number' <<< $modrinth_json)
    if [ "null" != $(jq "map(.version_number) | index(\"${project_version_number}\")" <<< $all_versions_curl_output) ]; then
        echo  "A version already exists for project ${project_id}! Skipping..."
        continue
    fi

    zipped_file_name=${datapack_prefix}${datapack_name}_${project_version_number}.zip

    #create a zipped file inside packs/<datapack>/dist/ without including the modrinth.json file & dist/ directory
    (cd "$datapack_path" && mkdir -p dist && zip -r "dist/${zipped_file_name}" . -x dist/ modrinth.json)

    echo "Datapack located at: $(ls ${datapack_path}/dist)"

    echo "curl looks like this:" "curl -s -H \"Authorization: MODRINTH_TOKEN\" -X POST \"$modrinth_POST_version_route\" -F data=$modrinth_json -F file=\"@${datapack_path}/dist/${zipped_file_name}\" 2>&1"

    curl_output=$(curl -s -H "Authorization: $MODRINTH_TOKEN" -X POST "$modrinth_POST_version_route" -F data="$modrinth_json" -F file="@${datapack_path}/dist/${zipped_file_name}" 2>&1)

    echo -e "Curl output when attempting to get post version...\n${curl_output}"

    curl_output_error=$(jq '.error' <<< $curl_output)
    if [ $curl_output_error == "null" ]; then
      echo -e "Successfully uploaded version ${project_version_number} for ${project_id}! Output:\n$(jq <<< $curl_output)"
    else
      echo -e "Failed to upload $datapack_name. Output:\n$(jq <<< $curl_output)"
    fi
done

echo -e "Finished looping through all datapacks."
exit 0
