# 🚀 Free Deployment Guide

## **Option 1: Render (Recommended - Easiest)**

### **Step 1: Prepare Your Code**
```bash
# Make sure all changes are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### **Step 2: Deploy on Render**
1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `walking-buddy-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn django_walking_buddy.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: Free

### **Step 3: Add Database**
1. In your Render dashboard, click "New +" → "PostgreSQL"
2. Name: `walking-buddy-db`
3. Plan: Free
4. Copy the **Internal Database URL**

### **Step 4: Add Redis (Optional)**
1. Click "New +" → "Redis"
2. Name: `walking-buddy-redis`
3. Plan: Free

### **Step 5: Set Environment Variables**
In your web service settings, add:
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://... (from step 3)
REDIS_URL=redis://... (from step 4)
```

---

## **Option 2: Fly.io (Great for WebSockets)**

### **Step 1: Install Fly CLI**
```bash
# Windows
winget install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

### **Step 2: Deploy**
```bash
# Login
flyctl auth signup

# In your project directory
flyctl launch

# Deploy
flyctl deploy
```

### **Step 3: Add Database**
```bash
flyctl postgres create
flyctl postgres attach <database-name>
```

---

## **Option 3: PythonAnywhere (Simplest)**

### **Step 1: Sign Up**
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account

### **Step 2: Upload Code**
1. Go to "Files" tab
2. Upload your project files
3. Or use Git: `git clone https://github.com/your-username/walking-buddy.git`

### **Step 3: Set Up Web App**
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Python version: 3.11
5. Source code: `/home/yourusername/walking-buddy`
6. WSGI file: Edit and point to your Django app

### **Step 4: Install Dependencies**
1. Go to "Consoles" tab
2. Open Bash console
3. Run:
```bash
cd walking-buddy
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

---

## **Option 4: Heroku (Cheap - $5/month)**

### **Step 1: Install Heroku CLI**
```bash
# Windows
winget install Heroku.CLI
```

### **Step 2: Deploy**
```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

---

## **🌐 Testing on Different Networks**

### **Mobile Testing**
- **Render/Fly.io**: Access from your phone's browser
- **ngrok**: Create tunnel to localhost for testing
  ```bash
  # Install ngrok
  # Run: ngrok http 8000
  # Share the URL with friends
  ```

### **Network Testing**
- **Speed Test**: Test loading times on different connections
- **Geographic Testing**: Use VPN to test from different locations
- **Device Testing**: Test on different devices and browsers

---

## **🔧 Environment Variables for Production**

Set these in your hosting platform:

```bash
# Django
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Redis (for WebSockets)
REDIS_URL=redis://username:password@host:port

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (for payments)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## **🎯 My Recommendation**

**Start with Render** because:
- ✅ Free tier is generous (750 hours/month)
- ✅ PostgreSQL included
- ✅ Easy deployment from GitHub
- ✅ Good for testing and small projects
- ✅ Can upgrade later if needed

**Then try Fly.io** if you need:
- 🌍 Global deployment
- ⚡ Better WebSocket performance
- 🔧 More control

---

## **🚀 Quick Start Commands**

```bash
# 1. Prepare your code
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Deploy on Render (manual steps above)

# 3. Test your app
curl https://your-app-name.onrender.com

# 4. Check logs
# In Render dashboard → Logs tab
```

Your app will be live and accessible from anywhere! 🌍 