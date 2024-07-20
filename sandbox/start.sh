#!/bin/bash
# Bash script to build a sandbox Docker image for buddy using Ubuntu 20.04

# Define image and container names
IMAGE_NAME="buddy_cli"
CONTAINER_NAME="buddy_sandbox"
HASH_FILE="last_image_hash.txt"

# Enable bash strict mode
set -euo pipefail

# The update flag will skip the image build and only update the Python files in the existing container
# WARNING: This will not install new requirements or update the Python environment in any way
if [[ "${1:-}" == "update" ]]; then
    echo "Update mode enabled. Skipping image build..."
    if check_container_existence; then
        if check_container_running; then
            copy_python_files
            echo "Restarting the container..."
            docker restart "$CONTAINER_NAME"
            docker exec -it "$CONTAINER_NAME" /bin/bash
            exit 0
        else
            echo "Container $CONTAINER_NAME exists but is not running. Starting the container..."
            start_container
            copy_python_files
            docker exec -it "$CONTAINER_NAME" /bin/bash
            exit 0
        fi
    else
        echo "Container does not exist, proceeding with regular build and run flow..."
        regular_flow
        exit 0
    fi
else
    regular_flow
    exit 0
fi

# Function for checking whether the sandbox already exists or not
check_container_existence() {
    echo "Checking if container $CONTAINER_NAME exists..."
    docker container inspect "$CONTAINER_NAME" > /dev/null 2>&1 && return 0 || return 1
}

# Function to check if the sandbox is running
check_container_running() {
    echo "Checking if container $CONTAINER_NAME is running..."
    [[ "$(docker inspect --format='{{.State.Running}}' "$CONTAINER_NAME")" == "true" ]] && return 0 || return 1
}

# Function to start the sandbox if it is not running
start_container() {
    echo "Starting container $CONTAINER_NAME..."
    docker start "$CONTAINER_NAME" && return 0 || return 1
}

# Function to copy Python files into the sandbox
copy_python_files() {
    echo "Copying Python files to the existing container..."
    find .. -name "*.py" | while read -r file; do
        relative_path="${file#../}" # remove ../ from the beginning
        if [[ "$relative_path" != *"/venv/"* ]]; then
            echo "Copying file: $file"
            docker_path="/app/${relative_path%/*}" # remove filename, keep directory structure
            docker exec "$CONTAINER_NAME" mkdir -p "$docker_path"
            docker cp "$file" "$CONTAINER_NAME:$docker_path"
        fi
    done
}

# Regular build and run flow
regular_flow() {
    echo "Building the sandbox image..."
    docker build -t "$IMAGE_NAME" -f Dockerfile .. > build_output.txt 2>&1

    echo "Checking if build was successful..."
    if grep -q "exporting layers" build_output.txt; then
        echo "Build successful. Handling containers..."
        if check_container_existence; then
            echo "Stopping and removing existing container..."
            docker stop "$CONTAINER_NAME"
            docker rm "$CONTAINER_NAME"
        fi
        echo "Running a new container..."
        docker run -it --network host --name "$CONTAINER_NAME" "$IMAGE_NAME"
    else
        echo "Build was not successful. Please check the build output for errors."
    fi
    echo "Cleaning up..."
    rm build_output.txt
    echo "Done."
}
