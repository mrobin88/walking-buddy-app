# Deployment Guide

## Railway Deployment

### Environment Variables

Set these environment variables in your Railway project:

#### Django Settings
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1
```

#### Database (PostgreSQL)
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

#### Redis (for Channels/Celery)
```
REDIS_URL=redis://username:password@host:port
```

#### Static Files (AWS S3 or Railway)
```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=your-bucket.s3.amazonaws.com
```

#### Email (SendGrid or similar)
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

#### Stripe (for payments)
```
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

#### Social Auth (optional)
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

#### Monitoring (optional)
```
SENTRY_DSN=your-sentry-dsn
```

### Railway Setup Steps

1. **Connect GitHub Repository**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Set Environment Variables**
   - Go to your project settings
   - Add all the environment variables listed above

3. **Add Services**
   - **PostgreSQL**: Add from Railway marketplace
   - **Redis**: Add from Railway marketplace (if needed)

4. **Deploy**
   - Railway will automatically deploy when you push to main branch
   - Check the deployment logs for any issues

### Local Development

For local development, create a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your local values
DEBUG=True
SECRET_KEY=your-local-secret-key
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379
```

### Docker Deployment

If you prefer Docker deployment:

```bash
# Build the image
docker build -t walking-buddy .

# Run with environment variables
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=your-db-url \
  walking-buddy
```

### Health Checks

The application includes health check endpoints:
- `/health/` - Basic health check
- `/api/status/` - Detailed system status

### Monitoring

- Check Railway logs for errors
- Set up Sentry for error tracking
- Monitor database connections
- Watch Redis memory usage

### SSL/HTTPS

Railway automatically provides SSL certificates for custom domains.

### Scaling

- Railway automatically scales based on traffic
- Consider upgrading to paid plan for better performance
- Monitor resource usage in Railway dashboard 