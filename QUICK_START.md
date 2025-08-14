# 🚀 Quick Start - Deploy to Hugging Face Spaces

## ⚡ Fast Deployment (5 minutes)

### 1. **Create Hugging Face Space**
- Go to [huggingface.co/spaces](https://huggingface.co/spaces)
- Click "Create new Space"
- Choose **"Gradio"** as SDK
- Set Python version to **3.11+**
- Name it: `eureka-gpt-assistant-suite`

### 2. **Clone & Upload Files**
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME
```

**Copy ALL files from `hf_deployment/` to the Space repository:**
- `app.py` ✅
- `requirements.txt` ✅
- `constants.py` ✅
- `models.py` ✅
- `prompts.py` ✅
- `services.py` ✅
- `README.md` ✅
- `.gitattributes` ✅
- `index.html` ✅
- `.gitignore` ✅

### 3. **Set Environment Variable**
- Go to Space Settings → Repository secrets
- Add: `OPENAI_API_KEY` = `your_actual_api_key`

### 4. **Deploy**
```bash
git add .
git commit -m "Initial deployment"
git push
```

### 5. **Test Your Deployment**
- Wait 2-5 minutes for build
- Visit your Space URL
- Test: `/api/health`
- Test: `/api/select-gpt`

## 🌐 Your Space URL
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## 📱 Available Endpoints
- **`/`** - Beautiful landing page
- **`/docs`** - Interactive API docs
- **`/api/health`** - Health check
- **`/api/select-gpt`** - Choose GPT
- **`/api/chat`** - Chat with GPT

## 🎯 13 GPT Assistants Ready
1. Offer Clarifier
2. Avatar Creator
3. Before State Research
4. After State Research
5. Avatar Validator
6. Trigger GPT
7. EPO Builder
8. SCAMPER Synthesizer
9. Wildcard Idea Bot
10. Concept Crafter
11. Hook & Headline GPT
12. Campaign Generator
13. Idea Injection Bot

---

**🚀 Ready to deploy! Your marketing AI suite will be live worldwide!**
