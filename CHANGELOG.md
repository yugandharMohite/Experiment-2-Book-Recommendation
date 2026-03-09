# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and setup
- Nutrition recommendation system with hybrid ML approach
- Gradient Boosting classifier for obesity level prediction (95%+ accuracy)
- KNN collaborative filtering for finding similar users
- Rule-based content recommendation engine
- FastAPI backend with REST endpoints
- Web dashboard with real-time BMI calculator
- GitHub Actions CI/CD pipeline
- Docker containerization
- Comprehensive test suite with pytest
- Documentation and contributing guidelines

### Changed
- None yet

### Fixed
- None yet

### Deprecated
- None yet

### Removed
- None yet

### Security
- None yet

## [1.0.0] - 2026-03-10

### Added
- Initial release
- Nutrition Recommendation System based on UCI Obesity Levels dataset
- Multi-model comparison (Gradient Boosting, Random Forest, MLP, KNN, Logistic Regression)
- 5-fold stratified cross-validation for robust evaluation
- Feature engineering for improved prediction accuracy
- Hybrid recommendation approach combining ML + Collaborative + Content-based filtering
- Personalized nutrition plans for 7 obesity categories
- Interactive web dashboard
- REST API endpoints
- Power BI/Tableau integration support
- Docker support with docker-compose
- GitHub Actions CI/CD

### Performance
- Test Accuracy: 94.78%
- Macro F1 Score: 94.32%
- Weighted F1 Score: 94.81%

---

## Versioning Convention

### Version Format
MAJOR.MINOR.PATCH

- **MAJOR**: Breaking API changes or major feature releases
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes and minor improvements

### Release Process
1. Update CHANGELOG.md
2. Bump version in setup.py and main.py
3. Commit: `git commit -m "Release v1.2.3"`
4. Tag: `git tag -a v1.2.3 -m "Version 1.2.3"`
5. Push: `git push && git push --tags`
6. GitHub Actions builds and publishes Docker image

### Supported Versions
- Latest stable: v1.0.0
- Support window: Latest + 2 previous minor versions

---

## Future Roadmap

### v1.1.0 (Q2 2026)
- [ ] User authentication and personalized recommendations
- [ ] Time-series tracking for weight progress
- [ ] Integration with wearable device APIs
- [ ] Advanced analytics dashboard
- [ ] Mobile app support

### v1.2.0 (Q3 2026)
- [ ] NLP integration for dietary preference understanding
- [ ] Meal plan generation with recipes
- [ ] Integration with food delivery APIs
- [ ] Community features and user forums

### v2.0.0 (Q4 2026)
- [ ] Graph-based recommendation engine
- [ ] Federated learning for privacy-preserving predictions
- [ ] Multi-language support
- [ ] Kubernetes deployment templates

---

## Known Issues

### Current
- None reported

### Resolved
- None yet (first release)

---

## Contributors

See [CONTRIBUTORS.md](./CONTRIBUTORS.md) for full list of contributors.

