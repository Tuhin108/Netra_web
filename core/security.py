"""
Security utilities for URL validation, sanitization, and request security.
"""
import re
import ipaddress
from urllib.parse import urlparse
from typing import Optional, List

# Allowed URL schemes
ALLOWED_SCHEMES = {'http', 'https'}

# Suspicious patterns for XSS detection
SUSPICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'vbscript:',
    r'on\w+\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
    r'<form',
    r'<input[^>]*type\s*=\s*["\']?password["\']?',
]

# Compile patterns for performance
SUSPICIOUS_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]

# Private IP ranges for SSRF protection
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('fe80::/10'),
    ipaddress.ip_network('fc00::/7'),
]


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate URL for security issues.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "Invalid URL format"
    
    try:
        parsed = urlparse(url.strip())
        
        # Check scheme
        if not parsed.scheme:
            return False, "Missing URL scheme"
        
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            return False, f"Unsupported scheme: {parsed.scheme}"
        
        # Check netloc
        if not parsed.netloc:
            return False, "Missing hostname"
        
        # Check for suspicious patterns
        for pattern in SUSPICIOUS_REGEX:
            if pattern.search(url):
                return False, "URL contains suspicious patterns"
        
        # Check hostname format
        hostname = parsed.netloc.lower()
        if not re.match(r'^[a-z0-9.-]+$', hostname):
            return False, "Invalid hostname format"
        
        # Check for localhost and private IPs
        if hostname in ['localhost', '127.0.0.1']:
            return False, "Localhost access not allowed"
        
        # Check for IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
            if any(ip in network for network in PRIVATE_IP_RANGES):
                return False, "Private IP access not allowed"
        except ValueError:
            # Not an IP address, continue
            pass
        
        return True, None
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"


def sanitize_url(url: str) -> str:
    """
    Sanitize URL by removing dangerous characters and normalizing.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL
    """
    if not url:
        return ""
    
    # Remove control characters
    url = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', url)
    
    # Normalize whitespace
    url = url.strip()
    
    # Ensure proper encoding
    try:
        from urllib.parse import quote
        # Basic URL encoding for special characters
        url = quote(url, safe='/:@!$&\'()*+,;=')
    except:
        pass
    
    return url


def is_safe_hostname(hostname: str) -> bool:
    """
    Check if hostname is safe (not private/local).
    
    Args:
        hostname: Hostname to check
        
    Returns:
        True if safe, False otherwise
    """
    if not hostname:
        return False
    
    hostname = hostname.lower()
    
    # Check for localhost
    if hostname in ['localhost', '127.0.0.1']:
        return False
    
    # Check for private IP ranges
    try:
        ip = ipaddress.ip_address(hostname)
        return not any(ip in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        # Domain name, check for suspicious patterns
        suspicious_keywords = ['localhost', 'internal', 'private', 'local']
        return not any(keyword in hostname for keyword in suspicious_keywords)


def get_safe_request_config() -> dict:
    """
    Get safe HTTP request configuration.
    
    Returns:
        Dictionary with safe request settings
    """
    return {
        'timeout': 8.0,
        'follow_redirects': True,
        'max_redirects': 10,
        'verify': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }


def detect_xss_payloads(content: str) -> List[str]:
    """
    Detect potential XSS payloads in content.
    
    Args:
        content: Content to scan
        
    Returns:
        List of detected XSS patterns
    """
    if not content:
        return []
    
    detected = []
    for pattern in SUSPICIOUS_REGEX:
        matches = pattern.findall(content)
        if matches:
            detected.extend(matches)
    
    return detected
