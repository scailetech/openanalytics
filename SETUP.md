# Setup Guide

## Repository Setup

The GitHub repository should be created at: **https://github.com/federicodeponte/openanalytics**

**Note:** You'll need to create the repository on GitHub first (or it will be created automatically when you push).

## Push to GitHub

To push your code to GitHub, you'll need to authenticate. Here are the options:

### Option 1: Using SSH (Recommended)

1. Set up SSH keys with GitHub if you haven't already
2. Update the remote URL:
   ```bash
   git remote set-url origin git@github.com:federicodeponte/openanalytics.git
   git push -u origin main
   ```

### Option 2: Using HTTPS with Personal Access Token

1. Generate a Personal Access Token (PAT) on GitHub:
   - Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with `repo` scope
   
2. Push using the token:
   ```bash
   git push -u origin main
   # When prompted, use your GitHub username and the PAT as password
   ```

### Option 3: Using GitHub CLI

```bash
gh auth login
git push -u origin main
```

## Next Steps

1. **Push the code** using one of the methods above
2. **Set up Modal secrets** for deployment:
   ```bash
   modal secret create openai-api-key OPENAI_API_KEY=your_key
   modal secret create openrouter-api-key OPENROUTER_API_KEY=your_key
   modal secret create serp-credentials \
     DATAFORSEO_LOGIN=your_login \
     DATAFORSEO_PASSWORD=your_password
   ```
3. **Deploy the services**:
   ```bash
   cd aeo-checks && modal deploy modal_deploy.py
   cd ../pdf-service && modal deploy modal_deploy.py
   ```

## Repository Structure

```
openanalytics/
├── aeo-checks/          # Main AEO analysis service
├── pdf-service/         # PDF generation service
├── reports/             # HTML report generator
├── README.md           # Main documentation
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

## Sharing with Colleagues

Once pushed to GitHub, you can share the repository URL:
**https://github.com/federicodeponte/openanalytics**

They can clone it with:
```bash
git clone https://github.com/federicodeponte/openanalytics.git
```

