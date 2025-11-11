"""
Invite code generator utility for creating unique, fun invite codes
"""

import random
from sqlalchemy.orm import Session


def generate_invite_code(db: Session, max_retries: int = 5) -> str:
    """
    Generate a fun, memorable invite code using word combinations.
    Format: adjective-noun-number (e.g., jolly-reindeer-742)
    
    Args:
        db: Database session
        max_retries: Maximum number of retries if collision occurs
        
    Returns:
        Unique invite code string
        
    Raises:
        RuntimeError: If unable to generate unique code after max_retries
    """
    from app.models.draw import Draw

    adjectives = [
        "jolly", "merry", "festive", "bright", "shiny", "sparkly",
        "cheerful", "happy", "cozy", "magical", "snowy", "frosty",
        "gleaming", "twinkling", "radiant", "dazzling", "glowing", "beaming"
    ]

    nouns = [
        "reindeer", "snowman", "gift", "star", "bell", "tree",
        "santa", "elf", "candy", "sleigh", "angel", "wreath",
        "snowflake", "gingerbread", "stocking", "ornament", "mistletoe", "carol"
    ]

    for attempt in range(max_retries):
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        num = random.randint(100, 999)

        invite_code = f"{adj}-{noun}-{num}"

        existing = db.query(Draw).filter(Draw.invite_code == invite_code).first()

        if not existing:
            return invite_code

    raise RuntimeError(f"Failed to generate unique invite code after {max_retries} attempts")
