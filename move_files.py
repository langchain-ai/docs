import shutil
from pathlib import Path


def move_files():
    # Define source and destination directories
    src_dirs = ["oss", "langsmith", "langgraph-platform"]
    dest_dir = Path("src")

    # Create destination directories if they don't exist
    for src_dir in src_dirs:
        (dest_dir / src_dir).mkdir(parents=True, exist_ok=True)

    # Move files from each source directory
    for src_dir in src_dirs:
        src_path = Path(src_dir)
        if not src_path.exists():
            print(f"Source directory {src_dir} does not exist")
            continue

        # Walk through the source directory
        for file_path in src_path.rglob("*.mdx"):
            # Calculate relative path from source directory
            rel_path = file_path.relative_to(src_path)
            # Create destination path
            dest_path = dest_dir / src_dir / rel_path
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            # Move the file
            shutil.copy2(file_path, dest_path)
            print(f"Copied {file_path} to {dest_path}")


if __name__ == "__main__":
    move_files()
