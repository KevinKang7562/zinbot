import re
import unicodedata


_CONTROL_CHARS_RE = re.compile(r"[\u0000-\u0008\u000B-\u001F\u007F]")
_BROKEN_LATIN1_RE = re.compile(r"[ÃÂÐÑØãâ€˜€™“”•·…]")
_WHITESPACE_RE = re.compile(r"[ \t\f\v]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

_CHAR_REPLACEMENTS = str.maketrans(
    {
        "\u00A0": " ",
        "\u2000": " ",
        "\u2001": " ",
        "\u2002": " ",
        "\u2003": " ",
        "\u2004": " ",
        "\u2005": " ",
        "\u2006": " ",
        "\u2007": " ",
        "\u2008": " ",
        "\u2009": " ",
        "\u200A": " ",
        "\u202F": " ",
        "\u205F": " ",
        "\u3000": " ",
        "\u200B": "",
        "\u200C": "",
        "\u200D": "",
        "\u2060": "",
        "\uFEFF": "",
        "‘": "'",
        "’": "'",
        "‚": ",",
        "‛": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "–": "-",
        "—": "-",
        "―": "-",
        "−": "-",
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "…": "...",
        "•": "*",
        "·": ".",
        "′": "'",
        "″": '"',
        "⅓": "1/3",
        "⅔": "2/3",
        "¼": "1/4",
        "½": "1/2",
        "¾": "3/4",
        "⅛": "1/8",
        "⅜": "3/8",
        "⅝": "5/8",
        "⅞": "7/8",
        "×": " x ",
        "÷": " / ",
        "±": " +/- ",
        "∓": " -/+ ",
        "≠": " != ",
        "≤": " <= ",
        "≥": " >= ",
        "≈": " ~= ",
        "≃": " ~= ",
        "≅": " ~= ",
        "∞": " infinity ",
        "∑": " sigma ",
        "∏": " product ",
        "∫": " integral ",
        "√": " sqrt ",
        "∂": " partial ",
        "∇": " nabla ",
        "∈": " in ",
        "∉": " not in ",
        "∩": " intersection ",
        "∪": " union ",
        "⊂": " subset ",
        "⊆": " subseteq ",
        "⊃": " superset ",
        "⊇": " superseteq ",
        "⇒": " => ",
        "→": " -> ",
        "←": " <- ",
        "↔": " <-> ",
        "∀": " for all ",
        "∃": " exists ",
        "¬": " not ",
        "∧": " and ",
        "∨": " or ",
        "°": " degree ",
    }
)

_GREEK_REPLACEMENTS = str.maketrans(
    {
        "α": " alpha ",
        "β": " beta ",
        "γ": " gamma ",
        "δ": " delta ",
        "ε": " epsilon ",
        "θ": " theta ",
        "λ": " lambda ",
        "μ": " mu ",
        "π": " pi ",
        "σ": " sigma ",
        "τ": " tau ",
        "φ": " phi ",
        "ω": " omega ",
        "Δ": " Delta ",
        "Θ": " Theta ",
        "Λ": " Lambda ",
        "Π": " Pi ",
        "Σ": " Sigma ",
        "Φ": " Phi ",
        "Ω": " Omega ",
    }
)


def _looks_like_mojibake(text: str) -> bool:
    return bool(_BROKEN_LATIN1_RE.search(text))


def _repair_mojibake(text: str) -> str:
    if not _looks_like_mojibake(text):
        return text
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    return repaired if len(repaired.strip()) >= len(text.strip()) / 2 else text


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = _repair_mojibake(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_CHAR_REPLACEMENTS)
    text = text.translate(_GREEK_REPLACEMENTS)
    text = _CONTROL_CHARS_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = _WHITESPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def decode_text_bytes(data: bytes) -> str:
    if not data:
        return ""

    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr", "utf-16", "latin1"):
        try:
            decoded = data.decode(encoding)
            if decoded:
                return normalize_text(decoded)
        except UnicodeDecodeError:
            continue

    return normalize_text(data.decode("utf-8", errors="replace"))
