# Cyber Security URL Scanner

A modern Flask-based web application for scanning and analyzing URLs for security threats, featuring a Bladerunner 2049-inspired cyberpunk interface.

![Bladerunner 2049 Theme](https://img.shields.io/badge/Theme-Bladerunner%202049-00ffff?style=for-the-badge&logo=blender&logoColor=white&color=00ffff&labelColor=0a0a1a)

## 🚀 Features

- **Real-time URL Scanning**: Analyze URLs for security threats and redirect chains
- **Bladerunner 2049 UI**: Immersive cyberpunk interface with neon effects and holographic elements
- **Progress Tracking**: Real-time progress updates during scans
- **Security Verdicts**: Comprehensive threat assessment with safety scores
- **API Support**: Programmatic access to scanning functionality
- **Responsive Design**: Optimized for desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Flask 2.3.3 with Python
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom Bladerunner 2049 theme with CSS animations
- **Networking**: HTTPX for URL analysis
- **Security**: Custom threat detection algorithms

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cyber-check
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

4. **Run the application**
   ```bash
   python web_app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎨 UI Features

### Bladerunner 2049 Theme
- Neon blue and pink color scheme
- Holographic grid background patterns
- Cyberpunk typography with Orbitron font
- Animated neon glow effects
- Responsive cyber interface elements

### Interactive Elements
- Real-time progress bars with cyber animations
- Hover effects with neon glows
- Smooth transitions and animations
- Mobile-optimized responsive design

## 🔧 Configuration

### Environment Variables
Create a `.env` file for custom configuration:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Security Settings
The application uses several security mechanisms:
- URL validation and sanitization
- Threat intelligence integration
- Custom security rules engine
- Real-time threat detection

## 📊 API Usage

### Scan a URL
```bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Response Format
```json
{
  "url": "https://example.com",
  "trace_result": {
    "input_url": "https://example.com",
    "final_url": "https://example.com",
    "hops": [...],
    "content_type": "text/html",
    "has_login_form": false,
    "errors": []
  },
  "verdict": {
    "label": "SAFE",
    "score": 95,
    "reasons": ["Valid SSL certificate", "No suspicious redirects"]
  }
}
```

## 🎯 Usage

1. **Enter URL**: Type or paste the URL you want to scan in the input field
2. **Start Scan**: Click the "Scan URL" button to begin analysis
3. **Monitor Progress**: Watch real-time progress updates with cyber animations
4. **View Results**: See detailed security analysis and threat assessment
5. **Take Action**: Follow recommended security actions based on the verdict

## 🏗️ Project Structure

```
cyber-check/
├── web_app.py          # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── core/              # Core scanning functionality
│   ├── __init__.py
│   ├── scanner.py     # URL scanning logic
│   ├── models.py      # Data models
│   ├── rules.py       # Security rules
│   ├── security.py    # Security utilities
│   ├── urlhaus.py     # Threat intelligence
│   └── html_redirects.py
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   └── error.html
├── static/           # Static assets
│   ├── css/
│   │   └── style.css # Bladerunner theme
│   ├── js/
│   │   └── app.js    # Frontend logic
│   └── favicon.ico
└── resources/        # Security resources
    ├── denylist.txt
    └── suspicious_tlds.txt
```

## 🔍 Core Components

### Scanner Module (`core/scanner.py`)
- URL tracing and redirect analysis
- Content type detection
- Security threat assessment
- Progress callback system

### Security Rules (`core/rules.py`)
- Custom threat detection rules
- Score-based verdict system
- Real-time threat intelligence

### UI Components
- **Base Template**: Common layout with cyber theme
- **Index Page**: URL input form with Bladerunner styling
- **Results Page**: Detailed security analysis display
- **Error Handling**: Cyber-themed error pages

## 🎨 Theme Customization

The Bladerunner 2049 theme uses CSS custom properties for easy customization:

```css
:root {
  --neon-blue: #00ffff;
  --neon-pink: #ff00ff;
  --neon-orange: #ff7700;
  --cyber-purple: #8a2be2;
  --dark-bg: #0a0a1a;
  --text-primary: #e0e0ff;
  /* ... more variables */
}
```

## 🚀 Deployment

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Using eventlet for WebSocket support
gunicorn -k eventlet -w 4 -b 0.0.0.0:5000 web_app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-k", "eventlet", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `web_app.py` or use `FLASK_PORT` environment variable
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **CSS not loading**: Check static file serving configuration

### Debug Mode
Enable debug mode for detailed error information:
```bash
export FLASK_DEBUG=True
python web_app.py
```

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the code comments for implementation details

---

**Built with ❤️ and cyberpunk aesthetics**
