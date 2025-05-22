import subprocess
import os
import sys

def run_command(command, error_message):
    """
    Executes a shell command and checks for errors.
    Prints output and exits if the command fails.
    """
    print(f"Executing command: {' '.join(command)}")
    try:
        # Using check=True will raise a CalledProcessError if the command fails
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Command output:")
        print(result.stdout)
        if result.stderr:
            print("Command error output (if any):")
            print(result.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {error_message}")
        print(f"Command failed with exit code {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1) # Exit with a non-zero code to fail the Jenkins build
    except FileNotFoundError:
        print(f"ERROR: Command not found. Make sure '{command[0]}' is in your PATH.")
        sys.exit(1)

def deploy_docker_container(image_name, container_name, port_mapping=None):
    """
    Deploys or updates a Docker container.
    - Pulls the latest image.
    - Stops and removes any existing container with the same name.
    - Runs a new container.
    """
    print(f"--- Starting Docker Deployment for Image: {image_name}, Container: {container_name} ---")

    # 1. Pull the latest Docker image
    print(f"Pulling Docker image: {image_name}...")
    run_command(["docker", "pull", image_name], f"Failed to pull Docker image: {image_name}")

    # 2. Check if container exists and stop/remove it
    print(f"Checking for existing container: {container_name}...")
    container_exists_cmd = ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"]
    try:
        existing_container = subprocess.run(container_exists_cmd, capture_output=True, text=True, check=True)
        if existing_container.stdout.strip() == container_name:
            print(f"Existing container '{container_name}' found. Stopping and removing...")
            run_command(["docker", "stop", container_name], f"Failed to stop container: {container_name}")
            run_command(["docker", "rm", container_name], f"Failed to remove container: {container_name}")
        else:
            print(f"No existing container '{container_name}' found. Proceeding to run.")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not check for existing container. Error: {e.stderr}")
        # We can proceed here, running 'docker run' will create it if it doesn't exist

    # 3. Run the new Docker container
    print(f"Running new Docker container: {container_name} from image: {image_name}...")
    run_command_args = ["docker", "run", "-d", "--name", container_name]

    if port_mapping:
        run_command_args.extend(["-p", port_mapping]) # e.g., "8080:80"

    run_command_args.append(image_name)

    run_command(run_command_args, f"Failed to run Docker container: {container_name}")

    print(f"Successfully deployed Docker container: {container_name}")
    print("--- Docker Deployment Complete ---")

if __name__ == "__main__":
    # Get values from environment variables or provide defaults
    # In Jenkins, you would set these as environment variables in your pipeline
    DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE", "nginx:latest") # Default to nginx
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "my-nginx-app")
    PORT_MAPPING = os.environ.get("PORT_MAPPING", "80:80") # Host_port:Container_port

    print(f"Using DOCKER_IMAGE: {DOCKER_IMAGE}")
    print(f"Using CONTAINER_NAME: {CONTAINER_NAME}")
    print(f"Using PORT_MAPPING: {PORT_MAPPING}")

    deploy_docker_container(DOCKER_IMAGE, CONTAINER_NAME, PORT_MAPPING)
