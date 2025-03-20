# shuscribe/services/llm/pipeline/flow.py

from enum import Enum
from typing import Optional

class FlowDecision(str, Enum):
    """Possible flow control decisions"""
    CONTINUE = "continue"  # Continue to next step in sequence
    REPEAT = "repeat"      # Repeat the current step
    GOTO = "goto"          # Go to a specific step
    END = "end"            # End the pipeline execution


class FlowControl:
    """Controls pipeline execution flow"""
    
    def __init__(self, decision: FlowDecision = FlowDecision.CONTINUE, target_step: Optional[str] = None):
        """Initialize flow control"""
        self.decision = decision
        self.target_step = target_step
    
    @staticmethod
    def continue_flow() -> 'FlowControl':
        """Continue to the next step"""
        return FlowControl(FlowDecision.CONTINUE)
    
    @staticmethod
    def repeat() -> 'FlowControl':
        """Repeat the current step"""
        return FlowControl(FlowDecision.REPEAT)
    
    @staticmethod
    def goto(step_name: str) -> 'FlowControl':
        """Go to a specific step"""
        return FlowControl(FlowDecision.GOTO, step_name)
    
    @staticmethod
    def end() -> 'FlowControl':
        """End pipeline execution"""
        return FlowControl(FlowDecision.END)