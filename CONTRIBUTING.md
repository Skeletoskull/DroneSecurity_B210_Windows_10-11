# Contributing to DroneSecurity-B210

Thank you for your interest in contributing! This project is a research tool for educational purposes.

## How to Contribute

### Reporting Issues

When reporting issues, please include:
- Operating system and version
- SDR hardware model (USRP B210, BladeRF A4, etc.)
- Python version
- Complete error message
- Steps to reproduce

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to functions
- Include type hints where appropriate
- Keep functions focused and modular

### Testing

Run tests before submitting:
```bash
pytest tests/
```

Add tests for new features:
```python
# tests/test_your_feature.py
def test_your_feature():
    assert your_function() == expected_result
```

### Areas for Contribution

**High Priority:**
- Bug fixes
- Documentation improvements
- Windows compatibility issues
- Performance optimizations

**Medium Priority:**
- Additional SDR hardware support
- GUI improvements
- Better error handling

**Low Priority:**
- New features (discuss first in issues)
- Code refactoring

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DroneSecurity-B210.git
cd DroneSecurity-B210

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
pytest tests/
```

## Questions?

Open an issue for discussion before starting major work.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
