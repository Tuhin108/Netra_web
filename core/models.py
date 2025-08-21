from dataclasses import dataclass, field
from typing import Literal

@dataclass
class TraceHop:
    """Represents a single hop in a redirect chain."""
    url: str
    status_code: int | None
    reason: str | None
    elapsed_ms: int

@dataclass
class TraceResult:
    """Contains the full trace result of a URL scan."""
    input_url: str
    final_url: str | None = None
    hops: list[TraceHop] = field(default_factory=list)
    js_or_meta_followed: bool = False
    content_type: str | None = None
    has_login_form: bool = False
    errors: list[str] = field(default_factory=list)

@dataclass
class Verdict:
    """Represents the final verdict of a URL scan."""
    label: Literal["SAFE", "SUSPICIOUS", "UNSAFE", "UNKNOWN"]
    score: int
    reasons: list[str] = field(default_factory=list)
