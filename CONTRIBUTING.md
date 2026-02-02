# Contributing to Pocket Agent

Thank you for your interest in contributing to Pocket Agent! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Include details**:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template**
3. **Explain the use case** and why it would be valuable
4. **Provide examples** of how it would work

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add: feature description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with a clear description

## 📝 Code Style

### Python
- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small

### Example
```python
def process_message(message: str, user_id: str) -> dict:
    """Process incoming message and generate response.
    
    Args:
        message: The user's message text
        user_id: Unique identifier for the user
        
    Returns:
        dict: Response containing content and metadata
    """
    # Implementation
    pass
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add support for Trello integration
fix: resolve connection error handling crash
docs: update quick start guide
refactor: simplify error extraction logic
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_kernel.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests
- Add tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Use descriptive test names

```python
def test_connection_error_provides_auth_link():
    """Test that connection errors return auth links instead of crashing."""
    # Test implementation
    pass
```

## 📚 Documentation

### When to Update Docs
- Adding new features
- Changing existing behavior
- Fixing bugs that affect usage
- Adding new integrations

### Documentation Structure
```
docs/
├── QUICK_START_GUIDE.md      # User onboarding
├── PROACTIVE_AGENT_GUIDE.md  # Feature guides
├── SKILLS_SYSTEM_DESIGN.md   # System design
├── development/              # Internal docs
└── archive/                  # Historical docs
```

### Writing Style
- Clear and concise
- Use examples
- Include code snippets
- Add screenshots when helpful

## 🏗️ Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Setup Steps
```bash
# Clone your fork
git clone https://github.com/yourusername/pocket-agent.git
cd pocket-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd wpp-bridge && npm install && cd ..

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

### Running Locally
```bash
# Start the agent
python main_v2.py

# Or use the start script
./start_local.bat  # Windows
./start_local.sh   # Linux/Mac
```

## 🔍 Code Review Process

### What We Look For
- ✅ Code quality and readability
- ✅ Test coverage
- ✅ Documentation updates
- ✅ No breaking changes (or clearly documented)
- ✅ Performance considerations
- ✅ Security best practices

### Review Timeline
- Initial review: Within 3-5 days
- Follow-up reviews: Within 2 days
- Merge: After approval from maintainers

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional integration support (Trello, Linear, etc.)
- [ ] Improved error handling and recovery
- [ ] Performance optimizations
- [ ] Test coverage improvements

### Medium Priority
- [ ] Documentation improvements
- [ ] Example use cases
- [ ] UI/UX enhancements
- [ ] Deployment guides

### Good First Issues
Look for issues labeled `good first issue` - these are great for newcomers!

## 💬 Communication

### Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions

### Response Times
- Issues: We aim to respond within 3-5 days
- PRs: Initial review within 3-5 days
- Questions: Within 1-2 days

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Credited in the CHANGELOG

Thank you for contributing to Pocket Agent! 🚀
