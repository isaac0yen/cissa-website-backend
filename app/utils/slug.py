"""Slug generation helpers.

Generates URL-friendly, SEO-oriented slugs from arbitrary text and
guarantees uniqueness against an existing set of slugs.
"""

import re
import unicodedata
from typing import Callable, Set


def slugify(value: str) -> str:
    """Convert a string into a URL-friendly slug.

    Example:
        "Tech Week 2026!" -> "tech-week-2026"

    Args:
        value (str): The text to slugify (e.g. a title).

    Returns:
        str: A lowercase, hyphen-separated slug. Falls back to "item" if
        the input contains no slug-able characters.
    """
    # normalize unicode (e.g. accented chars) to plain ASCII
    value = (
        unicodedata.normalize("NFKD", value or "")
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    value = value.lower().strip()
    # replace any run of non-alphanumeric chars with a single hyphen
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "item"


def generate_unique_slug(base_text: str, exists: Callable[[str], bool]) -> str:
    """Generate a unique slug from base_text.

    Appends an incrementing numeric suffix (-2, -3, ...) until the slug is
    not already taken, as determined by the `exists` callback.

    Args:
        base_text (str): The source text (typically a title).
        exists (Callable[[str], bool]): Returns True if a slug is already used.

    Returns:
        str: A unique slug.
    """
    base = slugify(base_text)
    slug = base
    suffix = 1
    while exists(slug):
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


def unique_slug_from_seen(base_text: str, seen: Set[str]) -> str:
    """Generate a unique slug using an in-memory set of already-used slugs.

    Convenience wrapper around generate_unique_slug for batch operations
    such as migration backfills. Mutates `seen` by adding the result.

    Args:
        base_text (str): The source text (typically a title).
        seen (Set[str]): Set of slugs already assigned in this batch.

    Returns:
        str: A unique slug, also added to `seen`.
    """
    slug = generate_unique_slug(base_text, lambda s: s in seen)
    seen.add(slug)
    return slug
