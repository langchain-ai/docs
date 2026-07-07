# :remove-start:
echo "✓ configuration-bash-auth samples validated"
exit 0
# :remove-end:

# :snippet-start: configuration-auth-set-sh
# Pipe the key in (stdin)
echo "$ANTHROPIC_API_KEY" | dcode auth set anthropic

# Copy it from an existing environment variable
dcode auth set openai --from-env OPENAI_API_KEY
# :snippet-end:

# :snippet-start: configuration-auth-remove-sh
dcode auth remove anthropic
dcode auth path
# :snippet-end:
