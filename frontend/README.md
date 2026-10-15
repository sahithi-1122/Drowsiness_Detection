# Driver Drowsiness Detection - Frontend

Next.js frontend for real-time drowsiness detection with webcam integration.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Project Structure

```
frontend/
├── app/
│   ├── page.jsx           # Main page with camera and results
│   ├── layout.jsx         # Root layout
│   └── globals.css        # Global styles + Tailwind
├── components/
│   ├── Camera.jsx         # Webcam component
│   ├── DetectionResult.jsx # Result display
│   └── Loading.jsx        # Loading indicator
├── lib/
│   └── api.js            # API client for backend
├── public/               # Static assets
├── package.json
└── next.config.js
```

## 📦 Components

### Camera Component
- Requests webcam access via `getUserMedia()`
- Displays live video preview
- Captures current frame as JPEG blob
- Error handling for permissions and no camera

**Props:**
- `onCapture(blob)` - Callback when frame is captured
- `disabled` - Disable capture button

### DetectionResult Component
- Displays prediction results
- Color-coded status (red=drowsy, green=alert)
- Confidence score with visual bar
- Detailed class probabilities

**Props:**
- `prediction` - Prediction object from API
- `error` - Error message to display

### Loading Component
- Animated spinner
- Custom loading message
- Used during API requests

**Props:**
- `message` - Loading message to display

## 🎨 Styling

Built with **Tailwind CSS** for responsive, modern UI.

**Color scheme:**
- Drowsy: Red (`bg-red-500`)
- Alert: Green (`bg-green-500`)
- Dark mode supported automatically

**Custom classes** (in `globals.css`):
- `.btn-primary` - Blue action button
- `.card` - Content card with shadow
- `.status-drowsy` - Drowsy status styling
- `.status-alert` - Alert status styling

## 🌐 API Integration

API client in `lib/api.js` provides:

```javascript
// Check backend health
await checkHealth()

// Send image for prediction
const result = await predictDrowsiness(imageBlob)

// Test connection
const isConnected = await testConnection()
```

**Environment variable:**
- `NEXT_PUBLIC_API_URL` - Backend URL (required)

## 🚢 Deployment to Vercel

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Option 2: GitHub Integration

1. **Push to GitHub**
2. **Import** project in [Vercel dashboard](https://vercel.com)
3. **Configure:**
   - Framework Preset: Next.js
   - Root Directory: `frontend` (if monorepo)
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
   
4. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```

5. **Deploy!**

### Post-Deployment

After deploying:

1. **Copy your Vercel URL** (e.g., `https://your-app.vercel.app`)

2. **Update backend CORS:**
   - Go to Render backend settings
   - Add to `ALLOWED_ORIGINS`: `https://your-app.vercel.app`
   - Redeploy backend

3. **Test the connection:**
   - Open your Vercel URL
   - Allow camera access
   - Capture a frame
   - Check if prediction works

## 🔧 Configuration

### next.config.js
Basic Next.js configuration with React strict mode.

### tailwind.config.js
Tailwind CSS configuration for styling.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

**Important:** 
- Variables with `NEXT_PUBLIC_` prefix are exposed to the browser
- Never hardcode URLs in components - always use env vars
- Set in Vercel dashboard for production

## 🧪 Testing

```bash
# Lint code
npm run lint

# Build for production (test for errors)
npm run build

# Run production build locally
npm run start
```

## 📱 Browser Compatibility

**Webcam support requires:**
- HTTPS in production (localhost HTTP is OK)
- Modern browser with `getUserMedia()` support:
  - Chrome 53+
  - Firefox 36+
  - Safari 11+
  - Edge 79+

**Mobile browsers:**
- iOS Safari 11+
- Chrome Mobile 53+

## 🐛 Troubleshooting

### Camera not working

**Issue:** "Permission denied" error

**Solution:**
- Check browser permissions (chrome://settings/content/camera)
- Ensure HTTPS in production (HTTP only works on localhost)
- Try incognito/private mode
- Try different browser

---

**Issue:** "No camera found"

**Solution:**
- Connect a webcam
- Check if camera works in other apps
- Refresh the page

### API connection failed

**Issue:** "Failed to fetch" or CORS error

**Solution:**
- Verify backend is running (`http://localhost:8000/health`)
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend `ALLOWED_ORIGINS` includes frontend URL
- Check no trailing slashes in URLs

### Build errors

**Issue:** Module not found

**Solution:**
```bash
rm -rf node_modules .next
npm install
npm run dev
```

### Dark mode not working

The app uses system preference for dark mode automatically via `prefers-color-scheme`.

To test:
- **Mac:** System Preferences → General → Appearance
- **Windows:** Settings → Personalization → Colors
- **Chrome DevTools:** Cmd/Ctrl+Shift+P → "Render" → Emulate CSS prefers-color-scheme

## 🎯 Features

- ✅ Live webcam preview
- ✅ One-click frame capture
- ✅ Real-time prediction display
- ✅ Confidence visualization
- ✅ Color-coded status
- ✅ Dark mode support
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Cold start awareness
- ✅ Backend status indicator

## 📚 Technologies

- **Next.js 14** - React framework (App Router)
- **React 18** - UI library
- **Tailwind CSS** - Utility-first CSS
- **getUserMedia API** - Webcam access

## 📄 License

MIT
