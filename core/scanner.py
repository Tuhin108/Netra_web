import httpx
import tldextract
from rapidfuzz import fuzz
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

from core.models import TraceHop, TraceResult, Verdict
from core.rules import (
    SUSPICIOUS_TLDS, REDIRECT_LIMIT, BRAND_NAMES, BRAND_SIMILARITY_THRESHOLD,
    SENSITIVE_INPUT_KEYWORDS, SCORE_SUSPICIOUS_TLD, SCORE_TOO_MANY_REDIRECTS,
    SCORE_DOMAIN_MISMATCH, SCORE_BRAND_LOOKALIKE, SCORE_SENSITIVE_FORM,
    SCORE_BINARY_DOWNLOAD, SCORE_URLHAUS_HIT, SCORE_NETWORK_ERROR
)
from core.urlhaus import check_urlhaus
from core.html_redirects import find_html_redirect

from typing import Callable

ProgressCallback = Callable[[float, str], None]

def _normalize_url(url: str) -> str:
    """Ensure URL has a scheme."""
    if not url.startswith(('http://', 'https://')):
        return f"https://{url}"
    return url

def _is_valid_url_scheme(url: str) -> bool:
    """Check if the URL scheme is either HTTP or HTTPS."""
    return url.startswith(('http://', 'https://'))

def _is_sensitive_form_present(soup: BeautifulSoup) -> bool:
    """Check for forms with sensitive input fields."""
    forms = soup.find_all('form')
    for form in forms:
        inputs = form.find_all('input')
        for input_tag in inputs:
            input_type = input_tag.get('type', '').lower()
            input_name = input_tag.get('name', '').lower()
            input_id = input_tag.get('id', '').lower()
            if input_type == 'password':
                return True
            for keyword in SENSITIVE_INPUT_KEYWORDS:
                if keyword in input_name or keyword in input_id:
                    return True
    return False

def scan_url(url: str, progress_callback: ProgressCallback, timeout_s: float = 8.0) -> tuple[TraceResult, Verdict]:
    """
    Performs a comprehensive safety scan on a given URL.
    """
    trace_result = TraceResult(input_url=url)
    verdict = Verdict(label="UNKNOWN", score=0)
    score = 0
    reasons = []

    try:
        # 1. Normalize & validate URL
        progress_callback(0.1, "Validating URL...")
        normalized_url = _normalize_url(url)
        if not _is_valid_url_scheme(normalized_url):
            trace_result.errors.append("Invalid URL scheme")
            verdict.label = "UNKNOWN"
            verdict.reasons.append("Invalid URL scheme")
            return trace_result, verdict
        
        parsed_url = urlparse(normalized_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            trace_result.errors.append("Invalid URL format")
            verdict.label = "UNKNOWN"
            verdict.reasons.append("Invalid URL")
            return trace_result, verdict

        # 2. Quick heuristics on initial domain
        input_domain_info = tldextract.extract(normalized_url)
        if input_domain_info.suffix in SUSPICIOUS_TLDS:
            score += SCORE_SUSPICIOUS_TLD
            reasons.append(f"Suspicious TLD (.{input_domain_info.suffix})")
        
        for brand in BRAND_NAMES:
            ratio = fuzz.ratio(input_domain_info.domain, brand)
            if ratio > BRAND_SIMILARITY_THRESHOLD:
                score += SCORE_BRAND_LOOKALIKE
                reasons.append(f"Potential brand impersonation (looks like '{brand}')")
                break

        # 3. Follow HTTP redirects
        progress_callback(0.25, "Following redirects...")
        final_url = None
        res = None
        with httpx.Client(follow_redirects=True, timeout=timeout_s) as client:
            current_url = normalized_url
            for i in range(REDIRECT_LIMIT + 2): # Allow a few more to detect "too many"
                if i > REDIRECT_LIMIT:
                    score += SCORE_TOO_MANY_REDIRECTS
                    reasons.append("Exceeded redirect limit")
                    break
                
                req = client.build_request("GET", current_url)
                res = client.send(req)
                
                hop = TraceHop(
                    url=str(res.url),
                    status_code=res.status_code,
                    reason=res.reason_phrase,
                    elapsed_ms=int(res.elapsed.total_seconds() * 1000)
                )
                trace_result.hops.append(hop)
                
                if not res.is_redirect:
                    final_url = str(res.url)
                    trace_result.content_type = res.headers.get('content-type')
                    break
                
                current_url = res.headers['location']
            
            trace_result.final_url = final_url or current_url

            # 4. If HTML, parse for meta/JS redirects
            if res and trace_result.content_type and 'text/html' in trace_result.content_type:
                progress_callback(0.45, "Parsing HTML redirects...")
                html_content = res.text
                if final_url:
                    html_redirect = find_html_redirect(html_content, final_url)
                    if html_redirect:
                        trace_result.js_or_meta_followed = True
                        # For simplicity, we'll just treat this as the final URL
                        trace_result.final_url = html_redirect
                        reasons.append("Followed HTML/JS redirect")

            # 5. Analyze final page
            progress_callback(0.65, "Analyzing page...")
            if trace_result.final_url:
                final_domain_info = tldextract.extract(trace_result.final_url)
                if input_domain_info.domain != final_domain_info.domain:
                    score += SCORE_DOMAIN_MISMATCH
                    reasons.append("Redirected to a different domain")

                if trace_result.content_type:
                    if 'application/octet-stream' in trace_result.content_type or \
                       (res and res.headers.get('content-disposition', '').startswith('attachment')):
                        score += SCORE_BINARY_DOWNLOAD
                        reasons.append("Leads to a file download")

                if res and trace_result.content_type and 'text/html' in trace_result.content_type:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    if _is_sensitive_form_present(soup):
                        score += SCORE_SENSITIVE_FORM
                        reasons.append("Page contains a sensitive data form (password, etc.)")
                        trace_result.has_login_form = True

            # 6. Query URLHaus
            progress_callback(0.85, "Checking reputation...")
            urls_to_check = {hop.url for hop in trace_result.hops}
            if trace_result.final_url:
                urls_to_check.add(trace_result.final_url)
            
            for u in urls_to_check:
                if check_urlhaus(u):
                    score += SCORE_URLHAUS_HIT
                    reasons.append("Flagged by URLHaus as malicious")
                    break # One hit is enough

    except httpx.RequestError as e:
        trace_result.errors.append(f"Network error: {e}")
        score += SCORE_NETWORK_ERROR
        reasons.append("Network error during scan")
    except Exception as e:
        trace_result.errors.append(f"An unexpected error occurred: {e}")
        verdict.label = "UNKNOWN"
        reasons.append("An internal error occurred")

    # 7. Final scoring and verdict
    verdict.score = score
    verdict.reasons = reasons
    if score >= 60:
        verdict.label = "UNSAFE"
    elif score >= 30:
        verdict.label = "SUSPICIOUS"
    elif not trace_result.errors:
        verdict.label = "SAFE"

    progress_callback(1.0, verdict.label)
    return trace_result, verdict
