"""
Draw Service Tests

Comprehensive unit tests for DrawService validating Secret Santa algorithm correctness.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.draw_service import DrawService
from app.core.exceptions import (
    DrawServiceException,
    InsufficientParticipantsError,
    DrawAlreadyCompletedError,
    DrawNotFoundError
)
from app.models.draw import Draw, Participant, DrawResult, DrawStatus, DrawType


class TestDrawService:
    """Main DrawService test class"""
    
    def test_execute_draw_success(self, test_db: Session):
        """Test successful draw execution"""
        draw = Draw(
            status=DrawStatus.IN_PROGRESS.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        participants = [
            Participant(
                draw_id=draw.id,
                first_name=f"Person{i}",
                last_name="Test",
                email=f"person{i}@test.com"
            )
            for i in range(1, 4)  # 3 katılımcı
        ]
        test_db.bulk_save_objects(participants)
        test_db.commit()
        
        service = DrawService(test_db)
        results = service.execute_draw(draw.id)
        
        assert len(results) == 3
        
        givers = {r.giver_participant_id for r in results}
        assert len(givers) == 3
        
        receivers = {r.receiver_participant_id for r in results}
        assert len(receivers) == 3
        
        for result in results:
            assert result.giver_participant_id != result.receiver_participant_id
        test_db.refresh(draw)
        assert draw.status == DrawStatus.COMPLETED.value
    
    def test_execute_draw_with_minimum_participants(self, test_db: Session):
        """Test draw with minimum participants (3)"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(3):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        results = service.execute_draw(draw.id)
        
        assert len(results) == 3
        for result in results:
            assert result.giver_participant_id != result.receiver_participant_id
    
    def test_execute_draw_with_many_participants(self, test_db: Session):
        """Test draw with many participants (10 people)"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(10):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"Person{i}",
                last_name="LastName",
                email=f"person{i}@example.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        results = service.execute_draw(draw.id)
        
        assert len(results) == 10
        
        giver_ids = {r.giver_participant_id for r in results}
        assert len(giver_ids) == 10
        
        receiver_ids = {r.receiver_participant_id for r in results}
        assert len(receiver_ids) == 10
        for result in results:
            assert result.giver_participant_id != result.receiver_participant_id
    
    def test_execute_draw_insufficient_participants(self, test_db: Session):
        """Test insufficient participants error (2 people)"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(2):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        # Act & Assert
        service = DrawService(test_db)
        with pytest.raises(InsufficientParticipantsError) as exc_info:
            service.execute_draw(draw.id)
        
        assert "at least 3 participants" in str(exc_info.value).lower()
    
    def test_execute_draw_no_participants(self, test_db: Session):
        """Test draw with no participants"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.commit()
        
        # Act & Assert
        service = DrawService(test_db)
        with pytest.raises(InsufficientParticipantsError):
            service.execute_draw(draw.id)
    
    def test_execute_draw_not_found(self, test_db: Session):
        """Test non-existent draw error"""
        service = DrawService(test_db)
        with pytest.raises(DrawNotFoundError) as exc_info:
            service.execute_draw(9999)
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_execute_draw_already_completed(self, test_db: Session):
        """Test already completed draw error"""
        draw = Draw(
            status=DrawStatus.COMPLETED.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(3):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        # Act & Assert
        service = DrawService(test_db)
        with pytest.raises(DrawAlreadyCompletedError) as exc_info:
            service.execute_draw(draw.id)
        
        assert "already completed" in str(exc_info.value).lower()
    
    def test_execute_draw_idempotency(self, test_db: Session):
        """Test idempotency - draw should not be executed twice"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(3):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        
        results1 = service.execute_draw(draw.id)
        assert len(results1) == 3
        with pytest.raises(DrawAlreadyCompletedError):
            service.execute_draw(draw.id)
    
    def test_get_draw_results(self, test_db: Session):
        """Test retrieving draw results"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(5):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        service.execute_draw(draw.id)
        
        results = service.get_draw_results(draw.id)
        assert len(results) == 5
        for result in results:
            assert result.draw_id == draw.id
            assert result.giver_participant_id is not None
            assert result.receiver_participant_id is not None
    
    def test_get_participant_match(self, test_db: Session):
        """Test retrieving match for specific participant"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        participants = []
        for i in range(4):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
            participants.append(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        service.execute_draw(draw.id)
        
        first_participant = participants[0]
        match = service.get_participant_match(draw.id, first_participant.id)
        assert match is not None
        assert match.giver_participant_id == first_participant.id
        assert match.receiver_participant_id != first_participant.id
        assert match.receiver_participant_id in [p.id for p in participants]
    
    def test_derangement_algorithm(self, test_db: Session):
        """Test derangement algorithm correctness - 100 iterations"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(5):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        
        for iteration in range(100):
            test_db.query(DrawResult).filter(
                DrawResult.draw_id == draw.id
            ).delete()
            
            draw.status = DrawStatus.ACTIVE.value
            test_db.commit()
            
            results = service.execute_draw(draw.id)
            participant_ids = [
                p.id for p in test_db.query(Participant)
                .filter(Participant.draw_id == draw.id)
                .all()
            ]
            
            for result in results:
                assert result.giver_participant_id != result.receiver_participant_id, \
                    f"Iteration {iteration}: Self-assignment detected!"
                assert result.giver_participant_id in participant_ids
                assert result.receiver_participant_id in participant_ids
            
            giver_ids = [r.giver_participant_id for r in results]
            assert sorted(giver_ids) == sorted(participant_ids)
            receiver_ids = [r.receiver_participant_id for r in results]
            assert sorted(receiver_ids) == sorted(participant_ids)


class TestDrawServiceEdgeCases:
    """DrawService edge case tests"""
    
    def test_execute_draw_with_two_participants_should_fail(self, test_db: Session):
        """Test that draw fails with only 2 participants"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(2):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        # Act & Assert
        service = DrawService(test_db)
        with pytest.raises(InsufficientParticipantsError):
            service.execute_draw(draw.id)
    
    def test_database_rollback_on_error(self, test_db: Session):
        """Test database rollback on error"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        participants = []
        for i in range(3):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
            participants.append(participant)
        test_db.commit()
        
        manual_result = DrawResult(
            draw_id=draw.id,
            giver_participant_id=participants[0].id,
            receiver_participant_id=participants[1].id
        )
        test_db.add(manual_result)
        test_db.commit()
        
        service = DrawService(test_db)
        with pytest.raises(DrawServiceException):
            service.execute_draw(draw.id)
        
        existing_results = test_db.query(DrawResult).filter(
            DrawResult.draw_id == draw.id
        ).all()
        assert len(existing_results) == 1
    
    def test_concurrent_draw_prevention(self, test_db: Session):
        """Test prevention of concurrent draw execution"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.MANUAL.value
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(3):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@test.com"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        
        results = service.execute_draw(draw.id)
        assert len(results) == 3
        with pytest.raises(DrawAlreadyCompletedError):
            service.execute_draw(draw.id)


class TestDrawServiceDerangementAlgorithm:
    """Derangement algorithm specific tests"""
    
    def test_derangement_with_3_participants(self, test_db: Session):
        """Test derangement with 3 participants"""
        service = DrawService(test_db)
        items = [1, 2, 3]
        
        for _ in range(100):
            result = service._create_derangement(items)
            
            assert sorted(result) == sorted(items)
            for i in range(len(items)):
                assert result[i] != items[i]
    
    def test_derangement_with_2_participants(self, test_db: Session):
        """Test derangement with 2 participants (simple swap)"""
        service = DrawService(test_db)
        items = [1, 2]
        
        result = service._create_derangement(items)
        
        assert result == [2, 1]
    
    def test_derangement_with_large_list(self, test_db: Session):
        """Test derangement with large list (20 items)"""
        service = DrawService(test_db)
        items = list(range(1, 21))
        
        result = service._create_derangement(items)
        
        assert sorted(result) == sorted(items)
        for i in range(len(items)):
            assert result[i] != items[i]
    
    def test_deterministic_derangement(self, test_db: Session):
        """Test deterministic derangement (fallback algorithm)"""
        service = DrawService(test_db)
        items = [1, 2, 3, 4, 5]
        
        result = service._deterministic_derangement(items)
        
        assert result == [2, 3, 4, 5, 1]
        for i in range(len(items)):
            assert result[i] != items[i]


class TestDrawServiceIntegration:
    """DrawService integration tests"""
    
    def test_full_flow_manual_draw(self, test_db: Session):
        """Test full manual draw flow"""
        draw = Draw(
            status=DrawStatus.IN_PROGRESS.value,
            draw_type=DrawType.MANUAL.value,
            require_address=True,
            require_phone=False
        )
        test_db.add(draw)
        test_db.flush()
        
        participant_data = [
            ("Alice", "Smith", "alice@example.com", "123 Main St", None),
            ("Bob", "Jones", "bob@example.com", "456 Oak Ave", None),
            ("Charlie", "Brown", "charlie@example.com", "789 Pine Rd", None),
            ("Diana", "Wilson", "diana@example.com", "321 Elm St", None),
        ]
        
        for first, last, email, address, phone in participant_data:
            participant = Participant(
                draw_id=draw.id,
                first_name=first,
                last_name=last,
                email=email,
                address=address,
                phone=phone
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        results = service.execute_draw(draw.id)
        
        assert len(results) == 4
        for first, last, email, _, _ in participant_data:
            participant = test_db.query(Participant).filter(
                Participant.email == email
            ).first()
            
            match = service.get_participant_match(draw.id, participant.id)
            assert match is not None
            assert match.giver_participant_id == participant.id
            assert match.receiver_participant_id != participant.id
        test_db.refresh(draw)
        assert draw.status == DrawStatus.COMPLETED.value
    
    def test_full_flow_dynamic_draw(self, test_db: Session):
        """Test full dynamic draw flow"""
        draw = Draw(
            status=DrawStatus.ACTIVE.value,
            draw_type=DrawType.DYNAMIC.value,
            invite_code="ABC123",
            require_address=False,
            require_phone=True
        )
        test_db.add(draw)
        test_db.flush()
        
        for i in range(5):
            participant = Participant(
                draw_id=draw.id,
                first_name=f"Participant{i}",
                last_name="Test",
                email=f"participant{i}@test.com",
                phone=f"555-000{i}"
            )
            test_db.add(participant)
        test_db.commit()
        
        service = DrawService(test_db)
        results = service.execute_draw(draw.id)
        
        assert len(results) == 5
        for result in results:
            assert result.draw_id == draw.id
        test_db.refresh(draw)
        assert draw.status == DrawStatus.COMPLETED.value

