# Contributing to SecureShell

Thank you for your interest in contributing to SecureShell! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python/Node version, SecureShell version)
- **Code samples** if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear and descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include code examples if applicable

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Make your changes
3. Add tests if applicable
4. Update documentation
5. Ensure tests pass
6. Submit your pull request

## Development Setup

### Python SDK

```bash
# Clone the repository
git clone https://github.com/divagr18/secureshell.git
cd secureshell

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev,test]"

# Run tests
pytest
```

### TypeScript SDK

```bash
# Navigate to TypeScript SDK
cd secureshell-ts

# Install dependencies
npm install

# Build
npm run build

# Run type checking
npm run typecheck
```

## Pull Request Process

1. **Update Documentation**: Ensure README and relevant docs are updated
2. **Add Tests**: New features should include tests
3. **Follow Style Guidelines**: See below
4. **Update CHANGELOG**: Add your changes to the appropriate section
5. **One Feature Per PR**: Keep pull requests focused
6. **Descriptive Commits**: Use clear, descriptive commit messages

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(gatekeeper): add support for custom risk thresholds

Added configuration option to customize risk threshold levels
for different deployment environments.

Closes #123
```

## Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for formatting
- Use type hints where applicable
- Maximum line length: 100 characters
- Write docstrings for all public functions/classes

```python
def evaluate_command(command: str, reasoning: str) -> GatekeeperResponse:
    """
    Evaluate a command for security risks.
    
    Args:
        command: The shell command to evaluate
        reasoning: The agent's reasoning for running the command
        
    Returns:
        GatekeeperResponse with decision and reasoning
    """
    pass
```

### TypeScript

- Follow the existing code style
- Use ESLint configuration
- Use TypeScript strict mode
- Write JSDoc comments for public APIs
- Maximum line length: 100 characters

```typescript
/**
 * Evaluate a command for security risks
 * @param command - The shell command to evaluate
 * @param reasoning - The agent's reasoning for running the command
 * @returns Promise resolving to GatekeeperResponse
 */
async evaluateCommand(command: string, reasoning: string): Promise<GatekeeperResponse> {
    // implementation
}
```

## Adding New LLM Providers

To add support for a new LLM provider:

### Python

1. Create `secureshell/providers/yourprovider.py`
2. Implement `BaseLLMProvider` interface
3. Add configuration in `SecureShellConfig`
4. Add example in `cookbook/providers/`
5. Update documentation

### TypeScript

1. Create `src/providers/yourprovider.ts`
2. Implement `BaseLLMProvider` interface
3. Export from `src/index.ts`
4. Add example in `cookbook/secureshell-ts/providers/`
5. Update documentation

## Testing

### Python

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=secureshell

# Run specific test file
pytest tests/test_gatekeeper.py
```

### TypeScript

```bash
# Run tests (when added)
npm test

# Type checking
npm run typecheck
```

## Documentation

- Update README.md for user-facing changes
- Update API documentation for new features
- Add examples for new functionality
- Keep CHANGELOG.md up to date

## Questions?

Feel free to:
- Open an issue for discussion
- Join our [Discussions](https://github.com/divagr18/secureshell/discussions)
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SecureShell!
