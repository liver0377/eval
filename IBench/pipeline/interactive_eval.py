"""
Interactive Evaluation Pipeline
Dynamic interactive evaluation - user and model alternate responses
"""
from typing import List, Optional
from IBench.models.local_model import LocalModel
from IBench.models.api_model import APIModel
from IBench.conversation.user_simulator import UserSimulator
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import (
    EvaluationResult, EvaluationMode, Message
)
from IBench.config import Config

class InteractiveEvaluator:
    """Dynamic interactive evaluator"""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        local_model_path: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize interactive evaluator
        
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
        self.user_simulator = UserSimulator(self.config.model)
        self.judge_model = APIModel(
            self.config.model,
            model_name=self.config.model.judge_model_name
        )
        
        # Initialize evaluator
        self.batch_evaluator = BatchEvaluator(
            self.config.evaluation,
            llm_judge=self.judge_model
        )
        
        print("InteractiveEvaluator initialized")
    
    def evaluate(
        self,
        initial_prompt: str,
        max_turns: Optional[int] = None
    ) -> EvaluationResult:
        """
        Evaluate assistant through dynamic interactive conversation
        
        Args:
            initial_prompt: Initial user prompt
            max_turns: Maximum number of turns (default from config)
            
        Returns:
            Complete evaluation result
        """
        if max_turns is None:
            max_turns = self.config.evaluation.max_conversation_turns
        
        conversation_id = f"interactive_conv_{hash(initial_prompt)}"
        
        conversation_history = []
        responses = []
        
        # First user message
        user_msg = Message(
            role="user",
            content=initial_prompt,
            turn_id=1
        )
        conversation_history.append(user_msg)
        
        # Interactive loop
        for turn in range(1, max_turns + 1):
            print(f"Turn {turn}...")
            
            # Generate assistant response
            assistant_response = self.local_model.generate(conversation_history)
            responses.append(assistant_response)
            
            assistant_msg = Message(
                role="assistant",
                content=assistant_response,
                turn_id=turn
            )
            conversation_history.append(assistant_msg)
            
            # Generate next user message (except after last turn)
            if turn < max_turns:
                user_msg = self.user_simulator.generate_user_message(conversation_history)
                conversation_history.append(user_msg)
        
        # Evaluate all responses
        result = self.batch_evaluator.evaluate_conversation(
            conversation_id=conversation_id,
            mode=EvaluationMode.INTERACTIVE,
            conversation_history=conversation_history,
            responses=responses
        )
        
        return result
    
    def evaluate_batch(
        self,
        initial_prompts: List[str],
        output_file: Optional[str] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple conversations in batch
        
        Args:
            initial_prompts: List of initial user prompts
            output_file: Optional output file path
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for i, prompt in enumerate(initial_prompts):
            print(f"Evaluating conversation {i + 1}/{len(initial_prompts)}...")
            
            result = self.evaluate(prompt)
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
        print("Interactive Evaluation Summary")
        print("=" * 50)
        print(f"Total Conversations: {report['total_conversations']}")
        print(f"Total Turns: {report['total_turns']}")
        print(f"Total Score: {report['total_score']}")
        print(f"Average Score: {report['average_score']:.2f}")
        print("=" * 50)
        print("\nConversation Details:")
        for conv in report['conversation_details']:
            print(f"  {conv['conversation_id']}: {conv['final_score']} ({conv['total_turns']} turns)")
