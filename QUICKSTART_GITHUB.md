# GitHub Quick Start Checklist

Complete this checklist to push your project to GitHub.

## ✅ Pre-GitHub Setup (Local Machine)

- [ ] All files committed locally (`git status` shows clean)
- [ ] `.env` file created from `.env.example` (NOT committed)
- [ ] `models/nutrition_model.pkl` trained and exists
- [ ] Tests pass locally: `pytest tests/ -v`
- [ ] Docker builds successfully: `docker build -t nutrition-recommender .`
- [ ] git configured: 
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```

## ✅ GitHub Account Setup

- [ ] GitHub account created
- [ ] SSH key configured ([Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh))
  ```bash
  ssh-keygen -t ed25519 -C "your.email@example.com"
  # Add public key to GitHub settings
  ```
- [ ] Verified SSH connection: `ssh -T git@github.com`

## ✅ Create GitHub Repository

- [ ] Login to [github.com](https://github.com)
- [ ] Click **New repository**
- [ ] Repository name: `nutrition-recommender`
- [ ] Description: "Hybrid ML system for personalized nutrition recommendations"
- [ ] Select **Public** (for open-source)
- [ ] **DO NOT** initialize with README (we have one)
- [ ] Click **Create repository**

## ✅ Push to GitHub

```bash
# In your local directory
git remote add origin git@github.com:yourusername/nutrition-recommender.git
git branch -M main
git push -u origin main
```

Or if using HTTPS:
```bash
git remote add origin https://github.com/yourusername/nutrition-recommender.git
git branch -M main
git push -u origin main
```

## ✅ GitHub Settings Configuration

### Branch Protection
1. Settings → Branches
2. Add rule for `main` branch
3. ☑ Require a pull request before merging
4. ☑ Require status checks to pass
5. ☑ Require branches to be up to date

### Actions Secrets
1. Settings → Secrets and variables → Actions
2. **New repository secret**
   - Name: `DOCKER_USERNAME`
   - Value: Your Docker Hub username
3. **New repository secret**
   - Name: `DOCKER_PASSWORD`
   - Value: Your Docker Hub access token (not password!)

Get Docker Hub token:
- [Docker Hub](https://hub.docker.com/) → Account Settings → Security → New Access Token

### Enable GitHub Pages (Optional)
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: `main`
4. Folder: `/docs`
5. Save

## ✅ Update Repository Links

Update these files with your GitHub username:

1. **README.md**
   - Replace `yourusername` with your GitHub username
   - Replace example URLs with your repo URL

2. **setup.py**
   - Update `url` and `author_email`

3. **pyproject.toml**
   - Update `authors` email
   - Update URLs

4. **GITHUB_SETUP_SUMMARY.md**
   - Update all placeholder references

5. **Commit & push changes**
   ```bash
   git add .
   git commit -m "docs: Update repository links and metadata"
   git push
   ```

## ✅ Docker Hub Setup (Optional)

1. Create [Docker Hub](https://hub.docker.com/) account
2. Click **Create repository**
3. Repository name: `nutrition-recommender`
4. Visibility: Public
5. Click **Create**
6. Under "Builds" → Connect GitHub account
7. Select your GitHub repo
8. Build rules: Auto-build on push to main

## ✅ Verify Deployment Pipeline

1. Make a test commit:
   ```bash
   echo "# Test" >> TEST.md
   git add TEST.md
   git commit -m "test: Verify CI/CD pipeline"
   git push
   ```

2. Watch GitHub Actions:
   - Navigate to your repo
   - Click **Actions** tab
   - Click on the workflow run
   - Verify all jobs pass (Test → Build → Deploy)

3. Verify Docker image pushed:
   - Go to Docker Hub
   - Check if image was built and pushed

## ✅ Testing the API

After CI/CD completes successfully:

```bash
# Your API is accessible at:
# http://localhost:8000 (local)
# or your Cloud deployment URL

# Test the health endpoint:
curl http://localhost:8000/health

# Test BMI calculator:
curl "http://localhost:8000/bmi?height_cm=180&weight_kg=75"

# Test recommendation:
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{...user data...}'
```

## ✅ Documentation Setup

- [ ] README.md reviewed and updated
- [ ] `/docs` folder visible in repo
  - [ ] ARCHITECTURE.md
  - [ ] API.md
  - [ ] DEPLOYMENT.md
- [ ] Links in README point to correct files
- [ ] CODE_OF_CONDUCT.md in root

## ✅ First Release

1. Update version in:
   - `setup.py`: `version="1.0.0"`
   - `pyproject.toml`: `version = "1.0.0"`

2. Create git tag:
   ```bash
   git tag -a v1.0.0 -m "Initial release - v1.0.0"
   git push origin v1.0.0
   ```

3. Create GitHub Release:
   - Go to **Releases** tab
   - Click **Create a release**
   - Select tag `v1.0.0`
   - Title: "Version 1.0.0 - Initial Release"
   - Description: Copy from CHANGELOG.md
   - Click **Publish release**

## ✅ Post-Launch Tasks

- [ ] Share on social media
- [ ] Post on Reddit (/r/MachineLearning, /r/Python)
- [ ] Share in Discord/Slack communities
- [ ] Add to awesome-lists (if applicable)
- [ ] Monitor GitHub issues and discussions
- [ ] Welcome first contributors
- [ ] Set up community communication channel

## 📞 Troubleshooting

### Git Push Fails
```bash
# Check remote
git remote -v

# Fix if wrong
git remote remove origin
git remote add origin git@github.com:yourusername/nutrition-recommender.git

# Try again
git push -u origin main
```

### CI/CD Pipeline Fails
1. Check GitHub Actions logs
2. Common issues:
   - Missing Docker credentials (check Secrets)
   - pytest failures (run locally first)
   - Model not found (ensure trained)

### Docker Push Fails
1. Verify Docker Hub credentials in GitHub Secrets
2. Check Docker Hub token hasn't expired
3. Ensure repository is public

## 🎉 Success Checklist

- [ ] Repository visible on GitHub
- [ ] README displays correctly
- [ ] CI/CD pipeline runs automatically
- [ ] Docker image published (if enabled)
- [ ] First release created
- [ ] Documentation accessible
- [ ] Contributors can fork/clone project
- [ ] Issues/Discussions enabled

---

**Congratulations! Your GitHub repository is live! 🚀**

Next: Start accepting contributions and engaging with your community!

