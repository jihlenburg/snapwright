# Contributing to SnapWright

Thank you for your interest in contributing to SnapWright! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/jihlenburg/snapwright/issues)
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, playwright version)
   - Minimal code example

### Suggesting Features

1. Check existing issues and discussions
2. Open a new issue with `[Feature Request]` prefix
3. Describe the problem you're trying to solve
4. Propose your solution
5. Consider alternatives

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add/update tests
5. Update documentation
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

#### Pull Request Guidelines

- Keep changes focused and atomic
- Follow existing code style
- Add tests for new functionality
- Update documentation
- Ensure all tests pass
- Keep commits clean and descriptive

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/jihlenburg/snapwright.git
cd snapwright
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
playwright install chromium
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

Run tests with:
```bash
pytest
```

With coverage:
```bash
pytest --cov=snapwright --cov-report=html
```

Run specific tests:
```bash
pytest tests/test_core.py::test_screenshot
```

## Code Style

We use:
- [Black](https://github.com/psf/black) for code formatting
- [Flake8](https://flake8.pycqa.org/) for linting
- [mypy](http://mypy-lang.org/) for type checking

Format code:
```bash
black src tests
```

Lint code:
```bash
flake8 src tests
mypy src
```

## Documentation

- Use clear, descriptive variable names
- Add docstrings to all public functions
- Include type hints
- Provide examples in docstrings
- Update README.md for significant changes

### Docstring Example

```python
def capture_screenshot(
    url: str,
    output_path: Optional[Path] = None,
    full_page: bool = True
) -> Optional[Path]:
    """
    Capture a screenshot of a website.
    
    Args:
        url: The URL to capture
        output_path: Where to save the screenshot
        full_page: Whether to capture the full page
        
    Returns:
        Path to the screenshot file, or None if failed
        
    Examples:
        >>> screenshot("https://example.com")
        PosixPath('screenshots/screenshot_1234567890.png')
        
        >>> screenshot("https://example.com", "my_screenshot.png")
        PosixPath('screenshots/my_screenshot.png')
    """
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a PR with version bump
4. After merge, tag the release
5. GitHub Actions will publish to PyPI

## Getting Help

- Check documentation
- Search existing issues
- Ask in discussions
- Join our community chat (if applicable)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Thank you for contributing!