from datetime import datetime


def compact_currency(value: float | int | None, symbol: str = "$") -> str:
    if value is None:
        return "Unavailable"

    number = float(value)
    magnitude = abs(number)

    if magnitude >= 1_000_000_000_000:
        return f"{symbol}{number / 1_000_000_000_000:.2f}T"
    if magnitude >= 1_000_000_000:
        return f"{symbol}{number / 1_000_000_000:.2f}B"
    if magnitude >= 1_000_000:
        return f"{symbol}{number / 1_000_000:.2f}M"
    if magnitude >= 1_000:
        return f"{symbol}{number / 1_000:.2f}K"

    return f"{symbol}{number:,.2f}"


def percentage(value: float | int | None) -> str:
    if value is None:
        return "Unavailable"

    return f"{float(value):.2f}%"


def signed_percentage(value: float | int | None) -> str:
    if value is None:
        return "Unavailable"

    return f"{float(value):+.2f}%"


def utc_time(iso_value: str) -> str:
    try:
        parsed = datetime.fromisoformat(iso_value)
        return parsed.strftime("%d %b %Y, %H:%M UTC")
    except (TypeError, ValueError):
        return "Unknown"
