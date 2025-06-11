# Walking Buddy Local Development Script
Write-Host "🚀 Starting Walking Buddy Local Development..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    if (-not (Test-Path ".env")) {
        Write-Host "📝 Creating basic .env file..." -ForegroundColor Yellow
        @"
DEBUG=True
SECRET_KEY=your-local-secret-key-change-this
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379
ALLOWED_HOSTS=localhost,127.0.0.1
"@ | Out-File -FilePath ".env" -Encoding UTF8
    }
}

# Run migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

# Collect static files
Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Start development server
Write-Host "🌐 Starting development server..." -ForegroundColor Green
Write-Host "📍 Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

python manage.py runserver 