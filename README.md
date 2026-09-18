# Thailand Tourism News Analyzer v2

React Frontend + FastAPI Backend + MySQL + Local Ollama

## Features

- Scrapes major Thai English news sources
- Uses **local Ollama** model to keep only Thailand tourism related news
- Classifies into 15 tourism categories
- **MySQL** database (auto-created on backend start)
- Tables and schema created automatically when backend starts
- Modern React web interface
- FastAPI REST API with CORS

## Project Structure

```
thailand_news_v2/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry + auto DB startup
│   │   ├── database.py      # MySQL connection + auto create DB
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── api/routes.py
│   ├── models/classifier.py # Ollama classification
│   ├── scrapers/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── services/api.js
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Step-by-step Setup Commands

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8 (running locally)
- Ollama installed and running

```bash
# Install Ollama model
ollama pull llama3.2
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux / Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / Mac

# Edit .env and set your MySQL password:
# MYSQL_PASSWORD=your_mysql_password
```

### 3. Start Backend (Database auto-created)

```bash
# From backend folder (with venv activated)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup the backend will automatically:
1. Create the MySQL database if it does not exist
2. Create all tables (news_articles)
3. Check Ollama connection

API docs: http://localhost:8000/docs

### 4. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start React dev server
npm run dev
```

Open: http://localhost:5173

### 5. First Scrape

In the web UI click **Run Scrape**  
or call the API:

```bash
curl -X POST http://localhost:8000/api/scrape
```

Scrape runs in background and uses Ollama to classify each article.

### 6. Useful Commands

```bash
# Backend only
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend
npm run dev

# Manual scrape from Python
cd backend
python -c "from scrapers.scraper import run_full_scrape; run_full_scrape()"
```

## Environment Variables (.env)

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=thailand_tourism_news

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
AUTO_SCRAPE_ON_STARTUP=false
```

## Notes

- All code is in English only.
- Database creation and table migration run automatically when backend starts.
- No manual migration commands needed for basic use.
- Set `AUTO_SCRAPE_ON_STARTUP=true` if you want scrape to start with the backend.
