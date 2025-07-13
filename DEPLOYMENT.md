# 🚀 Deployment Guide

## GitHub Repository Setup

1. **Create a new GitHub repository:**
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it: `justins-agent-lead-qualifier`
   - Make it Public (required for Streamlit Cloud free tier)
   - Don't initialize with README (we already have one)

2. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/justins-agent-lead-qualifier.git
   git push -u origin main
   ```

## Streamlit Cloud Deployment

### Step 1: Create New App
1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Deploy your app:**
   - Click "New app"
   - Select your repository: `vihaar/justin-s-whatnot-agent`
   - Set the path to your app: `app.py`
   - Click "Deploy"

### Step 2: Configure Secrets
1. **Get your Google API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key or copy your existing one

2. **Add secrets to Streamlit Cloud:**
   - In your app dashboard, click "Settings" (gear icon)
   - Scroll down to "Secrets" section
   - Click "Edit secrets"
   - Paste this configuration:
   ```toml
   GOOGLE_API_KEY = "your_actual_api_key_here"
   ```
   - Replace `your_actual_api_key_here` with your real API key
   - Click "Save"

### Step 3: Test Your App
- Your app will automatically redeploy with the new secrets
- Visit your app URL and test with a website
- You should see "✅ Orange Slice Agent ready!" in the sidebar



## Environment Variables

The app will automatically load the API key from Streamlit Cloud secrets.

## Custom Domain (Optional)

You can set up a custom domain in Streamlit Cloud settings.

## Troubleshooting

- **API Key Issues**: Make sure your Google API key is valid and has sufficient quota
- **Deployment Errors**: Check the logs in Streamlit Cloud
- **Import Errors**: Ensure all dependencies are in `requirements.txt`

## Security Notes

- Never commit your `.env` file to GitHub
- Use Streamlit Cloud secrets for API keys
- The `.gitignore` file is already configured to exclude sensitive files 