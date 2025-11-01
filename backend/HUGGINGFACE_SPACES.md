# Hugging Face Spaces Deployment Guide

This guide explains how to deploy the RezScan backend to Hugging Face Spaces.

## Prerequisites

- Hugging Face account (free)
- GitHub repository with your code
- Python 3.12 (or compatible version)

## Deployment Steps

### 1. Create a New Space on Hugging Face

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: e.g., `rezscan-backend`
   - **SDK**: Select **"Docker"** (required for Flask applications)
   - **Template**: Select **"Blank"** or any Docker template
   - **Hardware**: Select **"CPU basic"** (free tier, sufficient for this app)
   - **Visibility**: Public or Private

### 2. Configure Space Settings

1. After creating the space, go to **Settings**
2. Under **SDK**, ensure **"Docker"** is selected
3. Set **Space directory** to: `backend/` (if your repo structure has backend in a subdirectory)
   - Or if deploying from root: leave empty

### 3. Dockerfile Configuration

The `Dockerfile` has already been created in the `backend/` directory. It will:

- Install all Python dependencies from `requirements.txt`
- Download the spaCy model (`en_core_web_sm`)
- Run the Flask application via `app.py`

**Note**: The Dockerfile is minimal and straightforward. If you prefer to use Python SDK instead of Docker, you can:

1. Update your `README.md` in the `backend/` directory with Python SDK metadata (already added)
2. Switch the SDK type in Space settings from Docker to Python after creation
3. HF Spaces should automatically detect the Python SDK configuration from the README metadata

### 4. Environment Variables

Set the following in your Space settings (Settings → Repository secrets or Environment variables):

- `FLASK_ENV=production`
- `CORS_ORIGINS=https://your-vercel-frontend.vercel.app` (optional, or leave to allow all origins)
- `PORT` (automatically set by Spaces, default 7860)

### 5. Clone and Setup the Space Repository

**IMPORTANT**: Clone the Space repository in a **separate location** (outside your current project directory). This prevents git conflicts.

**Recommended approach:**

1. **Navigate to parent directory** (one level up from your current project):

   ```bash
   # From your current project directory (rezscan)
   cd ..
   # Now you're in the parent directory (e.g., C:\D\Programming\Projects)
   ```

2. **Clone the Space repository:**

   ```bash
   # Clone the Space repository
   # Use an access token as git password when prompted
   # Generate one from: https://huggingface.co/settings/tokens
   git clone https://huggingface.co/spaces/Pranay1002x2/rezscan-backend1

   cd rezscan-backend1
   ```

**Note**: On Windows PowerShell, you may need to install the HF CLI:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"
```

### 6. Copy Your Backend Code

Copy your backend code from your project to the cloned Space repository:

**On Windows (PowerShell):**

```powershell
# From the Space repository directory (rezscan-backend1)
# Copy all files from your project's backend folder
Copy-Item -Path "..\rezscan\backend\*" -Destination "." -Recurse -Force
```

**On Windows (CMD):**

```cmd
xcopy ..\rezscan\backend\* . /E /I /Y
```

**On Linux/Mac:**

```bash
# From the Space repository directory
cp -r ../rezscan/backend/* .
```

**Files that should be in the Space repository:**

- `app.py`
- `Dockerfile`
- `requirements.txt`
- `api/` directory (entire folder)
- `app/` directory (entire folder with all services)
- `models/` directory (if it exists)
- `README.md` (optional)

### 7. Commit and Push

```bash
cd rezscan-backend

# Add all files
git add .

# Commit changes
git commit -m "Add RezScan backend application"

# Push to deploy
git push
```

**Important**:

- HF Spaces requires your app to listen on **port 7860**
- The Dockerfile already configures this correctly
- The app will automatically build and deploy after pushing

### 8. Get Your Space URL

After deployment, your Space will be available at:

```
https://your-username-rezscan-backend.hf.space
```

The build process may take several minutes due to ML dependencies (spaCy, torch, sentence-transformers).

### 9. Update Vercel Frontend

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add new variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-username-rezscan-backend.hf.space`
4. Save and redeploy your frontend (or wait for auto-deploy)

## File Structure for HF Spaces

Your `backend/` directory should contain:

```
backend/
├── app.py                 # Entry point for HF Spaces (already created)
├── Dockerfile            # Docker configuration for deployment (already created)
├── api/
│   └── main.py           # Flask application
├── app/
│   └── services/         # Service modules
├── requirements.txt      # Python dependencies
└── README.md            # Space metadata (includes Python SDK config if needed)
```

## Important Notes

1. **Port Configuration**: HF Spaces uses port 7860 by default, but the app already reads from `PORT` env var
2. **Memory**: Free tier provides ~2GB RAM, which is sufficient for spaCy (400MB) + ML models
3. **CORS**: Configure `CORS_ORIGINS` env var in Space settings to restrict access to your Vercel frontend
4. **Uploads Folder**: The `uploads/` directory is created automatically and is writable
5. **HTTPS**: HF Spaces automatically provides HTTPS for your Space URL

## Troubleshooting

- **Build fails**: Check that all dependencies are in `requirements.txt`
- **spaCy model not found**: Ensure `python -m spacy download en_core_web_sm` runs during build
- **CORS errors**: Update `CORS_ORIGINS` environment variable in Space settings
- **Memory issues**: Upgrade to a paid tier or optimize model loading

## Testing Your Deployment

1. Test health endpoint: `https://your-space-url.hf.space/api/health`
2. Test from frontend: Ensure your Vercel frontend can connect to the backend
3. Test file upload: Try uploading a job description and resume via the frontend
