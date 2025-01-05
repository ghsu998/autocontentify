import os
import subprocess
from config.common import setup_logger  # Import setup_logger from common.py

# Initialize logger using common.py's setup_logger
logger = setup_logger(script_name="update_and_push")

def update_requirements_and_push():
    """
    Updates requirements.txt and pushes the changes to a Git repository.
    """
    try:
        # Define the path to the Git repository
        git_repo_dir = "/Users/gary/Documents/GitHub/AutoContentify"

        # Change to the Git repository directory
        os.chdir(git_repo_dir)

        # Define the path for requirements.txt
        requirements_path = os.path.join(git_repo_dir, "requirements.txt")

        # Step 1: Update requirements.txt
        logger.info("Updating requirements.txt...")
        with open(requirements_path, "w") as requirements_file:
            subprocess.run(["pip", "freeze"], stdout=requirements_file, check=True)
        logger.info(f"✅ Successfully updated {requirements_path}")

        # Step 2: Check if requirements.txt has changes
        logger.info("Checking for changes in requirements.txt...")
        result = subprocess.run(["git", "diff", "--exit-code", "requirements.txt"], capture_output=True)
        if result.returncode == 0:
            logger.warning("⚠️ No changes detected in requirements.txt. Skipping commit and push.")
            return

        # Step 3: Add requirements.txt to Git staging
        logger.info("Staging requirements.txt for Git...")
        subprocess.run(["git", "add", "requirements.txt"], check=True)

        # Step 4: Commit the change
        logger.info("Committing the changes...")
        subprocess.run(["git", "commit", "-m", "Update requirements.txt"], check=True)

        # Step 5: Push the changes
        logger.info("Pushing changes to the remote repository...")
        subprocess.run(["git", "push"], check=True)

        logger.info("✅ Successfully updated requirements.txt and pushed changes to Git!")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error during subprocess execution: {e}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    update_requirements_and_push()
