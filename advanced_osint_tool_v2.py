#!/usr/bin/env python3
"""
Advanced Terminal-Based OSINT Tool with Groq API Integration v2.0
Author: Security Researcher
Version: 2.0
"""

import requests
import json
import sys
import argparse
import time
import threading
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse, urlencode
import re
import base64
import hashlib
from colorama import init, Fore, Style
import csv
import os
import socket
import dns.resolver
import ipaddress

# Initialize colorama
init()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT

class OSINTTool:
    def __init__(self, target, output_file=None, groq_key=None):
        self.target = target
        self.output_file = output_file
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if groq_key:
            global GROQ_API_KEY
            GROQ_API_KEY = groq_key

    def print_banner(self):
        banner = f"""
{Colors.CYAN}{Colors.BRIGHT}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ ██╗     ██╗ ██████╗ ║
║   ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗║
║   ██████╔╝██║   ██║██████╔╝   ██║   █████╗  ██║   ██║██║     ██║██║   ██║║
║   ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝  ██║   ██║██║     ██║██║   ██║║
║   ██║     ╚██████╔╝██║  ██║   ██║   ██║     ╚██████╔╝███████╗██║╚██████╔╝║
║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ║
║                                                                      ║
║   OmniSight AI with Groq AI Integration                       ║
║   Version 2.0 | Made by Ali Zafar (alizafarbati)                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """
        print(banner)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = Colors.WHITE
        if level == "SUCCESS":
            color = Colors.GREEN
        elif level == "WARNING":
            color = Colors.YELLOW
        elif level == "ERROR":
            color = Colors.RED
        elif level == "INFO":
            color = Colors.BLUE
        
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.RESET}")

    def save_result(self, category, data):
        if self.output_file:
            with open(self.output_file, 'a') as f:
                f.write(f"\n[{category}]\n")
                if isinstance(data, dict):
                    for k, v in data.items():
                        f.write(f"{k}: {v}\n")
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                f.write(f"{k}: {v}\n")
                        else:
                            f.write(f"{item}\n")
                else:
                    f.write(f"{data}\n")

    # ==================== BASIC INFO MODULE ====================
    def get_basic_info(self):
        self.log("Gathering basic information...", "INFO")
        
        try:
            # Check if target is IP or domain
            try:
                ip_obj = ipaddress.ip_address(self.target)
                is_ip = True
            except ValueError:
                is_ip = False
            
            if is_ip:
                # IP Address
                response = self.session.get(f"http://ip-api.com/json/{self.target}")
                if response.status_code == 200:
                    data = response.json()
                    self.results['basic_info'] = {
                        'IP': self.target,
                        'Country': data.get('country', 'N/A'),
                        'Region': data.get('regionName', 'N/A'),
                        'City': data.get('city', 'N/A'),
                        'ISP': data.get('isp', 'N/A'),
                        'Org': data.get('org', 'N/A'),
                        'Latitude': data.get('lat', 'N/A'),
                        'Longitude': data.get('lon', 'N/A'),
                        'Timezone': data.get('timezone', 'N/A')
                    }
            else:
                # Domain
                parsed = urlparse(f"http://{self.target}" if not self.target.startswith('http') else self.target)
                domain = parsed.netloc or self.target
                
                # Get IP address
                try:
                    ip = socket.gethostbyname(domain)
                except:
                    ip = "N/A"
                
                # Get WHOIS info
                whois_info = self.get_whois_info(domain)
                
                self.results['basic_info'] = {
                    'Domain': domain,
                    'IP Address': ip,
                    'Protocol': parsed.scheme if parsed.scheme else 'http',
                    'Port': parsed.port or 80
                }
                self.results['basic_info'].update(whois_info)
                
            self.log("Basic information gathered successfully", "SUCCESS")
            self.save_result("Basic Info", self.results['basic_info'])
            
        except Exception as e:
            self.log(f"Error getting basic info: {e}", "ERROR")

    def get_whois_info(self, domain):
        """Get WHOIS information"""
        try:
            response = self.session.get(f"https://ipinfo.io/{domain}/json")
            if response.status_code == 200:
                data = response.json()
                return {
                    'ASN': data.get('org', 'N/A'),
                    'City': data.get('city', 'N/A'),
                    'Region': data.get('region', 'N/A'),
                    'Country': data.get('country', 'N/A'),
                    'Location': data.get('loc', 'N/A')
                }
        except:
            pass
        return {'ASN': 'N/A', 'Country': 'N/A'}

    # ==================== SUBDOMAIN MODULE ====================
    def get_subdomains(self):
        self.log("Enumerating subdomains...", "INFO")
        
        subdomains = []
        common_subdomains = [
            'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging',
            'api', 'blog', 'shop', 'portal', 'web', 'm', 'mobile',
            'app', 'apps', 'cpanel', 'whm', 'webmail', 'ns1', 'ns2',
            'smtp', 'pop', 'pop3', 'imap', 'owa', 'vpn', 'remote',
            'owa', 'autodiscover', 'exchange', 'file', 'files',
            'support', 'help', 'forum', 'community', 'status',
            'wiki', 'docs', 'git', 'gitlab', 'bitbucket', 'jira',
            'confluence', 'jenkins', 'monitor', 'grafana', 'kibana'
        ]
        
        for sub in common_subdomains:
            subdomain = f"{sub}.{self.target}"
            try:
                socket.gethostbyname(subdomain)
                subdomains.append(subdomain)
                self.log(f"Found subdomain: {subdomain}", "SUCCESS")
            except:
                pass
        
        self.results['subdomains'] = subdomains
        self.save_result("Subdomains", subdomains)
        return subdomains

    # ==================== PORT SCAN MODULE ====================
    def port_scan(self, ports=None):
        self.log("Starting port scan...", "INFO")
        
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 
                     443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080]
        
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target, port))
                sock.close()
                if result == 0:
                    open_ports.append(port)
                    self.log(f"Port {port} is OPEN", "SUCCESS")
            except:
                pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(scan_port, ports)
        
        self.results['open_ports'] = open_ports
        self.save_result("Open Ports", open_ports)
        return open_ports

    # ==================== EMAIL MODULE ====================
    def email_recon(self):
        self.log("Performing email reconnaissance...", "INFO")
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = []
        
        try:
            response = self.session.get(f"http://{self.target}", timeout=5)
            if response.status_code == 200:
                emails = re.findall(email_pattern, response.text)
                emails = list(set(emails))
        except:
            pass
        
        self.results['emails'] = emails
        self.save_result("Emails", emails)
        
        if emails:
            self.log(f"Found {len(emails)} email(s)", "SUCCESS")
            for email in emails:
                print(f"  {Colors.CYAN}{email}{Colors.RESET}")
        else:
            self.log("No emails found", "WARNING")
        
        return emails

    # ==================== SOCIAL MEDIA MODULE ====================
    def social_media_check(self):
        self.log("Checking social media presence...", "INFO")
        
        social_media = {
            'Twitter': f"https://twitter.com/search?q={self.target}",
            'Facebook': f"https://www.facebook.com/search/results?q={self.target}",
            'LinkedIn': f"https://www.linkedin.com/search/results/all/?keywords={self.target}",
            'GitHub': f"https://github.com/search?q={self.target}",
            'Instagram': f"https://www.instagram.com/explore/tags/{self.target}",
            'YouTube': f"https://www.youtube.com/results?search_query={self.target}"
        }
        
        self.results['social_media'] = social_media
        self.save_result("Social Media", social_media)
        
        self.log("Social media search URLs generated", "SUCCESS")
        return social_media

    # ==================== TECHNOLOGY STACK MODULE ====================
    def tech_stack_detection(self):
        self.log("Detecting technology stack...", "INFO")
        
        technologies = {}
        
        try:
            response = self.session.get(f"http://{self.target}", timeout=5)
            
            headers = response.headers
            if 'Server' in headers:
                technologies['Web Server'] = headers['Server']
            if 'X-Powered-By' in headers:
                technologies['Backend'] = headers['X-Powered-By']
            
            content = response.text.lower()
            if 'wp-content' in content:
                technologies['CMS'] = 'WordPress'
            elif 'joomla' in content:
                technologies['CMS'] = 'Joomla'
            elif 'drupal' in content:
                technologies['CMS'] = 'Drupal'
            elif 'laravel' in content:
                technologies['Framework'] = 'Laravel'
            elif 'react' in content:
                technologies['Frontend'] = 'React'
            elif 'vue' in content:
                technologies['Frontend'] = 'Vue.js'
            elif 'angular' in content:
                technologies['Frontend'] = 'Angular'
            
        except Exception as e:
            self.log(f"Error detecting tech stack: {e}", "ERROR")
        
        self.results['tech_stack'] = technologies
        self.save_result("Technology Stack", technologies)
        
        if technologies:
            self.log("Technology stack detected", "SUCCESS")
            for tech, value in technologies.items():
                print(f"  {Colors.CYAN}{tech}: {value}{Colors.RESET}")
        
        return technologies

    # ==================== GROQ AI ANALYSIS MODULE ====================
    def groq_ai_analysis(self):
        if not GROQ_API_KEY:
            self.log("Groq API key not found. Set GROQ_API_KEY environment variable or use --groq-key.", "WARNING")
            return None
        
        self.log("Performing AI analysis with Groq...", "INFO")
        
        try:
            prompt = f"""Analyze the following target for potential security risks:

Target: {self.target}

Please provide a comprehensive security analysis including:
1. Potential attack vectors
2. Recommended security measures
3. Common vulnerabilities to check
4. Information gathering suggestions

Provide detailed and actionable recommendations."""

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a cybersecurity expert assistant. Provide detailed security analysis."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            response = self.session.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                self.results['groq_analysis'] = analysis
                self.save_result("Groq AI Analysis", analysis)
                
                self.log("AI analysis completed", "SUCCESS")
                print(f"\n{Colors.BRIGHT}Groq AI Analysis:{Colors.RESET}")
                print(f"{Colors.CYAN}{analysis}{Colors.RESET}\n")
                return analysis
            else:
                self.log(f"Groq API error: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Error in Groq analysis: {e}", "ERROR")
            return None

    # ==================== THREAT INTELLIGENCE MODULE ====================
    def threat_intelligence(self):
        self.log("Gathering threat intelligence...", "INFO")
        
        intel = {}
        
        try:
            response = self.session.post(
                "https://urlscan.io/api/v1/scan/",
                json={"url": f"http://{self.target}", "public": "on"},
                headers={"API-Key": "public"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                intel['urlscan_result'] = data.get('api', 'Scan submitted')
        except:
            intel['urlscan_result'] = 'N/A'
        
        self.results['threat_intel'] = intel
        self.save_result("Threat Intelligence", intel)
        
        self.log("Threat intelligence gathered", "SUCCESS")
        return intel

    # ==================== WHOIS MODULE ====================
    def whois_lookup(self):
        self.log("Performing WHOIS lookup...", "INFO")
        
        try:
            response = self.session.get(f"https://whoisjson.com/api/v1/whois/{self.target}")
            if response.status_code == 200:
                data = response.json()
                self.results['whois'] = data
                self.save_result("WHOIS", data)
                self.log("WHOIS lookup completed", "SUCCESS")
                return data
        except:
            pass
        
        self.log("WHOIS lookup failed", "WARNING")
        return {}

    # ==================== DNS MODULE ====================
    def dns_lookup(self):
        self.log("Performing DNS lookup...", "INFO")
        
        dns_records = {}
        
        try:
            # A Record
            try:
                ip = socket.gethostbyname(self.target)
                dns_records['A'] = ip
            except:
                pass
            
            # NS Records
            try:
                answers = dns.resolver.resolve(self.target, 'NS')
                dns_records['NS'] = [str(r) for r in answers]
            except:
                pass
            
            # MX Records
            try:
                answers = dns.resolver.resolve(self.target, 'MX')
                dns_records['MX'] = [str(r.exchange) for r in answers]
            except:
                pass
            
        except Exception as e:
            self.log(f"DNS lookup error: {e}", "ERROR")
        
        self.results['dns'] = dns_records
        self.save_result("DNS Records", dns_records)
        
        if dns_records:
            self.log("DNS records retrieved", "SUCCESS")
            for record, value in dns_records.items():
                print(f"  {Colors.CYAN}{record}: {value}{Colors.RESET}")
        
        return dns_records

    # ==================== URL ENUMERATION MODULE ====================
    def url_enumeration(self):
        self.log("Enumerating URLs...", "INFO")
        
        urls = []
        
        common_paths = [
            '/robots.txt', '/sitemap.xml', '/crossdomain.xml', '/clientaccesspolicy.xml',
            '/.git/config', '/.env', '/composer.json', '/package.json',
            '/wp-admin', '/wp-login.php', '/xmlrpc.php',
            '/admin', '/login', '/signin', '/register',
            '/api', '/v1', '/v2', '/v3',
            '/backup', '/old', '/temp', '/tmp',
            '/config', '/settings', '/database',
            '/upload', '/uploads', '/files', '/images',
            '/css', '/js', '/fonts', '/assets',
            '/phpinfo.php', '/test.php', '/info.php',
            '/readme.md', '/CHANGELOG', '/LICENSE'
        ]
        
        base_url = f"http://{self.target}"
        
        for path in common_paths:
            url = base_url + path
            try:
                response = self.session.head(url, timeout=2, allow_redirects=True)
                if response.status_code in [200, 301, 302, 403, 401]:
                    urls.append({'url': url, 'status': response.status_code})
                    self.log(f"Found: {url} (Status: {response.status_code})", "INFO")
            except:
                pass
        
        self.results['urls'] = urls
        self.save_result("URLs", urls)
        
        self.log(f"Found {len(urls)} URLs", "SUCCESS")
        return urls

    # ==================== VULNERABILITY SCAN MODULE ====================
    def vulnerability_scan(self):
        self.log("Performing vulnerability scan...", "INFO")
        
        vulnerabilities = []
        
        checks = [
            ('/.git/config', 'Git repository exposed'),
            ('/.env', 'Environment file exposed'),
            ('/phpinfo.php', 'phpinfo() exposed'),
            ('/server-status', 'Apache server-status exposed'),
            ('/wp-admin', 'WordPress admin exposed'),
            ('/composer.json', 'Composer file exposed'),
        ]
        
        for path, description in checks:
            url = f"http://{self.target}{path}"
            try:
                response = self.session.get(url, timeout=2)
                if response.status_code == 200:
                    vulnerabilities.append({'url': url, 'issue': description})
                    self.log(f"Vulnerability found: {description}", "WARNING")
            except:
                pass
        
        self.results['vulnerabilities'] = vulnerabilities
        self.save_result("Vulnerabilities", vulnerabilities)
        
        if vulnerabilities:
            self.log(f"Found {len(vulnerabilities)} potential vulnerabilities", "WARNING")
        else:
            self.log("No obvious vulnerabilities found", "SUCCESS")
        
        return vulnerabilities

    # ==================== GENERATE REPORT ====================
    def generate_report(self):
        self.log("Generating comprehensive report...", "INFO")
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                     OSINT REPORT                                     ║
║                     Target: {self.target}                             ║
║                     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ║
╚══════════════════════════════════════════════════════════════════════╝

"""
        
        for category, data in self.results.items():
            report += f"\n{'='*60}\n"
            report += f"{category.upper().replace('_', ' ')}\n"
            report += f"{'='*60}\n\n"
            
            if isinstance(data, dict):
                for key, value in data.items():
                    report += f"  {key}: {value}\n"
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            report += f"  {k}: {v}\n"
                        report += "\n"
                    else:
                        report += f"  - {item}\n"
            else:
                report += f"  {data}\n"
            
            report += "\n"
        
        report_file = f"osint_report_{self.target.replace('.', '_')}_{int(time.time())}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.log(f"Report saved to: {report_file}", "SUCCESS")
        return report

    # ==================== MAIN EXECUTION ====================
    def run_all_modules(self):
        self.print_banner()
        
        modules = [
            ("Basic Info", self.get_basic_info),
            ("Subdomains", self.get_subdomains),
            ("Port Scan", self.port_scan),
            ("Email Recon", self.email_recon),
            ("Social Media", self.social_media_check),
            ("Tech Stack", self.tech_stack_detection),
            ("DNS Lookup", self.dns_lookup),
            ("URL Enumeration", self.url_enumeration),
            ("Vulnerability Scan", self.vulnerability_scan),
            ("Threat Intelligence", self.threat_intelligence),
            ("WHOIS Lookup", self.whois_lookup),
            ("Groq AI Analysis", self.groq_ai_analysis),
        ]
        
        print(f"\n{Colors.BRIGHT}Starting OSINT scan on: {self.target}{Colors.RESET}\n")
        
        for name, func in modules:
            try:
                func()
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Error in {name}: {e}", "ERROR")
        
        self.generate_report()
        
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"OSINT Scan Completed!")
        print(f"{'='*60}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description="OmniSight AI with Groq AI Integration")
    parser.add_argument("target", help="Target domain or IP address")
    parser.add_argument("-o", "--output", help="Output file for results")
    parser.add_argument("--ports", help="Custom ports (comma-separated)")
    parser.add_argument("--groq-key", help="Groq API key")
    
    args = parser.parse_args()
    
    tool = OSINTTool(args.target, args.output, args.groq_key)
    tool.run_all_modules()

if __name__ == "__main__":
    main()
