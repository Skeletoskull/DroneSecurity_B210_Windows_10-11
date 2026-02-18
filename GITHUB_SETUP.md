# GitHub Repository Setup Guide

Step-by-step guide to upload this project to GitHub.

## Prerequisites

- GitHub account
- Git installed on your system
- Repository cleaned and ready (this folder)

## Step 1: Create New Repository on GitHub

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name:** `DroneSecurity-B210`
   - **Description:** `Windows port of DroneSecurity with USRP B210 support - DJI DroneID receiver (NDSS 2023)`
   - **Visibility:** Public
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

## Step 2: Initialize Local Repository

Open PowerShell in the "for github" folder:

```powershell
# Navigate to the folder
cd "D:\Drone Classifier\DroneSecurity-public_squash\for github"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Windows port with USRP B210 support"
```

## Step 3: Connect to GitHub

```powershell
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/DroneSecurity-B210.git

# Verify remote
git remote -v
```

## Step 4: Push to GitHub

```powershell
# Push to main branch
git branch -M main
git push -u origin main
```

## Step 5: Configure Repository Settings

### Add Topics (Tags)

Go to repository page → Click "⚙️ Settings" → Add topics:
- `sdr`
- `usrp`
- `b210`
- `dji`
- `droneid`
- `drone-security`
- `gnuradio`
- `windows`
- `signal-processing`
- `ndss2023`

### Enable GitHub Actions

1. Go to "Actions" tab
2. Enable workflows
3. Tests will run automatically on push/PR

### Add Repository Description

Add this to the "About" section:
```
Windows port of DroneSecurity with USRP B210 support - DJI DroneID receiver (NDSS 2023)
```

Website: `https://www.ndss-symposium.org/ndss-paper/drone-security-and-the-mysterious-case-of-djis-droneid/`

### Create Releases

1. Go to "Releases" → "Create a new release"
2. Tag version: `v2.0.0`
3. Release title: `v2.0.0 - USRP B210 Windows Support`
4. Description:
```markdown
## 🎉 Major Release: USRP B210 Support

This release adds full Windows support using USRP B210 via GNU Radio/radioconda.

### ✨ New Features
- USRP B210 support (Windows & Linux)
- GNU Radio/radioconda integration
- Comprehensive testing suite
- Hardware auto-detection
- Spectrum analyzer tool

### 📈 Performance
- 2-3x faster detection vs BladeRF A4
- 50ms frequency settling (vs 100ms)
- Up to 56 MHz sample rate (Linux)

### 📚 Documentation
- Complete Windows setup guide
- Hardware comparison
- Troubleshooting guide

### 🙏 Credits
Based on original research by RUB-SysSec (NDSS 2023)
```

5. Attach sample files if needed
6. Publish release

## Step 6: Update README Badges (Optional)

Add badges to README.md:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/DroneSecurity-B210/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/DroneSecurity-B210/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](https://github.com/YOUR_USERNAME/DroneSecurity-B210)
```

## Step 7: Link to Original Repository

Create a fork relationship:

1. Go to original repo: https://github.com/RUB-SysSec/DroneSecurity
2. Click "Fork" button
3. Or add link in README:
```markdown
**Forked from:** [RUB-SysSec/DroneSecurity](https://github.com/RUB-SysSec/DroneSecurity)
```

## Step 8: Create GitHub Pages (Optional)

For documentation hosting:

1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: `main`, folder: `/docs` (or root)
4. Save

## Recommended Repository Structure

```
DroneSecurity-B210/
├── .github/
│   └── workflows/
│       └── tests.yml          # CI/CD pipeline
├── src/                       # Source code
├── tests/                     # Unit tests
├── samples/                   # Sample captures
├── img/                       # Documentation images
├── .gitignore                 # Git ignore rules
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── README.md                  # Main documentation
├── WINDOWS_SETUP.md           # Windows setup guide
├── QUICKSTART_B210.md         # Quick start guide
├── HARDWARE_COMPARISON.md     # Hardware comparison
├── DRONEID_SIGNAL_PROCESSING.md  # Technical details
└── requirements.txt           # Python dependencies
```

## Maintenance Tips

### Regular Updates

```powershell
# Pull latest changes
git pull origin main

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

### Creating Branches

```powershell
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push branch
git push origin feature/new-feature

# Create Pull Request on GitHub
```

### Tagging Releases

```powershell
# Create tag
git tag -a v2.0.1 -m "Bug fix release"

# Push tag
git push origin v2.0.1
```

## Troubleshooting

**"Permission denied" error:**
```powershell
# Use personal access token instead of password
# Generate token: GitHub → Settings → Developer settings → Personal access tokens
```

**Large files error:**
```powershell
# Remove large files from git history
git rm --cached large_file.raw
git commit -m "Remove large file"
```

**Merge conflicts:**
```powershell
# Pull latest changes
git pull origin main

# Resolve conflicts in files
# ... edit conflicting files ...

# Commit resolution
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

## Next Steps

1. ✅ Create repository on GitHub
2. ✅ Push code
3. ✅ Configure settings
4. ✅ Create first release
5. ✅ Add topics/tags
6. ✅ Enable GitHub Actions
7. 📢 Share with community!

## Support

For GitHub-specific issues:
- [GitHub Docs](https://docs.github.com/)
- [GitHub Community](https://github.community/)

For project issues:
- Open issue on your repository
- Check original repo: https://github.com/RUB-SysSec/DroneSecurity

---

**Ready to upload!** Follow the steps above to publish your repository.
