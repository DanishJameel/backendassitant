# 🚀 Render Deployment Guide for EUREKA GPT Assistant Suite

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## 🔄 Complete Git Commands

Run these commands in your terminal:

```bash
# 1. Add all your changes (excluding .env)
git add README.md app.py index.html models.py prompts.py requirements.txt services.py
git add "GPT FINAL FLOW/"

# 2. Add deployment files
git add render.yaml Procfile runtime.txt RENDER_DEPLOYMENT.md

# 3. Ensure .env is ignored
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 4. Commit changes
git commit -m "Update EUREKA GPT Assistant Suite with Render deployment preparation"

# 5. Push to GitHub
git push origin main
```

## 🌐 Deploy to Render

### **Step 1: Connect GitHub to Render**

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select your repository: `DanishJameel/Edurkaagent`

### **Step 2: Configure Your Web Service**

Fill in these settings:

- **Name**: `eureka-gpt-assistant-suite`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### **Step 3: Set Environment Variables**

Click **"Environment"** and add:

- **Key**: `OPENAI_API_KEY`
- **Value**: Your actual OpenAI API key
- **Sync**: Leave unchecked (this keeps it private)

### **Step 4: Deploy**

1. Click **"Create Web Service"**
2. Wait for build to complete (2-5 minutes)
3. Your app will be available at: `https://your-app-name.onrender.com`

## 🔧 Alternative: Use render.yaml (Recommended)

If you prefer automatic configuration:

1. **Push your code** with the `render.yaml` file
2. In Render, click **"New +"** → **"Blueprint"**
3. Select your repository
4. Render will automatically configure everything from `render.yaml`

## 📱 Your Deployed App

Once deployed, you'll have:

- **Main App**: `https://your-app-name.onrender.com`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/api/health`

## 🧪 Test Your Deployment

### **Test 1: Health Check**
```bash
curl https://your-app-name.onrender.com/api/health
```

### **Test 2: GPT Selection**
```bash
curl -X POST "https://your-app-name.onrender.com/api/select-gpt" \
     -H "Content-Type: application/json" \
     -d '{"gpt_type": "offer_clarifier"}'
```

### **Test 3: Chat with GPT**
```bash
curl -X POST "https://your-app-name.onrender.com/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, I want to clarify my offer", "gpt_type": "offer_clarifier"}'
```

## 🔒 Security & Environment Variables

### **Never Commit These Files:**
- `.env` (contains your API key)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python files)

### **Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Automatically set by Render

## 🚨 Common Issues & Solutions

### **Build Failures**
- **Python Version**: Ensure `runtime.txt` specifies `python-3.11.0`
- **Dependencies**: Check `requirements.txt` has all needed packages
- **Build Command**: Should be `pip install -r requirements.txt`

### **Runtime Errors**
- **Port Issues**: App must use `$PORT` environment variable
- **API Key**: Ensure `OPENAI_API_KEY` is set in Render
- **File Paths**: Use relative paths, not absolute

### **Performance Issues**
- **Free Tier**: Limited to 750 hours/month
- **Cold Starts**: First request may be slow
- **Memory**: Free tier has 512MB RAM limit

## 📊 Monitoring & Logs

### **View Logs**
1. Go to your Render dashboard
2. Click on your web service
3. Click **"Logs"** tab
4. Monitor for errors or issues

### **Health Monitoring**
- Use `/api/health` endpoint
- Set up external monitoring if needed
- Monitor OpenAI API usage

## 🔄 Updating Your App

### **Automatic Updates**
1. Push changes to GitHub `main` branch
2. Render automatically redeploys
3. Monitor build logs for any issues

### **Manual Updates**
1. Go to Render dashboard
2. Click **"Manual Deploy"**
3. Select branch and deploy

## 💰 Cost Considerations

### **Free Tier**
- **750 hours/month** (about 31 days)
- **512MB RAM**
- **Shared CPU**
- **Perfect for testing and small projects**

### **Paid Plans**
- **Starter**: $7/month for always-on service
- **Standard**: $25/month for better performance
- **Pro**: Custom pricing for enterprise needs

## 🎯 Best Practices

### **Development**
1. **Test locally** before pushing
2. **Use environment variables** for sensitive data
3. **Monitor API usage** to control costs
4. **Keep dependencies updated**

### **Deployment**
1. **Use render.yaml** for consistent configuration
2. **Set up monitoring** and alerts
3. **Test all endpoints** after deployment
4. **Keep backups** of your configuration

## 🆘 Need Help?

### **Render Support**
- **Documentation**: [docs.render.com](https://docs.render.com)
- **Community**: [community.render.com](https://community.render.com)
- **Email**: support@render.com

### **Common Commands**
```bash
# Check deployment status
git log --oneline -5

# View remote URLs
git remote -v

# Check ignored files
git status --ignored

# Force push (if needed)
git push -f origin main
```

---

## 🎉 Success Checklist

- [ ] Code pushed to GitHub
- [ ] .env file NOT committed
- [ ] render.yaml created and committed
- [ ] App deployed on Render
- [ ] Environment variables set
- [ ] Health check passes
- [ ] GPT endpoints working
- [ ] API documentation accessible

**🚀 Your EUREKA GPT Assistant Suite is now live on the web!**
