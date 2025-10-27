# Agent Patterns User Documentation

This directory contains the complete user documentation for the **agent-patterns** Python library.

## Documentation Structure

```
usr-docs/
├── index.md                 # Main documentation index
├── installation.md          # Installation guide
├── quickstart.md            # 5-minute tutorial
├── faq.md                   # Frequently asked questions
├── troubleshooting.md       # Common issues and solutions
├── changelog.md             # Version history
├── contributing.md          # Contribution guidelines
│
├── concepts/               # Core concepts
│   ├── what-are-patterns.md
│   └── architecture.md
│
├── patterns/               # Agent pattern documentation
│   ├── choosing-a-pattern.md
│   ├── comparison-matrix.md
│   ├── react.md
│   ├── reflection.md
│   ├── self-discovery.md
│   ├── storm.md
│   ├── plan-and-solve.md
│   ├── reflexion.md
│   ├── rewoo.md
│   ├── lats.md
│   └── llm-compiler.md
│
├── guides/                 # How-to guides
│   ├── prompt-customization.md
│   ├── custom-instructions.md
│   ├── prompt-overrides.md
│   ├── setting-goals.md
│   ├── configuration.md
│   ├── error-handling.md
│   ├── testing.md
│   ├── deployment.md
│   ├── extending-patterns.md
│   └── best-practices.md
│
├── api/                    # API reference
│   ├── index.md
│   ├── base-agent.md
│   ├── patterns.md
│   └── types.md
│
└── examples/               # Example code
    └── index.md
```

## Building Documentation Locally

### Prerequisites

```bash
pip install -r requirements.txt
```

### Build HTML

```bash
# From the project root
cd usr-docs
sphinx-build -b html . _build/html
```

### View Documentation

```bash
# Open in browser (macOS)
open _build/html/index.html

# Open in browser (Linux)
xdg-open _build/html/index.html

# Open in browser (Windows)
start _build/html/index.html
```

### Build PDF

```bash
sphinx-build -b latex . _build/latex
cd _build/latex
make
```

## Development

### Auto-rebuild on Changes

```bash
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

Then open http://127.0.0.1:8000 in your browser.

### Checking Links

```bash
sphinx-build -b linkcheck . _build/linkcheck
```

## Read the Docs

This documentation is configured for automatic builds on Read the Docs via `.readthedocs.yaml` in the project root.

### Publishing to Read the Docs

1. Go to https://readthedocs.org/
2. Import the GitHub repository: `osok/agent-patterns`
3. The configuration in `.readthedocs.yaml` will be used automatically

### Manual Build Trigger

Builds are triggered automatically on:
- Push to main branch
- Pull requests
- New tags/releases

## Documentation Standards

### Markdown Format

- Use MyST Markdown syntax
- Code blocks with language tags
- Admonitions for notes/warnings
- Cross-references with proper links

### Code Examples

All code examples should:
- Be complete and runnable
- Include necessary imports
- Show expected output
- Follow library best practices

### Cross-References

Link to related documentation:
```markdown
See [Pattern Comparison](patterns/comparison-matrix.md)
See [API Reference](api/index.md)
```

### Admonitions

Use admonitions for important information:

```markdown
```{note}
This is a helpful note
```

```{warning}
This is a warning
```

```{tip}
This is a tip
```
```

## Contributing to Documentation

1. **Edit Markdown files** in this directory
2. **Build locally** to verify changes
3. **Submit PR** with documentation updates

See [contributing.md](contributing.md) for detailed guidelines.

## Documentation Coverage

### Patterns
- ✅ All 9 patterns documented
- ✅ Complete API reference for each
- ✅ Usage examples for each
- ✅ Comparison matrix
- ✅ Pattern selection guide

### Guides
- ✅ Prompt customization (all 3 methods)
- ✅ Configuration and setup
- ✅ Error handling
- ✅ Testing strategies
- ✅ Deployment guide
- ✅ Best practices

### API Reference
- ✅ BaseAgent complete reference
- ✅ All pattern APIs
- ✅ Type definitions
- ✅ Common parameters

### Getting Started
- ✅ Installation guide
- ✅ Quick start tutorial
- ✅ Core concepts
- ✅ Architecture overview

### Support
- ✅ FAQ (30+ questions)
- ✅ Troubleshooting guide
- ✅ Examples index
- ✅ Contribution guide

## Quick Links

- **Read the Docs**: https://agent-patterns.readthedocs.io/ (once published)
- **GitHub**: https://github.com/osok/agent-patterns
- **PyPI**: https://pypi.org/project/agent-patterns/
- **Issues**: https://github.com/osok/agent-patterns/issues

## Documentation Statistics

- **Total pages**: 35+
- **Total size**: ~500KB markdown
- **Code examples**: 200+
- **Pattern docs**: 9 (one per pattern)
- **Guide docs**: 10
- **API docs**: 4
- **Support docs**: 7

## License

Documentation is part of the agent-patterns project and is licensed under the MIT License.
