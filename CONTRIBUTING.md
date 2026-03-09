# Contributing to Nutrition Recommendation System

We appreciate your interest in contributing! This document provides guidelines and instructions.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- No harassment or discrimination

## 🚀 Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/yourusername/nutrition-recommender.git
cd nutrition-recommender
git remote add upstream https://github.com/original-owner/nutrition-recommender.git
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b fix/bug-description
```

### 3. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for testing/linting
```

## 📝 Coding Standards

### Python Style Guide (PEP 8)
- Use `black` for formatting: `black src/ tests/`
- Use `flake8` for linting: `flake8 src/ tests/`
- Use `mypy` for type checking: `mypy src/`

### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Docstrings
```python
def recommend_nutrition(user_dict: dict) -> dict:
    """
    Generate personalized nutrition recommendation.
    
    Args:
        user_dict: User profile with demographics and eating habits
        
    Returns:
        dict: Nutrition plan with calorie targets and meal suggestions
        
    Raises:
        ValueError: If required fields missing
    """
    pass
```

## 🧪 Testing Requirements

All new features must include tests:

```bash
# Run full test suite
pytest tests/ -v --cov=src

# Run specific test
pytest tests/test_api.py::test_health_check_returns_valid_structure -v

# Test with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests
```python
import pytest
from fastapi.testclient import TestClient

def test_bmi_calculation():
    """Test BMI calculation accuracy."""
    response = client.get("/bmi?height_cm=180&weight_kg=75")
    assert response.status_code == 200
    assert response.json()["bmi"] == 23.15
    assert response.json()["category"] == "Normal Weight"
```

## 📝 Commit Messages

Follow conventional commits:
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, whitespace)
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build process, dependencies

Examples:
```
feat(api): add nutrition recommendation endpoint
fix(model): handle missing BMI values
docs(readme): add deployment instructions
test(classifier): increase coverage to 95%
```

## 🔄 Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes** with meaningful commits

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request** on GitHub with:
   - Clear title and description
   - Link to related issues (`closes #123`)
   - Screenshots for UI changes
   - Test results

5. **PR Template** (auto-fill):
   ```markdown
   ## Description
   Briefly describe the changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows styling guidelines
   - [ ] Comments added for complex logic
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

6. **Review Process**
   - At least 1 maintainer approval required
   - CI/CD pipeline must pass
   - Code coverage must not decrease
   - Address review feedback

## 🐛 Reporting Issues

### Bug Report
```markdown
**Describe the bug:**
Clear description of what went wrong

**To Reproduce:**
Steps to reproduce the issue

**Expected behavior:**
What should have happened

**Environment:**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python: [e.g., 3.12]
- Version: [e.g., 1.2.3]

**Logs/Screenshots:**
Attach relevant error messages
```

### Feature Request
```markdown
**Description:**
Clear description of desired feature

**Use Case:**
Why this feature is needed

**Proposed Solution:**
Your suggested approach (optional)

**Alternatives:**
Other possible approaches
```

## 📚 Documentation

When adding features:
1. Update API docs in `/docs`
2. Add docstrings to functions
3. Update README.md if user-facing
4. Add example usage in docstrings
5. Update CHANGELOG.md

## 🔍 Code Review Checklist

Reviewers will verify:
- ✅ Code follows style guidelines
- ✅ No security vulnerabilities
- ✅ Tests cover new functionality
- ✅ Documentation is accurate
- ✅ Performance impact is acceptable
- ✅ Breaking changes are documented
- ✅ Changelog is updated

## 📦 Release Process

1. Update version in `setup.py` and `__version__.py`
2. Update `CHANGELOG.md`
3. Create Git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions builds and pushes Docker image
6. Create Release on GitHub with changelog

## 🎓 Development Tips

### Local Testing with Docker
```bash
docker build -t nutrition-recommender:dev .
docker run -it -p 8000:8000 -v $(pwd):/app nutrition-recommender:dev
```

### MLflow Experiment Tracking
```bash
mlflow ui  # View at http://localhost:5000
```

### Database Inspection
```bash
python -c "import pandas as pd; df = pd.read_csv('Data/ObesityDataSet_raw_and_data_sinthetic.csv'); print(df.head())"
```

### Performance Profiling
```bash
python -m cProfile -s cumulative train_and_save_model.py
```

## 📞 Getting Help

- **Questions**: Start a GitHub Discussion
- **Documentation**: Check `/docs` folder
- **Examples**: See `/notebooks` folder
- **Slack**: Join our community Slack (link in README)

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- CONTRIBUTORS.md file

Thank you for contributing! 🙌

