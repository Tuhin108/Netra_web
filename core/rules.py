# Scoring weights
SCORE_SUSPICIOUS_TLD = 15
SCORE_TOO_MANY_REDIRECTS = 15
SCORE_DOMAIN_MISMATCH = 20
SCORE_BRAND_LOOKALIKE = 25
SCORE_SENSITIVE_FORM = 30
SCORE_BINARY_DOWNLOAD = 20
SCORE_URLHAUS_HIT = 40
SCORE_NETWORK_ERROR = 10

# Thresholds
REDIRECT_LIMIT = 3
BRAND_SIMILARITY_THRESHOLD = 80  # rapidfuzz ratio

# Lists (can be expanded)
SUSPICIOUS_TLDS = set()
BRAND_NAMES = {
    "paypal", "google", "amazon", "apple", "microsoft", "facebook",
    "instagram", "twitter", "linkedin", "netflix", "spotify", "ebay",
    "walmart", "target", "chase", "wellsfargo", "bankofamerica",
}
SENSITIVE_INPUT_KEYWORDS = {"password", "otp", "card", "cvv", "ssn", "pin"}

def load_suspicious_tlds(path: str = "resources/suspicious_tlds.txt"):
    """Load suspicious TLDs from a file into the global set."""
    try:
        with open(path, "r") as f:
            for line in f:
                tld = line.strip()
                if tld and not tld.startswith("#"):
                    SUSPICIOUS_TLDS.add(tld)
    except FileNotFoundError:
        print(f"Warning: Suspicious TLDs file not found at '{path}'")

# Load the TLDs on module import
load_suspicious_tlds()
