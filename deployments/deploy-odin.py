"""
This script pulls the specified repository and builds a docker image, 
running it when complete. If there is already a running version, it will be taken
down and replaced with the newly built image.
"""

import subprocess
import os
import sys

# Configuration
REPO_DIR = '/home/david/repos/odin'
BASE_IMAGE_NAME = 'odin'
CONTAINER_NAME = 'odin'
BRANCH_NAME = 'master'
BUILD_NR_FILE = 'odin-build-nr.txt'  # File that stores the build number
VERSION = '0.0.1' # Fallback version in case build-nr file does not exist

def run_command(command, cwd=None):
    """Run a shell command and output the result to the console in real time."""
    print(f"Executing: {command}")
    
    with subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        # Iterate over the output line by line
        for stdout_line in iter(process.stdout.readline, ""):
            print(stdout_line, end="")  # Print output in real-time
        process.stdout.close()
        
        stderr_output = process.stderr.read()  # Read any remaining error output
        if stderr_output:
            print(stderr_output, end="")

        return_code = process.wait()  # Wait for the process to finish
        if return_code != 0:
            print(f"Error: Command exited with code {return_code}")
#            sys.exit(return_code)i

def pull_from_git():
    print("Pulling the latest changes from Git...")
    run_command(f"git pull origin {BRANCH_NAME}", cwd=REPO_DIR)

def build_docker_image(image_name):
    print("Building the Docker image...")
    run_command(f"docker build -t {image_name} {REPO_DIR}")

def stop_and_remove_container():
    print(f"Stopping the running container '{CONTAINER_NAME}' (if it exists)...")
    run_command(f"docker stop {CONTAINER_NAME}", cwd=REPO_DIR)

    print(f"Removing the stopped container '{CONTAINER_NAME}' (if it exists)...")
    run_command(f"docker rm {CONTAINER_NAME}", cwd=REPO_DIR)

def start_new_container(image_name):
    print(f"Starting a new container '{CONTAINER_NAME}' with the image '{image_name}'...")
    run_command(f"docker run -d -p 8014:8080 -e ODIN_CONN_STRING=$ODIN_CONN_STRING --name {CONTAINER_NAME} {image_name}")

def read_version():
    """Read the current version number from the build-nr.txt file."""
    if os.path.exists(BUILD_NR_FILE):
        with open(BUILD_NR_FILE, 'r') as f:
            return f.read().strip()
    return VERSION

def write_version(version):
    """Write the new version number to the build-nr.txt file."""
    with open(BUILD_NR_FILE, 'w') as f:
        f.write(str(version))

def main():
    print("Starting the deployment process...")
    
    # Read and increment the version number
    version = read_version();
    versionParams = version.split('.');
    versionParams[2] = int(versionParams[2]) + 1
    version = '.'.join(str(i) for i in versionParams);
    VERSION = version;
    write_version(version)

    # Create the image name with the version number
    image_name = f"{BASE_IMAGE_NAME}:v{version}"

    pull_from_git()
    build_docker_image(image_name)
    stop_and_remove_container()
    start_new_container(image_name)
    
    print(f"Deployment completed successfully with image: {image_name}")

if __name__ == "__main__":
    main()

