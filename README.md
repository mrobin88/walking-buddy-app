# 🚶 Walking Buddy App

A social walking app that connects people for outdoor activities, real-time chat, and location-based friend discovery.

## ✨ Features

- **User Authentication** - Secure login/register with JWT tokens
- **Friend System** - Send/accept friend requests
- **Real-time Chat** - Direct messaging between users
- **Location Services** - Find nearby walking buddies
- **Profile Management** - Upload photos, update preferences
- **Performance Monitoring** - Real-time system status tracking
- **Walk Tracking** - Record and share walking activities

## 🛠️ Tech Stack

- **Backend:** Django 4.2.7 + Django REST Framework
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Authentication:** JWT + Session-based auth
- **Real-time:** Django Channels
- **File Storage:** Local (dev) / AWS S3 (production)
- **Monitoring:** Custom performance tracking
- **Deployment:** Railway, Docker-ready

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd walking-buddy-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit the app**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/check-auth/` - Check authentication status

### User Management
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/update-profile/` - Update profile
- `POST /api/auth/profile/picture/` - Upload profile picture
- `GET /api/auth/stats/` - Get user statistics

### Friends & Social
- `GET /api/auth/friends/` - List friends
- `POST /api/auth/friends/send/<user_id>/` - Send friend request
- `POST /api/auth/friends/accept/<user_id>/` - Accept friend request
- `POST /api/auth/friends/reject/<user_id>/` - Reject friend request
- `GET /api/auth/nearby-users/` - Find nearby users

### Chat
- `GET /api/chat/dm/list/<user_id>/` - Get chat history
- `POST /api/chat/dm/send/<user_id>/` - Send message
- `POST /api/chat/dm/mark-read/<dm_id>/` - Mark message as read

### System Monitoring
- `GET /api/auth/system-status/` - System performance metrics

## 🏗️ Project Structure

```
walking-buddy-app/
├── django_walking_buddy/     # Django project settings
├── users/                    # User management app
├── chat/                     # Chat functionality
├── walks/                    # Walking activities
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # User uploads
├── logs/                     # Application logs
└── requirements.txt          # Python dependencies
```

## 🚀 Deployment

### Railway (Recommended)

1. **Connect to Railway**
   - Install Railway CLI: `npm i -g @railway/cli`
   - Login: `railway login`
   - Link project: `railway link`

2. **Deploy**
   ```bash
   railway up
   ```

3. **Set environment variables**
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set DEBUG=False
   railway variables set DATABASE_URL=your-postgres-url
   ```

### Environment Variables

```bash
# Required
SECRET_KEY=your-django-secret-key
DEBUG=True/False
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report

# Run linting
flake8 .
black --check .
isort --check-only .

# Security checks
bandit -r .
safety check
```

## 📈 Monitoring

The app includes built-in performance monitoring:

- **System Status API:** `/api/auth/system-status/`
- **Performance Logs:** `logs/performance.log`
- **Database Query Logs:** `logs/django.log`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/your-username/walking-buddy/issues)
- **Documentation:** [Wiki](https://github.com/your-username/walking-buddy/wiki)
- **Email:** your-email@example.com

## 🎯 Roadmap

- [ ] Push notifications
- [ ] Group walks
- [ ] Achievement system
- [ ] Route sharing
- [ ] Weather integration
- [ ] Mobile app
- [ ] Advanced analytics

---

**Built with ❤️ for the walking community** 