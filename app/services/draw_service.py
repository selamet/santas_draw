"""
Draw Service Module

Secret Santa draw algorithm implementation.
"""

import logging
import random
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.draw import Draw, Participant, DrawResult, DrawStatus
from app.core.exceptions import (
    DrawServiceException,
    InsufficientParticipantsError,
    DrawAlreadyCompletedError,
    DrawNotFoundError
)


logger = logging.getLogger(__name__)


class DrawService:
    """
    Secret Santa draw service
    
    Performs random matching between participants ensuring:
    - Nobody is matched with themselves (derangement algorithm)
    - Each participant gives to exactly one person
    - Each participant receives from exactly one person
    """
    
    MAX_DERANGEMENT_ATTEMPTS = 100
    
    def __init__(self, db: Session):
        self.db = db
        
    def execute_draw(self, draw_id: int) -> List[DrawResult]:
        """
        Execute the draw and return results
        
        Args:
            draw_id: ID of the draw to execute
            
        Returns:
            List of created DrawResult objects
            
        Raises:
            DrawNotFoundError: If draw is not found
            InsufficientParticipantsError: If less than 3 participants
            DrawAlreadyCompletedError: If draw is already completed
        """
        draw = self._get_draw(draw_id)
        self._validate_draw_status(draw)
        participants = self._get_participants(draw_id)
        self._validate_participant_count(participants, draw_id)
        matches = self._generate_matches(participants)
        draw_results = self._create_draw_results(draw_id, matches)
        self._update_draw_status(draw, DrawStatus.COMPLETED)
        
        logger.info(
            f"Draw executed successfully: draw_id={draw_id}, "
            f"participants={len(participants)}, matches={len(draw_results)}"
        )
        
        return draw_results
    
    def _get_draw(self, draw_id: int) -> Draw:
        draw = self.db.query(Draw).filter(Draw.id == draw_id).first()
        
        if not draw:
            logger.error(f"Draw not found: draw_id={draw_id}")
            raise DrawNotFoundError(f"Draw with id {draw_id} not found")
        
        return draw
    
    def _validate_draw_status(self, draw: Draw) -> None:
        if draw.status == DrawStatus.COMPLETED.value:
            logger.error(f"Draw already completed: draw_id={draw.id}")
            raise DrawAlreadyCompletedError(f"Draw {draw.id} is already completed")
    
    def _get_participants(self, draw_id: int) -> List[Participant]:
        return self.db.query(Participant).filter(Participant.draw_id == draw_id).all()
    
    def _validate_participant_count(self, participants: List[Participant], draw_id: int) -> None:
        if len(participants) < 3:
            logger.error(f"Insufficient participants: draw_id={draw_id}, count={len(participants)}")
            raise InsufficientParticipantsError(
                f"Draw requires at least 3 participants, got {len(participants)}"
            )
    
    def _generate_matches(self, participants: List[Participant]) -> List[Dict[str, int]]:
        """Generate matches using derangement algorithm (no self-assignments)"""
        participant_ids = [p.id for p in participants]
        receivers = self._create_derangement(participant_ids)
        matches = [
            {"giver_id": giver_id, "receiver_id": receiver_id}
            for giver_id, receiver_id in zip(participant_ids, receivers)
        ]
        logger.debug(f"Generated {len(matches)} matches")
        return matches
    
    def _create_derangement(self, items: List[int]) -> List[int]:
        """
        Create a derangement (permutation where no element appears in its original position)
        
        Perfect for Secret Santa matching - ensures nobody is matched with themselves.
        """
        n = len(items)
        
        if n < 2:
            raise DrawServiceException("Cannot create derangement with less than 2 items")
        
        if n == 2:
            return [items[1], items[0]]
        
        for _ in range(self.MAX_DERANGEMENT_ATTEMPTS):
            shuffled = items.copy()
            random.shuffle(shuffled)
            
            if all(shuffled[i] != items[i] for i in range(n)):
                return shuffled
        
        return self._deterministic_derangement(items)
    
    def _deterministic_derangement(self, items: List[int]) -> List[int]:
        """Fallback: cyclic permutation [A,B,C,D] -> [B,C,D,A]"""
        return items[1:] + [items[0]]
    
    def _create_draw_results(self, draw_id: int, matches: List[Dict[str, int]]) -> List[DrawResult]:
        """Create DrawResult records in database"""
        draw_results = []
        
        try:
            for match in matches:
                result = DrawResult(
                    draw_id=draw_id,
                    giver_participant_id=match["giver_id"],
                    receiver_participant_id=match["receiver_id"]
                )
                self.db.add(result)
                draw_results.append(result)
            
            logger.info(f"Created {len(draw_results)} DrawResult records")
            
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise DrawServiceException(
                "Failed to create draw results due to database constraint violation"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise DrawServiceException(f"Failed to create draw results: {str(e)}") from e
        
        return draw_results
    
    def _update_draw_status(self, draw: Draw, status: DrawStatus) -> None:
        draw.status = status.value
        logger.info(f"Draw status updated: draw_id={draw.id}, status={status.value}")
    
    def get_draw_results(self, draw_id: int) -> List[DrawResult]:
        """Get all results for a draw"""
        return self.db.query(DrawResult).filter(DrawResult.draw_id == draw_id).all()
    
    def get_participant_match(self, draw_id: int, participant_id: int) -> Optional[DrawResult]:
        """Get the match for a specific participant"""
        return (
            self.db.query(DrawResult)
            .filter(
                DrawResult.draw_id == draw_id,
                DrawResult.giver_participant_id == participant_id
            )
            .first()
        )

