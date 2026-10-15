# 🚀 Complete Deployment Guide

Step-by-step guide to deploy the Driver Drowsiness Detection system to production.

## 📋 Prerequisites

- GitHub account
- [Render](https://render.com) account (backend hosting)
- [Vercel](https://vercel.com) account (frontend hosting)
- Trained model weights (`best.pt`)

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Driver Drowsiness Detection System"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/driver-drowsiness-detection.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Model Weights

Ensure `backend/weights/best.pt` exists:

```bash
# Check file exists
ls -lh backend/weights/best.pt

# If missing, copy from ml_pipeline
cp ml_pipeline/models/yolo_best.pt backend/weights/best.pt
```

**Important:** Model file should be 5-10 MB. If larger than 100MB, use Git LFS:

```bash
git lfs install
git lfs track "backend/weights/*.pt"
git add .gitattributes
git add backend/weights/best.pt
git commit -m "Add model weights with Git LFS"
git push
```

---

## 🖥️ Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name:** `drowsiness-detection-api` (or your choice)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend` (if monorepo)
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Free tier is fine for testing
- Upgrade to paid for production (no cold starts)

### 2.2 Environment Variables

Click **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Add Vercel URL later |
| `MODEL_PATH` | `weights/best.pt` | Path to model weights |
| `MODEL_TYPE` | `yolo` | Model architecture |
| `PYTHON_VERSION` | `3.11.0` | Specify Python version |

### 2.3 Health Check

Under **"Settings"** → **"Health Check"**:
- **Health Check Path:** `/health`
- **Wait:** 30 seconds (model loading time)

### 2.4 Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (~5-10 minutes)
3. Check logs for:
   ```
   ✓ Model loaded successfully!
   ✓ API is ready to accept requests
   ```

### 2.5 Test Backend

Copy your Render URL (e.g., `https://drowsiness-api.onrender.com`)

**Test health endpoint:**
```bash
curl https://drowsiness-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Driver Drowsiness Detection API",
  "model_loaded": true
}
```

**Test prediction (optional):**
```bash
curl -X POST https://drowsiness-api.onrender.com/predict \
  -F "file=@test_image.jpg"
```

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure project:

**Framework Preset:** Next.js (auto-detected)

**Root Directory:** 
- If monorepo: `frontend`
- If frontend is root: leave empty

**Build Settings:**
- **Build Command:** `npm run build` (default)
- **Output Directory:** `.next` (default)
- **Install Command:** `npm install` (default)

### 3.2 Environment Variables

Before deploying, add environment variable:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://drowsiness-api.onrender.com` |

Replace with your actual Render backend URL.

### 3.3 Deploy

1. Click **"Deploy"**
2. Wait for build (~2-3 minutes)
3. Get your deployment URL (e.g., `https://your-app.vercel.app`)

### 3.4 Test Frontend

1. Open your Vercel URL
2. Allow camera access
3. Click "Capture & Analyze Frame"
4. Check if prediction works

---

## 🔗 Step 4: Connect Frontend & Backend

### 4.1 Update Backend CORS

Your backend needs to allow requests from your Vercel frontend.

1. Go to Render Dashboard → Your backend service
2. **Environment** → Edit `ALLOWED_ORIGINS`
3. Update to:
   ```
   http://localhost:3000,https://your-app.vercel.app
   ```
   Replace `your-app.vercel.app` with your actual Vercel domain
   
4. **Save Changes** (this will redeploy)

### 4.2 Verify Connection

1. Open your Vercel frontend
2. Check backend status indicator (should show "Connected")
3. Test a prediction
4. Check browser DevTools Console for any CORS errors

---

## ✅ Step 5: Production Checklist

### Security

- [ ] Backend CORS only allows your frontend domain (no wildcards)
- [ ] HTTPS enabled on both frontend and backend
- [ ] No API keys or secrets in frontend code
- [ ] Environment variables properly set

### Performance

- [ ] Model loads once at startup (not per-request)
- [ ] Image compression reasonable (JPEG quality ~95%)
- [ ] Frontend has loading states for cold starts

### User Experience

- [ ] Camera permissions handled gracefully
- [ ] Error messages are user-friendly
- [ ] Loading states show during inference
- [ ] Dark mode works correctly

### Monitoring

- [ ] Backend health check endpoint working
- [ ] Check Render logs for errors
- [ ] Check Vercel analytics for frontend errors

---

## 🔄 Updating Deployment

### Update Backend

```bash
git add backend/
git commit -m "Update backend"
git push
```

Render auto-deploys on git push (if enabled).

### Update Frontend

```bash
git add frontend/
git commit -m "Update frontend"
git push
```

Vercel auto-deploys on git push.

### Update Model Weights

```bash
# Copy new weights
cp ml_pipeline/models/new_model.pt backend/weights/best.pt

# Commit and push
git add backend/weights/best.pt
git commit -m "Update model weights"
git push

# Render will redeploy automatically
```

---

## 🐛 Troubleshooting

### Backend Issues

**"Application failed to respond"**
- Check Render logs
- Verify model weights exist
- Increase health check wait time
- Check if `PORT` env var is used correctly

**Cold starts (30-60s delay)**
- This is normal on Render free tier
- Upgrade to paid plan to keep service running
- Or use a keep-alive service (cron-job.org)

**CORS errors**
- Verify `ALLOWED_ORIGINS` includes exact frontend URL
- No trailing slashes in URLs
- Include protocol (https://)

### Frontend Issues

**"Network error"**
- Check `NEXT_PUBLIC_API_URL` is set in Vercel
- Verify backend is running
- Check browser DevTools Network tab

**Camera not working**
- HTTPS required in production
- Check browser permissions
- Try different browser

**Dark mode broken**
- Clear browser cache
- Check Tailwind CSS is properly configured

### Deployment Issues

**Build fails on Render**
- Check Python version matches
- Verify requirements.txt is correct
- Check if model weights are too large

**Build fails on Vercel**
- Check Node version (should use 18+)
- Verify package.json is correct
- Check if `NEXT_PUBLIC_API_URL` is set

---

## 💰 Cost Estimation

### Free Tier (Good for Portfolio/Demo)

| Service | Cost | Limitations |
|---------|------|-------------|
| Render | $0 | 750 hours/month, cold starts |
| Vercel | $0 | 100GB bandwidth, fair use |
| **Total** | **$0/month** | Cold starts, limited traffic |

### Production (Paid Tier)

| Service | Cost | Benefits |
|---------|------|----------|
| Render Starter | $7/month | No cold starts, always on |
| Vercel Pro | $20/month | 1TB bandwidth, priority support |
| **Total** | **$27/month** | Fast, reliable, production-ready |

---

## 🔐 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Go to Vercel project → **Settings** → **Domains**
2. Add your domain (e.g., `drowsiness-detection.com`)
3. Configure DNS (Vercel provides instructions)
4. Update backend `ALLOWED_ORIGINS`:
   ```
   https://drowsiness-detection.com
   ```

### Add Custom Domain to Render

1. Go to Render service → **Settings** → **Custom Domains**
2. Add your domain (e.g., `api.drowsiness-detection.com`)
3. Configure DNS (Render provides instructions)
4. Update frontend `NEXT_PUBLIC_API_URL`:
   ```
   https://api.drowsiness-detection.com
   ```

---

## 📊 Monitoring & Analytics

### Render

- **Logs:** Real-time logs in dashboard
- **Metrics:** CPU, memory, response time
- **Alerts:** Set up email alerts for downtime

### Vercel

- **Analytics:** Built-in web analytics
- **Logs:** Function logs and errors
- **Speed Insights:** Core Web Vitals

### External Monitoring (Optional)

- [UptimeRobot](https://uptimerobot.com) - Free uptime monitoring
- [Sentry](https://sentry.io) - Error tracking
- [LogRocket](https://logrocket.com) - Session replay

---

## 🎉 Success!

Your Driver Drowsiness Detection system is now live!

**Share your project:**
- Add to portfolio
- Share on LinkedIn/Twitter
- Submit to hackathons
- Publish on Product Hunt

**Next steps:**
- Add real-time video streaming (WebRTC)
- Implement temporal smoothing (consecutive frames)
- Add audio alerts
- Build mobile app (React Native)
- Add analytics dashboard

---

## 📞 Support

If you encounter issues:
1. Check logs (Render/Vercel dashboards)
2. Review this guide
3. Check component READMEs
4. Open GitHub issue

Good luck! 🚀
