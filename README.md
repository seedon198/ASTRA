# ASTRA – Global Attack Surface Tracker

Real-time cybersecurity exposure visualization powered by multiple threat intelligence APIs

ASTRA provides an interactive dashboard showing global attack surfaces with a cyberpunk-themed interface, featuring live exposure data by country and organization from Shodan Pro, GreyNoise, and VirusTotal.

## Features

- Multi-API Intelligence - Combines Shodan Pro, GreyNoise, and VirusTotal data
- Interactive World Map - D3.js powered visualization with neon styling
- Real-time Leaderboards - Country and organization exposure rankings  
- Automated Data Collection - GitHub Actions running every 15 minutes
- Cyberpunk Aesthetic - Neon colors, futuristic design, dark theme

## Data Sources

- Shodan Pro API - Device and service discovery, exposure statistics
- GreyNoise API - Threat intelligence and malicious activity tracking
- VirusTotal API - Malware analysis and domain reputation

## Project Structure

```
├── data/                     # JSON data files
├── frontend/                 # Static dashboard
│   ├── index.html           # Main dashboard page
│   ├── styles.css           # Neon cyberpunk styling
│   └── app.js               # Map and leaderboard logic
├── scripts/                  # Data collection
│   └── fetch_data.py        # Shodan API integration
└── .github/workflows/        # Automation
    └── data-fetch.yml       # 15-minute data updates
```

## Setup

1. **API Configuration**
   ```bash
   # Set your API keys as GitHub secrets:
   # Repository Settings > Secrets and Variables > Actions
   # - SHODAN_API_KEY (Shodan Pro)
   # - GREYNOISE_API_KEY (GreyNoise Free)
   # - VIRUSTOTAL_API_KEY (VirusTotal Free)
   ```

2. **Local Development**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   export SHODAN_API_KEY="your_shodan_pro_key_here"
   export GREYNOISE_API_KEY="your_greynoise_key_here"
   export VIRUSTOTAL_API_KEY="your_virustotal_key_here"
   
   # Run data fetcher
   python scripts/fetch_data.py
   
   # Serve frontend locally
   python -m http.server 8000
   # Visit http://localhost:8000/frontend/
   ```

3. **GitHub Actions**
   - Automatically fetches data every 15 minutes
   - Commits updates to `data/latest.json`
   - Requires all three API keys configured as secrets
   - Respects rate limits for free tier APIs

## Technology Stack

## Technology Stack

- Frontend: HTML5, CSS3, JavaScript (D3.js, TopoJSON)
- Backend: Python (requests, json, shodan, pygreynoise)
- Automation: GitHub Actions
- Data Sources: Shodan Pro API, GreyNoise API, VirusTotal API
- Deployment: Static hosting compatible

## Security and Rate Limits

- API keys are stored as GitHub secrets
- Sensitive files are excluded via .gitignore
- Rate limiting implemented for all APIs:
  - VirusTotal: 4 requests/minute (free tier)
  - GreyNoise: API-specific limits
  - Shodan Pro: Higher rate limits than free tier
- All external data is validated before processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the cyberpunk design guidelines
4. Test with sample data
5. Submit a pull request

## License

MIT License - See LICENSE file for details
