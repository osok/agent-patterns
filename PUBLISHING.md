# Publishing to PyPI Guide

This guide explains how to publish the `agent-patterns` package to PyPI.

## Prerequisites

1. **GitHub Repository**: https://github.com/osok/agent-patterns
2. **PyPI Account**: Create an account at https://pypi.org
3. **PyPI Trusted Publishing**: Configure on PyPI (recommended method)

## Method 1: Trusted Publishing (Recommended)

This method uses GitHub Actions with OIDC (OpenID Connect) for secure, token-free publishing.

### Step 1: Configure PyPI Trusted Publishing

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `agent-patterns`
   - **Owner**: `osok`
   - **Repository name**: `agent-patterns`
   - **Workflow name**: `pypi.yaml`
   - **Environment name**: `pypi`
4. Click "Add"

### Step 2: Create a GitHub Release

1. Go to your repository: https://github.com/osok/agent-patterns
2. Click "Releases" → "Create a new release"
3. Create a new tag: `v0.2.0`
4. Release title: `v0.2.0`
5. Description: Add release notes (see template below)
6. Click "Publish release"

The GitHub Action will automatically:
- Build the package
- Run checks
- Publish to PyPI

### Release Notes Template

```markdown
## Agent Patterns v0.2.0

### 🎉 New Features

- **Flexible Prompt Customization**: Three powerful ways to customize prompts
  - File-based customization with custom `prompt_dir`
  - `custom_instructions` parameter for domain-specific guidelines
  - `prompt_overrides` for programmatic prompt replacement

### ✨ Improvements

- All 9 agent patterns support new customization parameters
- Comprehensive documentation with examples
- Enhanced type safety throughout

### 📚 Documentation

- New [Prompt Customization Guide](docs/PROMPT_CUSTOMIZATION.md)
- 13 comprehensive examples demonstrating customization
- Updated README with installation from PyPI

### 🐛 Bug Fixes

- Fixed prompt dict key consistency across all patterns
- Improved error handling in prompt loading

### 📦 Patterns Included

- ReAct (Reason + Act)
- Plan & Solve
- Reflection
- Reflexion
- LLM Compiler
- REWOO
- LATS
- Self-Discovery
- STORM
```

## Method 2: Manual Publishing (Alternative)

If you prefer to publish manually using API tokens:

### Step 1: Create PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Scope: "Entire account" or specific to "agent-patterns" project
4. Copy the token (starts with `pypi-`)

### Step 2: Build and Publish

```bash
# Install build tools
pip install --upgrade build twine

# Build the distribution
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

When prompted, enter:
- Username: `__token__`
- Password: (paste your API token)

## Testing Before Publishing

### Test on TestPyPI

1. Configure TestPyPI trusted publishing (same as PyPI but at https://test.pypi.org)
2. Manually trigger the workflow to publish to TestPyPI:
   - Go to Actions → "Publish to PyPI" → "Run workflow"
3. Install and test:

```bash
pip install --index-url https://test.pypi.org/simple/ agent-patterns
```

### Local Testing

```bash
# Build the package
python -m build

# Install locally
pip install dist/agent_patterns-0.2.0-py3-none-any.whl

# Test imports
python -c "from agent_patterns.patterns import SelfDiscoveryAgent; print('Success!')"
```

## Version Bumping

To release a new version:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.3.0"
   ```

2. Commit the change:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.3.0"
   git push
   ```

3. Create a new release on GitHub with tag `v0.3.0`

## Workflow Details

The GitHub Actions workflow (`.github/workflows/pypi.yaml`) does the following:

### On Release:
1. **Build Job**:
   - Checks out code
   - Sets up Python 3.10
   - Installs build dependencies
   - Builds source distribution and wheel
   - Runs `twine check` to verify
   - Uploads artifacts

2. **Publish to PyPI Job**:
   - Downloads build artifacts
   - Uses trusted publishing to upload to PyPI
   - Requires the "pypi" environment

### On Manual Trigger:
- Same as above, but also publishes to TestPyPI

## Troubleshooting

### Error: "Project name already exists"
- The project name `agent-patterns` must be unique on PyPI
- If taken, choose a different name in `pyproject.toml`

### Error: "Invalid or non-existent authentication information"
- Verify trusted publishing is configured correctly on PyPI
- Check that repository name, owner, and workflow name match exactly

### Error: "Filename has already been used"
- You're trying to upload a version that already exists
- Bump the version number in `pyproject.toml`

### Workflow fails with permission error
- Ensure the workflow has `id-token: write` permission
- This is required for trusted publishing

### Package missing prompt files
- Check that `MANIFEST.in` includes prompt templates
- Verify with: `python -m build && tar -tzf dist/agent-patterns-*.tar.gz | grep prompts`

## Security Best Practices

1. **Use Trusted Publishing**: Avoid storing API tokens in GitHub Secrets
2. **Use Environments**: Protect the "pypi" environment in GitHub settings
3. **Review Releases**: Always review what you're publishing before creating a release
4. **Test First**: Use TestPyPI before publishing to production PyPI

## Monitoring

After publishing:

1. Check PyPI: https://pypi.org/project/agent-patterns/
2. Verify installation: `pip install agent-patterns`
3. Check download stats: https://pypistats.org/packages/agent-patterns

## Rollback

If you need to remove a version:

1. You cannot delete a version from PyPI
2. You can "yank" a version to hide it: https://pypi.org/project/agent-patterns/
3. Best practice: Publish a patch version with fixes

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions for PyPI](https://github.com/marketplace/actions/pypi-publish)

---

**Current Version**: 0.2.0
**Last Updated**: 2025-10-26
