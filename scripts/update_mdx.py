import glob


def update_mdx_files():
    # Get all MDX files in the specified directories
    mdx_files = []
    for root in ["oss", "langsmith"]:
        mdx_files.extend(glob.glob(f"{root}/**/*.mdx", recursive=True))

    for file_path in mdx_files:
        try:
            with open(file_path) as f:
                content = f.read()

            # Only add if the placeholder heading is not already present
            if "## Placeholder heading" not in content:
                # Add the placeholder heading and text after the first heading
                if "# " in content:
                    parts = content.split("# ", 1)
                    new_content = (
                        parts[0]
                        + "# "
                        + parts[1]
                        + "\n\n## Placeholder heading\n\nThis is an example"
                    )

                    with open(file_path, "w") as f:
                        f.write(new_content)
                    print(f"Updated {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e!s}")


if __name__ == "__main__":
    update_mdx_files()
