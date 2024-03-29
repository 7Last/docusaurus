#!/bin/bash

# Update submodules and discard local changes
echo "Updating submodules..."
git submodule update --recursive --remote
output_folder="src/static"
mkdir -p "$output_folder"

# Function to list content of submodule recursively and store in JSON
list_content_to_json() {
    submodule_path="$1"
    output_json="$2"

    # List content of submodule recursively
    content=$(tree --du -h -f -J "$submodule_path" | jq '.[0]')
    # create json object with key content
    echo "$content" > "$output_json"
}

# Iterate through submodules
for submodule in $(git submodule | awk '{print $2}'); do
    # Create directory to store JSON

    # List content of submodule recursively and store in JSON
    list_content_to_json "$submodule" "$output_folder/$submodule.json"
    git add "$output_folder/$submodule.json"
done