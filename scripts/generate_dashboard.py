#!/usr/bin/env python3
"""
ASTRA Dashboard Generator
Generates a professional README.md dashboard from collected threat intelligence data
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

class AstraDashboardGenerator:
    def __init__(self, data_file: str = "data/latest.json"):
        self.data_file = data_file
        self.root_dir = os.path.dirname(os.path.dirname(__file__))
        
    def load_data(self) -> Dict[str, Any]:
        """Load the latest threat intelligence data"""
        data_path = os.path.join(self.root_dir, self.data_file)
        
        try:
            with open(data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Data file {data_path} not found. Using placeholder data.")
            return self._get_placeholder_data()
    
    def _get_placeholder_data(self) -> Dict[str, Any]:
        """Fallback data structure"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "data_sources": ["Shodan Pro", "GreyNoise", "VirusTotal"],
            "countries": {},
            "organizations": {},
            "global_stats": {
                "total_exposed_services": 0,
                "total_critical_vulns": 0,
                "total_threat_activity": 0,
                "malicious_domains": 0,
                "suspicious_domains": 0
            },
            "api_status": {
                "shodan": "inactive",
                "greynoise": "inactive",
                "virustotal": "inactive"
            }
        }
    
    def generate_header(self, data: Dict[str, Any]) -> str:
        """Generate enhanced dashboard header with working badges"""
        last_updated = data.get("last_updated", "Unknown")
        # Fix the badge URL to use the correct repository
        encoded_time = last_updated.replace(' ', '%20').replace(':', '%3A')
        
        header = f"""# ASTRA - Global Attack Surface Tracker

<div align="center">

![ASTRA Logo](https://img.shields.io/badge/ASTRA-Global%20Attack%20Surface%20Tracker-2ea44f?style=for-the-badge&logo=shield)

**Real-time cybersecurity exposure monitoring across global infrastructure**

[![Data Status](https://img.shields.io/badge/Data-Live-brightgreen?style=flat-square)](https://github.com/seedon198/ASTRA)
[![Last Updated](https://img.shields.io/badge/Updated-{encoded_time}-blue?style=flat-square)](https://github.com/seedon198/ASTRA)
[![APIs Active](https://img.shields.io/badge/APIs-{len(data.get("data_sources", []))}-success?style=flat-square)](https://github.com/seedon198/ASTRA)
[![Auto Update](https://img.shields.io/badge/Auto%20Update-15min-orange?style=flat-square)](https://github.com/seedon198/ASTRA)

</div>

---

## 🌍 Global Threat Intelligence Dashboard

> **Last Updated:** `{last_updated}`  
> **Data Sources:** {" • ".join(data.get("data_sources", []))}  
> **Coverage:** {len(data.get("countries", {}))} Countries • {len(data.get("organizations", {}))} Organizations

---

"""
        return header
    
    def generate_global_stats(self, data: Dict[str, Any]) -> str:
        """Generate enhanced executive summary with visual elements"""
        stats = data.get("global_stats", {})
        
        def format_number(num):
            return f"{num:,}"
        
        exposed = stats.get("total_exposed_services", 0)
        vulns = stats.get("total_critical_vulns", 0)
        threats = stats.get("total_threat_activity", 0)
        malicious = stats.get("malicious_domains", 0)
        suspicious = stats.get("suspicious_domains", 0)
        
        section = f"""## 📊 Executive Summary

<table>
<tr>
<td align="center">

**🚨 CRITICAL ALERTS**
```
{format_number(vulns)}
```
Critical Vulnerabilities

</td>
<td align="center">

**🌐 EXPOSED SERVICES**
```
{format_number(exposed)}
```
Internet-Facing Assets

</td>
<td align="center">

**⚡ ACTIVE THREATS**
```
{format_number(threats)}
```
Live Attack Attempts

</td>
<td align="center">

**🦠 MALWARE DOMAINS**
```
{format_number(malicious)}
```
Confirmed Malicious

</td>
</tr>
</table>

---

## 🎯 Threat Intelligence Matrix

| **Risk Category** | **Count** | **Percentage** | **Trend** | **Source** | **Severity** |
|:------------------|----------:|:--------------:|:---------:|:-----------|:-------------|
| Exposed Services | {format_number(exposed)} | 100.0% | 📊 | Shodan Pro | ⚠️ **HIGH** |
| Critical Vulns | {format_number(vulns)} | {(vulns / exposed * 100) if exposed > 0 else 0:.1f}% | 📈 | Shodan Pro | 🔴 **CRITICAL** |
| Active Threats | {format_number(threats)} | {(threats / exposed * 100) if exposed > 0 else 0:.1f}% | 📈 | GreyNoise | 🔴 **CRITICAL** |
| Malicious Domains | {format_number(malicious)} | {(malicious / 100 * 100):.1f}% | 📊 | VirusTotal | 🔴 **CRITICAL** |
| Suspicious Domains | {format_number(suspicious)} | {(suspicious / 100 * 100):.1f}% | 📉 | VirusTotal | ⚠️ **HIGH** |

"""
        return section
    
    def generate_country_leaderboard(self, data: Dict[str, Any]) -> str:
        """Generate country exposure leaderboard"""
        countries = data.get("countries", {})
        
        if not countries:
            return "## Top Countries by Exposure\n\n*No country data available*\n\n"
        
        # Sort countries by exposed services
        sorted_countries = sorted(
            countries.items(), 
            key=lambda x: x[1].get("exposed_services", 0), 
            reverse=True
        )[:10]  # Top 10
        
        section = """## Top Countries by Exposure

| Rank | Country | Exposed Services | Critical Vulns | Threat Activity |
|------|---------|-----------------|----------------|-----------------|
"""
        
        for i, (country, stats) in enumerate(sorted_countries, 1):
            exposed = stats.get("exposed_services", 0)
            vulns = stats.get("critical_vulns", 0)
            threats = stats.get("threat_activity", 0)
            
            section += f"| {i} | **{country}** | {exposed:,} | {vulns:,} | {threats:,} |\n"
        
        section += "\n"
        return section
    
    def generate_organization_leaderboard(self, data: Dict[str, Any]) -> str:
        """Generate organization exposure leaderboard"""
        orgs = data.get("organizations", {})
        
        if not orgs:
            return "## Top Organizations by Exposure\n\n*No organization data available*\n\n"
        
        # Sort organizations by exposed services
        sorted_orgs = sorted(
            orgs.items(), 
            key=lambda x: x[1].get("exposed_services", 0), 
            reverse=True
        )
        
        section = """## Top Organizations by Exposure

| Rank | Organization | Exposed Services | Critical Vulns |
|------|-------------|-----------------|----------------|
"""
        
        for i, (org, stats) in enumerate(sorted_orgs, 1):
            exposed = stats.get("exposed_services", 0)
            vulns = stats.get("critical_vulns", 0)
            
            section += f"| {i} | **{org}** | {exposed:,} | {vulns:,} |\n"
        
        section += "\n"
        return section
    
    def generate_api_status(self, data: Dict[str, Any]) -> str:
        """Generate API status section"""
        api_status = data.get("api_status", {})
        data_sources = data.get("data_sources", [])
        
        section = """## Data Sources & API Status

| API | Status | Purpose |
|-----|--------|---------|
"""
        
        apis = {
            "shodan": "Device & Service Discovery",
            "greynoise": "Threat Intelligence",
            "virustotal": "Malware & Domain Analysis"
        }
        
        for api, purpose in apis.items():
            status = api_status.get(api, "unknown")
            status_badge = "🟢 Active" if status == "active" else "🔴 Inactive"
            section += f"| **{api.title()}** | {status_badge} | {purpose} |\n"
        
        section += f"\n**Active Data Sources:** {', '.join(data_sources)}\n\n"
        return section
    
    def generate_methodology(self) -> str:
        """Generate methodology section"""
        return """## Methodology

### Data Collection
- **Shodan Pro API**: Discovers internet-connected devices and services across global infrastructure
- **GreyNoise API**: Identifies malicious and benign internet scanning activity
- **VirusTotal API**: Analyzes domains and IPs for malware and suspicious activity

### Update Frequency
- Data refreshed every 15 minutes via automated GitHub Actions
- Real-time correlation across multiple threat intelligence sources
- Historical trending and anomaly detection

### Metrics Explanation
- **Exposed Services**: Internet-accessible services identified by Shodan
- **Critical Vulnerabilities**: High-severity security issues requiring immediate attention
- **Threat Activity**: Malicious scanning and attack attempts detected by GreyNoise
- **Domain Analysis**: Malware and phishing domains identified by VirusTotal

---

"""
    
    def generate_footer(self) -> str:
        """Generate dashboard footer"""
        return """## About ASTRA

ASTRA (Attack Surface Tracker & Risk Analyzer) provides automated threat intelligence monitoring for cybersecurity professionals. This dashboard aggregates data from multiple authoritative sources to deliver real-time insights into global attack surfaces.

### Repository Structure
```
├── data/                     # Threat intelligence data (JSON)
├── scripts/                  # Data collection and processing
├── .github/workflows/        # Automated data updates
└── README.md                # This dashboard
```

### Contributing
Contributions welcome. Please ensure all additions maintain professional presentation standards and follow established data processing patterns.

**Note**: This dashboard updates automatically. Manual edits to README.md will be overwritten during the next automated update cycle.
"""
    
    def generate_dashboard(self) -> str:
        """Generate the complete README.md dashboard"""
        data = self.load_data()
        
        dashboard = ""
        dashboard += self.generate_header(data)
        dashboard += self.generate_global_stats(data)
        dashboard += self.generate_country_leaderboard(data)
        dashboard += self.generate_organization_leaderboard(data)
        dashboard += self.generate_api_status(data)
        dashboard += self.generate_methodology()
        dashboard += self.generate_footer()
        
        return dashboard
    
    def save_dashboard(self, content: str, output_file: str = "README.md"):
        """Save the generated dashboard to README.md"""
        output_path = os.path.join(self.root_dir, output_file)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Dashboard generated and saved to {output_path}")

def main():
    """Main execution function"""
    generator = AstraDashboardGenerator()
    dashboard_content = generator.generate_dashboard()
    generator.save_dashboard(dashboard_content)
    print("ASTRA dashboard generation completed successfully")

if __name__ == "__main__":
    main()
