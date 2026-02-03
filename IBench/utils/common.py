"""
Common data structures for IBench
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class RuleType(Enum):
    """Rule type classification"""
    LLM = "LLM"
    RULE = "Rule"

class EvaluationMode(Enum):
    """Evaluation mode"""
    CONTEXT = "context"  # Environment history evaluation
    INTERACTIVE = "interactive"  # Dynamic interactive evaluation

@dataclass
class Message:
    """Single message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    turn_id: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "turn_id": self.turn_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Create from dictionary"""
        return cls(
            role=data["role"],
            content=data["content"],
            turn_id=data["turn_id"]
        )

@dataclass
class RuleResult:
    """Result of single rule evaluation"""
    rule_id: int
    rule_type: RuleType
    rule_description: str
    passed: bool
    score: int
    reason: str
    turn_id: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type.value,
            "rule_description": self.rule_description,
            "passed": self.passed,
            "score": self.score,
            "reason": self.reason,
            "turn_id": self.turn_id
        }

@dataclass
class TurnEvaluation:
    """Evaluation results for a single turn"""
    turn_id: int
    response: str
    single_rules: List[RuleResult] = field(default_factory=list)
    stage_rules: List[RuleResult] = field(default_factory=list)
    
    @property
    def total_score(self) -> int:
        """Calculate total score for this turn"""
        all_rules = self.single_rules + self.stage_rules
        return sum(rule.score for rule in all_rules if not rule.passed)
    
    @property
    def passed_single_rules(self) -> int:
        """Count passed single rules"""
        return sum(1 for rule in self.single_rules if rule.passed)
    
    @property
    def passed_stage_rules(self) -> int:
        """Count passed stage rules"""
        return sum(1 for rule in self.stage_rules if rule.passed)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "turn_id": self.turn_id,
            "response": self.response,
            "single_rules": [rule.to_dict() for rule in self.single_rules],
            "stage_rules": [rule.to_dict() for rule in self.stage_rules],
            "total_score": self.total_score
        }

@dataclass
class EvaluationResult:
    """Complete evaluation result for a conversation"""
    conversation_id: str
    mode: EvaluationMode
    turn_evaluations: List[TurnEvaluation] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    @property
    def final_score(self) -> int:
        """Calculate final score (sum of all turn scores)"""
        return sum(turn.total_score for turn in self.turn_evaluations)
    
    @property
    def total_turns(self) -> int:
        """Get total number of turns"""
        return len(self.turn_evaluations)
    
    def get_turn_by_id(self, turn_id: int) -> Optional[TurnEvaluation]:
        """Get turn evaluation by turn_id"""
        for turn in self.turn_evaluations:
            if turn.turn_id == turn_id:
                return turn
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "mode": self.mode.value,
            "total_turns": self.total_turns,
            "final_score": self.final_score,
            "metadata": self.metadata,
            "turn_evaluations": [turn.to_dict() for turn in self.turn_evaluations]
        }

@dataclass
class RuleDefinition:
    """Definition of a rule"""
    rule_id: int
    rule_type: RuleType
    description: str
    score: int
    precondition: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type.value,
            "description": self.description,
            "score": self.score,
            "precondition": self.precondition
        }
