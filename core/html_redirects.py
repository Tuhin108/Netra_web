import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

def find_html_redirect(html_content: str, base_url: str) -> str | None:
    """
    Parses HTML to find meta refresh tags or simple JavaScript redirects.
    Returns the absolute URL of the redirect, or None if not found.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Check for meta refresh tags
    meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'refresh', re.I)})
    if isinstance(meta_refresh, Tag) and meta_refresh.has_attr('content'):
        content_val = meta_refresh['content']
        if isinstance(content_val, list):
            content = content_val[0] if content_val else ''
        else:
            content = str(content_val)

        match = re.search(r'url\s*=\s*([\'"]?)(.*?)\1', content, re.I)
        if match:
            redirect_url = match.group(2).strip()
            if redirect_url:
                return urljoin(base_url, redirect_url)

    # 2. Check for simple JavaScript redirects inside <script> tags
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # Simple regex for window.location assignments
            js_redirect_pattern = re.compile(
                r"""
                window\.location\s*=\s*['"]([^'"]+)['"]|
                window\.location\.href\s*=\s*['"]([^'"]+)['']|
                window\.location\.replace\(['"]([^'"]+)['']\)
                """,
                re.IGNORECASE | re.VERBOSE
            )
            match = js_redirect_pattern.search(script.string)
            if match:
                redirect_url = next((g for g in match.groups() if g is not None), None)
                if redirect_url:
                    return urljoin(base_url, redirect_url)

    return None
