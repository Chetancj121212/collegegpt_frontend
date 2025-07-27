# Render Deployment Guide for College Bot Backend

## Prerequisites
1. A Render account (https://render.com)
2. Your backend code pushed to a GitHub repository
3. Required API keys and connection strings

## Deployment Steps

### 1. Create a New Web Service on Render

1. Go to your Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your backend code

### 2. Configure the Service

**Basic Settings:**
- **Name**: `college-bot-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend` (if your backend is in a subdirectory)

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

In the Render dashboard, add these environment variables:

**Required:**
- `GEMINI_API_KEY`: Your Google Gemini API key

**Optional (for Azure integration):**
- `AZURE_STORAGE_CONNECTION_STRING`: Your Azure Storage connection string
- `AZURE_FILES_SHARE_NAME`: `college-documents` (or your share name)
- `AZURE_BLOB_CONNECTION_STRING`: Your Azure Blob Storage connection string
- `AZURE_BLOB_CONTAINER_NAME`: `uploaded-documents` (or your container name)

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. You'll get a URL like: `https://your-service-name.onrender.com`

### 5. Test Your Deployment

After deployment, test these endpoints:
- `GET /` - Should return API status
- `GET /health` - Should return health check
- `GET /system/status` - Should return system information

### 6. Update Frontend CORS

Don't forget to update your frontend to use the new backend URL!

## Alternative: Using render.yaml

You can also use the included `render.yaml` file for infrastructure-as-code deployment:

1. Place the `render.yaml` file in your repository root
2. In Render dashboard, create a new service from "Infrastructure as Code"
3. Connect your repository
4. Render will automatically configure everything based on the YAML file

## Troubleshooting

- **Build fails**: Check that all dependencies in `requirements.txt` are compatible
- **App crashes**: Check logs in Render dashboard for error messages
- **CORS issues**: Verify CORS settings in your FastAPI application
- **Environment variables**: Make sure all required env vars are set in Render dashboard

## Monitoring

- Use Render's built-in logs and metrics
- The `/health` endpoint can be used for uptime monitoring
- Consider setting up alerts for service downtime
