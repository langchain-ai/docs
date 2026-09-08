# IDE Setup for Documentation Writers

This repository includes configuration files to ensure consistent formatting across different editors and IDEs used by documentation writers.

Ensure the following steps are taken and configurations are in place before making substantial docs changes.

## Automatic Configuration

### VSCode

If you're using Visual Studio Code, the settings in `.vscode/settings.json` should be automatically applied when you open this project. No additional setup required.

### Other IDEs

Most modern IDEs support EditorConfig. The `.editorconfig` file in the root directory will automatically configure:

- IntelliJ IDEA / PyCharm / WebStorm
- Sublime Text
- Atom
- Vim
- Emacs
- And many others

## Formatting Standards

### Indentation

- **1 tab = 4 spaces** for all files except:
  - JSON files: 2 spaces
  - YAML files: 2 spaces
  - CSS/HTML files: 2 spaces

### Line Length

- **No hard line breaks** for markdown files
- Word wrap is enabled but doesn't insert hard breaks
- Long lines are visually wrapped but remain as single lines in the file

### Line Endings

- **Unix-style line endings** (`\n`) for all files
- Trailing whitespace is automatically trimmed
- Final newline is automatically inserted

### Markdown-Specific Settings

- Preserve trailing spaces in markdown (needed for line breaks)
- No automatic formatting on save
- Word wrap enabled for readability
- No ruler/column guides

## Manual IDE Setup (if needed)

If your IDE doesn't automatically pick up these settings, configure manually:

### General Settings

```text
Tab Size: 4 spaces
Insert Spaces: Yes (not tabs)
Word Wrap: On
Auto Format on Save: Off
Trim Trailing Whitespace: Yes
Insert Final Newline: Yes
```

### Markdown Settings

```text
Word Wrap: On
Hard Line Breaks: Off
Preserve Trailing Spaces: Yes
Max Line Length: Unlimited
```

### Code Examples

```text
Python: 4 spaces
JavaScript/TypeScript: 4 spaces
JSON: 2 spaces
YAML: 2 spaces
```

## VSCode Extensions (Recommended)

For the best writing experience in VSCode, consider installing:

- **EditorConfig for VS Code** - Automatically applies .editorconfig settings
- **markdownlint** - Markdown editing enhancements
- **Markdown All in One** - Markdown editing enhancements
- **MDX** - Syntax highlighting for `.mdx` files
- **Prettier - Code formatter** (disabled for markdown in our settings)

## Why These Settings?

### No Hard Line Breaks

- Allows flexibility in how content is displayed across different devices
- Prevents awkward line breaks when content is edited
- Better for collaborative editing and version control
- Responsive to different screen sizes

### 4 Spaces for Indentation

- Consistent with Python conventions (used in code examples)
- Good readability for nested content
- Standard across most programming languages

### No Auto-Formatting

- Prevents unwanted changes to carefully crafted markdown
- Avoids breaking custom formatting like tables or code blocks
- Gives writers full control over content structure

## Troubleshooting

### VSCode Not Applying Settings

1. Restart VSCode after opening the project
2. Check that you're in the docs folder (not a parent directory)
3. Verify `.vscode/settings.json` exists in the project root

### Other IDEs Not Applying Settings

1. Ensure your IDE supports EditorConfig
2. Install the EditorConfig plugin if needed
3. Check that `.editorconfig` is in the project root
4. Restart your IDE

### Settings Not Working

If automatic configuration isn't working, manually configure your IDE using the settings listed above.
