import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Scan this directory for all *.Dockerfile files
dockerfiles = [f for f in os.listdir("./environments") if f.endswith(".Dockerfile")]

# Create a dictionary of each Dockerfile by its OS, and then sub dictionaries by "root" and "user" variants
dockerfile_dict = {}

for dockerfile in dockerfiles:
    parts = dockerfile.split("_")
    os_name = parts[0]
    variant = parts[1].split(".")[0]

    if os_name not in dockerfile_dict:
        dockerfile_dict[os_name] = {}

    dockerfile_dict[os_name][variant] = f"environments/{dockerfile}"

    
def get_operating_system_environments():
    """
    Get a list of available operating system environments.
    """
    return list(dockerfile_dict.keys())


def run_docker_build(command):
    """
    Run Docker build command with real-time output.
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc


def get_local_dockerfile_path(os_name, variant):
    """
    Get the local path of the Dockerfile for the specified operating system and variant.
    
    Args:
        os_name (str): The operating system
        variant (str): The variant of the Dockerfile
    
    Returns:
        str: The local path of the Dockerfile
    """
    return dockerfile_dict[os_name][variant]


def get_available_environments():
    """
    Print the available operating system environments.
    """
    
    environments = get_operating_system_environments()
    return "\n".join(environments)


def run_command(command, shell=False, display_output=False):
    """
    Run a shell command and return the output.
    
    Args:
        command (str): The command to run
        shell (bool): Whether to run the command in a shell
        display_output (bool): Whether to display the output of the command in real-time
        
    Returns:
        str: The output of the command
    """
    
    if display_output:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_iter = iter(proc.stdout.readline, '')
        stderr_iter = iter(proc.stderr.readline, '')
            
        for stdout_line in stdout_iter:
            if display_output:
                print(stdout_line.strip())
        
        for stderr_line in stderr_iter:
            if display_output:
                print(stderr_line.strip())

        proc.stdout.close()
        proc.stderr.close()
        proc.wait()
        return None
    else:
        proc = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0 and display_output:
            print(f"Error running command: {command}\n{proc.stderr}")
            sys.exit(1)
        return proc.stdout.strip()


def copy_file_to_container(container_id, local_path, container_path):
    target_subdir = os.path.dirname(container_path)
    
    # Check if the contents are different by reading
    local_contents = open(local_path, "r").read()
    container_contents = run_command(f"docker exec {container_id} cat {container_path}", shell=True, display_output=False)
    
    if "No such file or directory" not in container_contents and local_contents.strip() == container_contents.strip():
        return
    
    print(f"Copying {local_path} to {container_path}...")
    run_command(f"docker exec {container_id} mkdir -p {target_subdir}")
    run_command(f"docker cp {local_path} {container_id}:{container_path}")

    if "requirements.txt" in local_path:
        print("Updating Python dependencies...")
        run_command(f"docker exec {container_id} pip install -r {container_path}")


def copy_files_to_container(container_id):
    """
    Copy files from the local source directory to the container in parallel.
    
    Args:
        container_id (str): The ID of the container to copy files to
    """
    
    # Define the local source directory and the target directory inside the container
    src_dir = os.path.abspath("../src")
    target_dir = "/app/"
    
    # List of tasks for parallel execution
    tasks = []

    # Walk through the local source directory and prepare copy tasks
    for root, _, files in os.walk(src_dir):
        # Make sure it's not evenv
        if any(substring in root for substring in ["venv", ".git", "sandbox"]):
            continue
        
        for file in files:
            if ".py" not in file and file != "requirements.txt":
                continue
            
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, src_dir)
            container_path = os.path.join(target_dir, relative_path)
            
            container_path = container_path.replace("\\", "/")
            
            # Append tuple of arguments for the copy operation
            tasks.append((container_id, local_path, container_path))

    # Execute copy tasks in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: copy_file_to_container(*args), tasks)


def main(update=False, open_existing=False, os_name="ubuntu", is_root=False):
    container_name = f"buddy_sandbox_{os_name}_{'root' if is_root else 'user'}"
    container_id = run_command(f"docker ps -aq --filter name={container_name}", shell=True)
    dockerfile_path = get_local_dockerfile_path(os_name, "root" if is_root else "user")

    if update:
        if not container_id:
            print("Error: Existing sandbox not found. Can't run the update procedure.")
            sys.exit(1)

        print("Uploading files and restarting the sandbox...")

        # Ensure the container is running
        status = run_command(f"docker inspect -f '{{{{.State.Status}}}}' {container_id}", shell=True)
        if status != "running":
            run_command(f"docker start {container_id}", shell=True)

        # Copy files to the running container
        copy_files_to_container(container_id)

        # Restart the container
        run_command(f"docker restart {container_id}", shell=True)
        print("Sandbox updated and restarted.")
        
        # Attach to /bin/bash
        subprocess.run(f"docker exec -it {container_id} /bin/bash", shell=True)
    elif open_existing:
        if not container_id:
            print(f"Error: Existing {os_name} sandbox not found. Can't open the sandbox. Run without any flags to build a new environment.")
            sys.exit(1)
            
        # Make sure its running
        status = run_command(f"docker inspect -f '{{.State.Status}}' {container_id}", shell=True)
        if status != "running":
            print(f"Starting the existing {os_name} sandbox...")
            run_command(f"docker start -d {container_id}", shell=True)

        print("Attaching to the existing sandbox container...")
        subprocess.run(f"docker exec -it {container_id} /bin/bash", shell=True)
    else:
        print(f"Building a new {os_name} sandbox environment...")
        
        # Build a new Docker image
        run_docker_build(f"docker build -t {container_name} -f {dockerfile_path} ../src --progress=plain")

        # Remove existing container if it exists
        if container_id:
            print("Removing existing sandbox container...")
            run_command(f"docker rm -f {container_id}", shell=True)

        # Run a new container
        print(f"Starting the new {os_name} sandbox container...")
        subprocess.run(f"docker run -it --name {container_name} {container_name} /bin/bash", shell=True)


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(f"""
Usage: python start_sandbox.py [--update] [--open] [--os <os>] [--root]

Defaults:
    os: ubuntu
    root: False

Options:
    --update: Update the existing sandbox environment with the latest files, don't rebuild the environment
    --open: Attach to the existing sandbox container without rebuilding the environment
    --os: Specify the operating system environment to use
    --root: Use the root variant of the environment
    
Available operating system environments:
{get_available_environments()}
    
If no options are provided, a new sandbox environment will be built.
""")
        sys.exit(0)
    
    update_flag = "--update" in sys.argv
    open_flag = "--open" in sys.argv
    os_flag = "--os" in sys.argv
    root_flag = "--root" in sys.argv
    
    if os_flag:
        os_index = sys.argv.index("--os")
        os_name = sys.argv[os_index + 1]
    
    main(update=update_flag, open_existing=open_flag, os_name=os_name, is_root=root_flag)
