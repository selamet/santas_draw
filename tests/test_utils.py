"""
Utility function tests
"""

import pytest
from app.utils.link_generator import generate_invite_code
from app.models.draw import Draw, DrawType, DrawStatus


@pytest.mark.utils
class TestInviteCodeGenerator:
    """Test invite code generation utility"""
    
    def test_generate_invite_code_format(self, test_db):
        """Test that generated invite code has correct format"""
        invite_code = generate_invite_code(test_db)
        
        # Format: word-word-number
        parts = invite_code.split('-')
        assert len(parts) == 3
        assert parts[0].isalpha()  # adjective
        assert parts[1].isalpha()  # noun
        assert parts[2].isdigit()  # number
        assert len(parts[2]) == 3  # 3-digit number
    
    def test_generate_invite_code_uniqueness(self, test_db):
        """Test that generated codes are unique"""
        codes = set()
        
        for _ in range(10):
            code = generate_invite_code(test_db)
            codes.add(code)
            
            # Add to database to test collision detection
            draw = Draw(
                creator_id=1,
                draw_type=DrawType.DYNAMIC.value,
                status=DrawStatus.ACTIVE.value,
                invite_code=code
            )
            test_db.add(draw)
            test_db.commit()
        
        # All codes should be unique
        assert len(codes) == 10
    
    def test_generate_invite_code_collision_handling(self, test_db):
        """Test that collisions are handled correctly"""
        # Pre-populate some codes
        for i in range(3):
            draw = Draw(
                creator_id=1,
                draw_type=DrawType.DYNAMIC.value,
                status=DrawStatus.ACTIVE.value,
                invite_code=f"test-code-{i}"
            )
            test_db.add(draw)
        test_db.commit()
        
        # Generate new code - should not collide
        new_code = generate_invite_code(test_db)
        
        existing = test_db.query(Draw).filter(
            Draw.invite_code == new_code
        ).first()
        
        assert existing is None
    
    def test_generate_invite_code_uses_christmas_words(self, test_db):
        """Test that generated codes use Christmas-themed words"""
        christmas_adjectives = {
            "jolly", "merry", "festive", "bright", "shiny", "sparkly",
            "cheerful", "happy", "cozy", "magical", "snowy", "frosty",
            "gleaming", "twinkling", "radiant", "dazzling", "glowing", "beaming"
        }
        
        christmas_nouns = {
            "reindeer", "snowman", "gift", "star", "bell", "tree",
            "santa", "elf", "candy", "sleigh", "angel", "wreath",
            "snowflake", "gingerbread", "stocking", "ornament", "mistletoe", "carol"
        }
        
        # Generate multiple codes and check if they use expected words
        for _ in range(5):
            code = generate_invite_code(test_db)
            parts = code.split('-')
            
            # At least adjective or noun should be from our lists
            assert parts[0] in christmas_adjectives
            assert parts[1] in christmas_nouns

