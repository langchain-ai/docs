# :remove-start:
echo "✓ configuration-bash-cli samples validated"
exit 0
# :remove-end:

# :snippet-start: configuration-profile-override-sh
dcode --profile-override '{"max_input_tokens": 4096}'

# Combine with --model
dcode --model google_genai:gemini-3.5-flash --profile-override '{"max_input_tokens": 4096}'

# In non-interactive mode
dcode -n "Summarize this repo" --profile-override '{"max_input_tokens": 4096}'
# :snippet-end:

# :snippet-start: configuration-install-package-sh
dcode --install my_package --package
# :snippet-end:

# :snippet-start: configuration-doctor-sh
# Show diagnostics in the terminal
dcode doctor
# :snippet-end:
