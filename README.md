# LinkedIn Stealth Automation API

A production-ready LinkedIn automation service built with Python, FastAPI, and Selenium with stealth capabilities to bypass anti-bot detection.

## 🚀 Features

- **Stealth Browsing**: Uses undetected-chromedriver and selenium-stealth to avoid detection
- **Session Persistence**: Maintains browser sessions across API requests
- **Dynamic UI Handling**: Adapts to different LinkedIn UI layouts and patterns
- **RESTful API**: Clean FastAPI endpoints for all operations
- **Robust Error Handling**: Comprehensive error handling and logging
- **Modular Architecture**: Well-organized, maintainable code structure

## 📁 Project Structure

```
linkedin_automation/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── logs/                           # Application logs
├── linkedin_automation/            # Main package
│   ├── __init__.py
│   ├── core/                       # Core automation logic
│   │   ├── __init__.py
│   │   ├── browser_manager.py      # Browser session management
│   │   ├── linkedin_auth.py        # LinkedIn authentication
│   │   ├── profile_handler.py      # Profile interactions
│   │   └── message_handler.py      # Messaging functionality
│   ├── api/                        # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── endpoints.py            # API route definitions
│   │   └── models.py               # Pydantic request/response models
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── logger.py               # Logging configuration
│       └── config.py               # Configuration management
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Windows/Linux/MacOS

### Installation

1. **Clone/Download the project**
   ```bash
   # Navigate to your project directory
   cd "d:\bappu paapu\abex_python backend_task"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env file with your settings if needed
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 📚 API Endpoints

The API provides 7 endpoints for LinkedIn automation:

### 1. Health Check
```http
GET /api/v1/health
```
**Response:** API status and timestamp

### 2. Login to LinkedIn
```http
POST /api/v1/login
Content-Type: application/json

{
    "email": "your_linkedin_email@example.com",
    "password": "your_password"
}
```

### 3. Send Connection Request
```http
POST /api/v1/connect
Content-Type: application/json

{
    "profile_url": "https://www.linkedin.com/in/someone",
    "message": "Optional connection message"
}
```

### 4. Check Connection Status
```http
POST /api/v1/check_connection
Content-Type: application/json

{
    "profile_url": "https://www.linkedin.com/in/someone"
}
```

### 5. Get Session Information
```http
GET /api/v1/session_info
```

### 6. Close Browser Session
```http
GET /api/v1/close
```

### 7. Root Endpoint
```http
GET /
```
**Response:** Welcome message

## 🧪 Testing the API

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Access interactive documentation:**
   ```
   http://localhost:8000/docs
   ```

3. **Test endpoints using the FastAPI interface or cURL commands**

## 🔧 Development Status

- [x] Project structure setup
- [x] Browser session management with stealth features
- [x] LinkedIn authentication with robust error handling
- [x] Profile interactions and connection requests
- [x] Message handling with realistic typing behavior
- [x] Complete API endpoints (7 endpoints)
- [x] Comprehensive error handling & logging
- [x] Documentation & testing suite
- [x] **🎉 PROJECT COMPLETE AND READY FOR SUBMISSION**

## 🚨 Important Notes

- This tool is for educational and legitimate automation purposes only
- Respect LinkedIn's Terms of Service and rate limits
- Use responsibly and ethically
- Consider LinkedIn's robots.txt and API guidelines

## 📝 License

This project is for educational purposes. Please use responsibly.
