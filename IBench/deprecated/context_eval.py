"""
Context Evaluation Pipeline
Environment history evaluation - evaluate assistant responses given full conversation context
"""
from typing import List, Optional
from IBench.models.local_model import LocalModel
from IBench.models.api_model import APIModel
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import (
    EvaluationResult, EvaluationMode, Message
)
from IBench.config import Config

class ContextEvaluator:
    """Environment history evaluator"""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        local_model_path: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize context evaluator
        
        Args:
            config: Optional configuration object
            local_model_path: Path to local model (overrides config)
            api_key: API key for judge model (overrides config)
        """
        self.config = config or Config()
        
        # Override config if parameters provided
        if local_model_path:
            self.config.model.local_model_path = local_model_path
        if api_key:
            self.config.model.api_key = api_key
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration")
        
        # Initialize models
        self.local_model = LocalModel(self.config.model)
        self.judge_model = APIModel(
            self.config.model,
            model_name=self.config.model.judge_model_name
        )
        
        # Initialize evaluator
        self.batch_evaluator = BatchEvaluator(
            self.config.evaluation,
            llm_judge=self.judge_model
        )
        
        print("ContextEvaluator initialized")
    
    def evaluate(
        self,
        conversation_history: List[Message],
        max_turns: Optional[int] = None
    ) -> EvaluationResult:
        """
        Evaluate assistant responses given conversation context
        
        Args:
            conversation_history: Full conversation history ending with user message
            max_turns: Maximum number of turns to evaluate (default from config)
            
        Returns:
            Complete evaluation result
        """
        if max_turns is None:
            max_turns = self.config.evaluation.max_conversation_turns
        
        conversation_id = f"context_conv_{len(conversation_history)}"
        
        # Generate assistant responses for each turn
        responses = []
        current_history = []
        
        for i, msg in enumerate(conversation_history):
            if msg.role == "user":
                current_history.append(msg)
                
                # Generate assistant response
                response = self.local_model.generate(current_history)
                responses.append(response)
                
                # Add assistant message to history for next turn
                current_history.append(
                    Message(
                        role="assistant",
                        content=response,
                        turn_id=i + 1
                    )
                )
        
        # Evaluate all responses
        result = self.batch_evaluator.evaluate_conversation(
            conversation_id=conversation_id,
            mode=EvaluationMode.CONTEXT,
            conversation_history=conversation_history,
            responses=responses
        )
        
        return result
    
    def evaluate_batch(
        self,
        conversation_batches: List[List[Message]],
        output_file: Optional[str] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple conversations in batch
        
        Args:
            conversation_batches: List of conversation histories
            output_file: Optional output file path
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for i, conv_history in enumerate(conversation_batches):
            print(f"Evaluating conversation {i + 1}/{len(conversation_batches)}...")
            
            result = self.evaluate(conv_history)
            results.append(result)
        
        # Save results if output file specified
        if output_file:
            self.batch_evaluator.save_results(results, output_file)
        
        return results
    
    def print_summary(self, results: List[EvaluationResult]):
        """
        Print evaluation summary
        
        Args:
            results: List of evaluation results
        """
        report = self.batch_evaluator.generate_report(results)
        
        print("\n" + "=" * 50)
        print("Context Evaluation Summary")
        print("=" * 50)
        print(f"Total Conversations: {report['total_conversations']}")
        print(f"Total Turns: {report['total_turns']}")
        print(f"Total Score: {report['total_score']}")
        print(f"Average Score: {report['average_score']:.2f}")
        print("=" * 50)
        print("\nConversation Details:")
        for conv in report['conversation_details']:
            print(f"  {conv['conversation_id']}: {conv['final_score']} ({conv['total_turns']} turns)")
