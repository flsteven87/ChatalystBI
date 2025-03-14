# ChatalystBI

A smart business intelligence platform that offers AI-powered analytics through a conversational interface.

## Overview

ChatalystBI transforms how you interact with business data by combining the power of Large Language Models with data visualization capabilities. Users can simply chat with the system to analyze data, generate insights, and create visualizations without technical expertise.

## Architecture

### Frontend
- Built with Next.js, React 19, and Tailwind CSS
- Responsive chat interface with support for text and visualization rendering
- Modern UI with optimized performance

### Backend
- FastAPI framework for high-performance API endpoints
- LLM integration using OpenAI and CrewAI
- Data processing and visualization generation capabilities
- RESTful API design

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Poetry (for Python dependency management)

### Installation

#### Backend Setup
```bash
cd backend
poetry install
cp .env.example .env  # Update with your API keys
poetry run python -m app.main
```

#### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local  # Configure environment variables
npm run dev
```

## Usage

1. Navigate to `http://localhost:3000` in your browser
2. Start a new conversation with ChatalystBI
3. Ask questions about your business data
4. View generated visualizations and insights directly in the chat

## Development

### Backend Development
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## License

MIT 