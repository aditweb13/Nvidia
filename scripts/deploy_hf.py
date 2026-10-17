"""Deploy Cascade to Hugging Face Spaces."""

import os
import sys
from huggingface_hub import HfApi

REPO_NAME = "cascade-nemotron-router"

def main():
    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/{REPO_NAME}"
    print(f"Deploying to Hugging Face Space: {repo_id}")

    # 1. Verify or create Space repository
    try:
        space_url = api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
        )
        print(f"Space created / verified: {space_url}")
    except Exception as e:
        print(f"create_repo notice: {e}")
        try:
            info = api.space_info(repo_id)
            print(f"Space confirmed existing: {info.id}")
        except Exception as check_err:
            print(f"Space {repo_id} was not found on Hugging Face: {check_err}")
            print(f"Please create it at https://huggingface.co/new-space with name '{REPO_NAME}' and SDK 'Docker'.")
            sys.exit(1)

    # 2. Upload directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Uploading files from {root_dir}...")

    ignore_patterns = [
        ".git",
        ".git/*",
        ".gitignore",
        ".env",
        ".env.*",
        "*.env",
        "__pycache__",
        "__pycache__/*",
        "*/__pycache__/*",
        "*.pyc",
        ".pytest_cache",
        ".pytest_cache/*",
        ".ruff_cache",
        ".ruff_cache/*",
        "data/*.db",
        "data/*.sqlite*",
        ".cache",
        ".cache/*",
        "eval/.cache/*",
        ".vscode/*",
        ".idea/*",
    ]

    commit_info = api.upload_folder(
        folder_path=root_dir,
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=ignore_patterns,
        commit_message="deploy: update Cascade router to Hugging Face Spaces",
    )
    print(f"Upload complete! Commit: {commit_info}")
    print(f"Live Space URL: https://huggingface.co/spaces/{repo_id}")

if __name__ == "__main__":
    main()
