# Complete Deployment Guide

## 🚀 Quick Start Options

### Option 1: Railway Deployment (Recommended - Easiest)
### Option 2: Docker Deployment (More Control)
### Option 3: Local Development (Testing)

---

## Option 1: Railway Deployment

### Step 1: Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Set Up Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### Step 3: Add Services
1. **PostgreSQL**: Add from Railway marketplace
2. **Redis**: Add from Railway marketplace (for WebSocket support)

### Step 4: Set Environment Variables
In Railway dashboard → Variables tab, add:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1

# Database (Railway will auto-generate this)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis (Railway will auto-generate this)
REDIS_URL=redis://username:password@host:port

# Static Files (AWS S3)
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Email (SendGrid)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Stripe (for payments)
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

### Step 5: Deploy
Railway will automatically deploy when you push to main branch!

---

## Option 2: Docker Deployment

### Local Docker Development
```bash
# Start all services
docker-compose up --build

# Or start in background
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Production Docker Deployment
```bash
# Create .env file with production variables
cp .env.example .env
# Edit .env with your production values

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d --build
```

### Docker Commands
```bash
# Build image
docker build -t walking-buddy .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=your-db-url \
  walking-buddy

# View running containers
docker ps

# View logs
docker logs <container-id>
```

---

## Option 3: Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## Environment Variables Reference

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `False` (production) |
| `SECRET_KEY` | Django secret key | `your-super-secret-key` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-domain.com,localhost` |
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host:port/db` |
| `REDIS_URL` | Redis connection | `redis://host:port` |

### Optional Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `USE_S3` | Use AWS S3 for static files | `True` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `...` |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | `my-bucket` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `EMAIL_HOST` | SMTP host | `smtp.sendgrid.net` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `your-api-key` |

---

## Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failed
- Check if Redis is running
- Verify JWT token is valid
- Check ASGI configuration

#### 2. Database Connection Error
- Verify DATABASE_URL is correct
- Check if database is accessible
- Ensure migrations are run

#### 3. Static Files Not Loading
- Run `python manage.py collectstatic`
- Check S3 configuration
- Verify static files directory

#### 4. Chat Not Working
- Check WebSocket authentication
- Verify Redis connection
- Check browser console for errors

### Debug Commands
```bash
# Check Django status
python manage.py check

# Test database connection
python manage.py dbshell

# Check Redis connection
redis-cli ping

# View logs
tail -f logs/django.log
```

---

## Monitoring & Maintenance

### Health Checks
- `/health/` - Basic health check
- `/api/status/` - Detailed system status

### Logs
- Railway: View in dashboard
- Docker: `docker-compose logs`
- Local: `logs/django.log`

### Backups
- Database: Use Railway's backup feature
- Files: S3 versioning
- Code: GitHub repository

---

## Next Steps

1. **Choose your deployment method** (Railway recommended)
2. **Set up environment variables**
3. **Deploy and test**
4. **Set up monitoring**
5. **Configure custom domain**
6. **Set up SSL certificate**

Your app is now ready for production! 🎉 