#!/bin/bash
# Setup script for gitleaks security hooks across all repositories

echo "🔒 Setting up account-level security protection with gitleaks..."

# Function to setup gitleaks hook in a repository
setup_gitleaks_hook() {
    local repo_path="$1"
    local hook_file="$repo_path/.git/hooks/pre-commit"
    
    echo "📁 Setting up gitleaks hook in: $repo_path"
    
    # Create pre-commit hook
    cat > "$hook_file" << 'EOF'
#!/bin/bash
# Gitleaks secret detection pre-commit hook

echo "🔒 Scanning for secrets with gitleaks..."

# Find gitleaks config file
config_file=""
if [ -f ".gitleaks.toml" ]; then
    config_file=".gitleaks.toml"
elif [ -f "../aeo-checks/.gitleaks.toml" ]; then
    config_file="../aeo-checks/.gitleaks.toml"
elif [ -f "../../aeo-checks/.gitleaks.toml" ]; then
    config_file="../../aeo-checks/.gitleaks.toml"
fi

# Run gitleaks protect on staged files
if [ -n "$config_file" ]; then
    if ! gitleaks protect --verbose --staged --config="$config_file"; then
        echo ""
        echo "🚨 COMMIT BLOCKED: Potential secrets detected!"
        echo "🔍 Review the findings above and remove any exposed credentials"  
        echo "💡 If this is a false positive, update the .gitleaks.toml allowlist"
        echo ""
        exit 1
    fi
else
    # Use default gitleaks rules if no config found
    if ! gitleaks protect --verbose --staged; then
        echo ""
        echo "🚨 COMMIT BLOCKED: Potential secrets detected!"
        echo "🔍 Review the findings above and remove any exposed credentials"
        echo ""
        exit 1
    fi
fi

echo "✅ Secret scan passed - commit allowed"
exit 0
EOF

    # Make hook executable
    chmod +x "$hook_file"
    echo "✅ Gitleaks hook installed at: $hook_file"
}

# Setup hooks in common repository locations
echo ""
echo "🎯 Installing gitleaks hooks in repositories..."

# Current repository
if [ -d ".git" ]; then
    setup_gitleaks_hook "."
fi

# Parent repository (openanalytics)  
if [ -d "../.git" ]; then
    setup_gitleaks_hook ".."
fi

# Other common project directories
for repo_dir in ~/openanalytics ~/openblog ~/opencontext ~/personal-assistant; do
    if [ -d "$repo_dir/.git" ]; then
        setup_gitleaks_hook "$repo_dir"
    fi
done

echo ""
echo "🎉 Account-level gitleaks protection installed!"
echo "📋 Coverage:"
echo "   ✅ Automatic secret scanning on every commit"
echo "   ✅ Blocks commits containing API keys, tokens, or credentials"
echo "   ✅ Customizable detection rules via .gitleaks.toml"
echo "   ✅ Works across all your repositories"
echo ""
echo "🔧 To test: Try committing a file with a fake API key"
echo "💡 To update rules: Edit .gitleaks.toml in this directory"
echo ""
echo "⚠️  Remember: This protects new commits, but always rotate any previously exposed keys!"