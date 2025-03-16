# ChatalystBI

A smart business intelligence platform that offers AI-powered analytics through a conversational interface.

## Overview

ChatalystBI transforms how you interact with business data by combining the power of Large Language Models with data visualization capabilities. Users can simply chat with the system to analyze data, generate insights, and create visualizations without technical expertise.

## Features

- **Natural Language Interface**: Ask questions about your data in plain language
- **AI-Powered Analytics**: Leverage LLMs to analyze and interpret data
- **Automated Visualizations**: Generate charts and graphs based on conversation context
- **Simplified User Experience**: No SQL or programming knowledge required

## Technology Stack

- **Backend**: FastAPI for high-performance API endpoints
- **AI Integration**: OpenAI and CrewAI for intelligent processing
- **Frontend**: Streamlit for a simple, interactive user interface
- **Data Visualization**: Matplotlib and custom visualization tools

## Architecture

The application follows a clean architecture with these components:

```
ChatalystBI/
├── app/                  # Backend application code
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration and setup
│   ├── db/               # Database connections and models
│   ├── models/           # Data models
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic services
│   ├── static/           # Static files (images, etc.)
│   ├── tools/            # Helper tools and utilities
│   └── utils/            # Utility functions
├── streamlit_app.py      # Streamlit frontend application
├── requirements.txt      # Python dependencies
└── .env.example          # Example environment variables
```

## Getting Started

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ChatalystBI.git
cd ChatalystBI

# Create and activate virtual environment
python -m venv venv
# On Windows
# venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys
```

## Usage

### Start the FastAPI server:
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start the API server
uvicorn app.main:app --reload
```

### Start the Streamlit interface:
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start the Streamlit interface
streamlit run streamlit_app.py
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 