#!/bin/bash
# build_and_publish.sh
# Script to build documentation, build the package, and upload to PyPI
# Usage: ./build_and_publish.sh [--no-docs] [--no-build] [--no-upload]

set -e  # Exit immediately if a command exits with a non-zero status

# Default flags
BUILD_DOCS=1
BUILD_PACKAGE=1
UPLOAD_TO_PYPI=1

# Process arguments
for arg in "$@"; do
  case $arg in
    --no-docs)
      BUILD_DOCS=0
      shift
      ;;
    --no-build)
      BUILD_PACKAGE=0
      shift
      ;;
    --no-upload)
      UPLOAD_TO_PYPI=0
      shift
      ;;
    --help)
      echo "Usage: ./build_and_publish.sh [--no-docs] [--no-build] [--no-upload]"
      echo "  --no-docs    Skip building documentation"
      echo "  --no-build   Skip building package"
      echo "  --no-upload  Skip uploading to PyPI"
      exit 0
      ;;
  esac
done

# Check if required tools are installed
check_tool() {
  if ! command -v $1 &> /dev/null; then
    echo "Error: $1 is required but not installed."
    echo "Please install it with: $2"
    exit 1
  fi
}

check_tool python3 "sudo apt install python3"
check_tool pip "sudo apt install python3-pip"

# Make sure we're in the project root
cd "$(dirname "$0")"

echo "========================================"
echo "  Agent Patterns Build & Publish Tool"
echo "========================================"
echo

# Ensure we have the latest dependencies
echo "Installing required dependencies..."
pip install -U pip build twine sphinx mkdocs mkdocs-material mkdocstrings

# Function to handle errors
handle_error() {
  echo "ERROR: $1"
  echo "Aborting."
  exit 1
}

# 1. Build Documentation (if enabled)
if [ $BUILD_DOCS -eq 1 ]; then
  echo
  echo "========================================"
  echo "       Building Documentation"
  echo "========================================"
  
  # Install documentation requirements
  echo "Installing documentation dependencies..."
  if [ -f docs/requirements.txt ]; then
    pip install -r docs/requirements.txt || handle_error "Failed to install documentation dependencies"
  fi
  
  # Check which documentation system to use
  if [ -f mkdocs.yml ]; then
    echo "Building MkDocs documentation..."
    mkdocs build || handle_error "MkDocs build failed"
    echo "MkDocs documentation built successfully in 'site' directory."
  elif [ -f docs/conf.py ]; then
    echo "Building Sphinx documentation..."
    cd docs
    make html || handle_error "Sphinx build failed"
    cd ..
    echo "Sphinx documentation built successfully in 'docs/_build/html' directory."
  else
    handle_error "No documentation configuration found (mkdocs.yml or docs/conf.py)"
  fi
  
  echo "Documentation build completed."
  
  # Don't push to Read the Docs automatically - this happens via webhooks when you push to GitHub
  echo "Note: Documentation will be automatically built on Read the Docs when you push to GitHub."
fi

# 2. Build package (if enabled)
if [ $BUILD_PACKAGE -eq 1 ]; then
  echo
  echo "========================================"
  echo "          Building Package"
  echo "========================================"
  
  # Remove previous builds
  echo "Cleaning previous builds..."
  rm -rf dist build src/*.egg-info
  
  # Build source distribution and wheel
  echo "Building source distribution and wheel..."
  python -m build || handle_error "Failed to build package"
  
  echo "Package built successfully in 'dist' directory."
  ls -l dist/
fi

# 3. Upload to PyPI (if enabled)
if [ $UPLOAD_TO_PYPI -eq 1 ]; then
  echo
  echo "========================================"
  echo "         Uploading to PyPI"
  echo "========================================"
  
  # Check for PyPI credentials
  if [ -z "$TWINE_USERNAME" ] && [ -z "$TWINE_PASSWORD" ]; then
    echo "PyPI credentials not found in environment variables."
    echo "You can set TWINE_USERNAME and TWINE_PASSWORD or use the .pypirc file."
    
    # Ask for confirmation before continuing
    read -p "Continue with PyPI upload? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Upload aborted."
      exit 0
    fi
  fi
  
  # Check if package exists
  if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    handle_error "No distribution files found in 'dist' directory. Run with --build first."
  fi
  
  # Verify distribution files
  echo "Verifying distribution files..."
  twine check dist/* || handle_error "Package verification failed"
  
  # Final confirmation before upload
  echo
  echo "Ready to upload to PyPI."
  read -p "Proceed with upload? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload aborted."
    exit 0
  fi
  
  # Upload to PyPI
  echo "Uploading to PyPI..."
  twine upload dist/* || handle_error "Failed to upload to PyPI"
  
  echo "Package successfully uploaded to PyPI."
fi

echo
echo "========================================"
echo "             All Done!"
echo "========================================"

if [ $BUILD_DOCS -eq 1 ]; then
  echo "✅ Documentation built"
else
  echo "⏭️  Documentation build skipped"
fi

if [ $BUILD_PACKAGE -eq 1 ]; then
  echo "✅ Package built"
else
  echo "⏭️  Package build skipped"
fi

if [ $UPLOAD_TO_PYPI -eq 1 ]; then
  echo "✅ Package uploaded to PyPI"
else
  echo "⏭️  PyPI upload skipped"
fi

echo
echo "Next steps:"
echo "  - Tag this release: git tag -a v$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])") -m 'Release v$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")'"
echo "  - Push tags: git push --tags"
echo "  - Check documentation on Read the Docs: https://agent-patterns.readthedocs.io/"
echo "  - Check package on PyPI: https://pypi.org/project/agent-patterns/" 