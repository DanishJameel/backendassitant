# 🚀 Hugging Face Spaces Deployment Guide

This guide will walk you through deploying the EUREKA GPT Assistant Suite to Hugging Face Spaces.

## 📋 Prerequisites

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Git Knowledge**: Basic understanding of Git commands

## 🎯 Step-by-Step Deployment

### **Step 1: Create a New Space**

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Owner**: Your username or organization
   - **Space name**: `eureka-gpt-assistant-suite` (or your preferred name)
   - **License**: Choose appropriate license
   - **SDK**: Select **"Gradio"** (this will work for our FastAPI backend)
   - **Python version**: 3.11 or higher

### **Step 2: Clone the Space Repository**

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME
```

### **Step 3: Upload Required Files**

Copy these files from your local `gpt_backend` directory to the Space repository:

```bash
# Core application files
cp ../gpt_backend/app.py ./
cp ../gpt_backend/requirements.txt ./
cp ../gpt_backend/constants.py ./
cp ../gpt_backend/models.py ./
cp ../gpt_backend/prompts.py ./
cp ../gpt_backend/services.py ./
cp ../gpt_backend/README.md ./
cp ../gpt_backend/.gitattributes ./
```

### **Step 4: Set Environment Variables**

1. In your Space repository, go to **Settings** → **Repository secrets**
2. Add a new secret:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your actual OpenAI API key

### **Step 5: Commit and Push**

```bash
git add .
git commit -m "Initial deployment of EUREKA GPT Assistant Suite"
git push
```

### **Step 6: Monitor Deployment**

1. Go to your Space page on Hugging Face
2. Check the **Logs** tab for any deployment issues
3. Wait for the build to complete (usually 2-5 minutes)

## 🔧 Configuration Files

### **app.py**
- Main FastAPI application entry point
- Configured for Hugging Face Spaces
- Runs on port 7860 (Hugging Face default)

### **requirements.txt**
- All necessary Python dependencies
- Optimized for Hugging Face deployment

### **Environment Variables**
- `OPENAI_API_KEY`: Required for OpenAI API access

## 🌐 Accessing Your Deployed App

Once deployed, your app will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## 📡 API Endpoints Available

Your deployed app will have these endpoints:

- **`/`** - Landing page with app information
- **`/docs`** - Interactive API documentation (Swagger UI)
- **`/api/select-gpt`** - Select GPT assistant
- **`/api/chat`** - Chat with selected GPT
- **`/api/reset`** - Reset conversation session
- **`/api/combined-summary`** - Get combined summary
- **`/api/health`** - Health check

## 🧪 Testing Your Deployment

### **Test the Health Endpoint**
```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/api/health
```

### **Test GPT Selection**
```bash
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/api/select-gpt \
  -H "Content-Type: application/json" \
  -d '{"gpt_type": "offer_clarifier"}'
```

### **Test Chat**
```bash
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session", "message": "Hello", "gpt_type": "offer_clarifier"}'
```

## 🔍 Troubleshooting

### **Common Issues:**

1. **Build Fails**
   - Check the logs in your Space
   - Verify all required files are uploaded
   - Ensure `requirements.txt` is correct

2. **API Key Error**
   - Verify `OPENAI_API_KEY` is set in repository secrets
   - Check the secret name matches exactly

3. **Import Errors**
   - Ensure all Python files are in the root directory
   - Check file permissions

4. **Port Issues**
   - Hugging Face uses port 7860 by default
   - Don't change the port in `app.py`

### **Check Logs:**
1. Go to your Space page
2. Click **"Logs"** tab
3. Look for error messages
4. Common errors are usually in the build or runtime logs

## 🔄 Updating Your Deployment

To update your deployed app:

```bash
# Make changes to your local files
# Then push to Hugging Face
git add .
git commit -m "Update: [describe your changes]"
git push
```

Hugging Face will automatically rebuild and redeploy your app.

## 📊 Monitoring and Analytics

- **Space Metrics**: View usage statistics in your Space dashboard
- **API Calls**: Monitor API usage through Hugging Face analytics
- **Error Logs**: Check logs for any runtime errors

## 🚀 Production Considerations

1. **Rate Limiting**: Hugging Face has rate limits for free accounts
2. **Scaling**: Consider upgrading for higher traffic
3. **Security**: Review CORS settings for production use
4. **Backup**: Keep local copies of all files

## 📚 Additional Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 🆘 Getting Help

If you encounter issues:

1. Check the Space logs first
2. Review this deployment guide
3. Check Hugging Face community forums
4. Verify your OpenAI API key is working

---

**Happy Deploying! 🎉**

Your EUREKA GPT Assistant Suite will be live and accessible to users worldwide through Hugging Face Spaces.
