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

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Deploy your app:**
   - Click "New app"
   - Select your repository: `justins-agent-lead-qualifier`
   - Set the path to your app: `app.py`
   - Click "Deploy"

3. **Set up environment variables:**
   - In your Streamlit Cloud app settings
   - Go to "Secrets" section
   - Add your Google API key:
   ```toml
   GOOGLE_API_KEY = "your_actual_api_key_here"
   ```

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