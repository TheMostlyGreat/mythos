from typing import List, Dict, Any
from mythos.utils.llm_utils import call_OpenAI_API, create_messages
from mythos.utils.logger import get_logger
from mythos.config.settings import (
    QUESTIONER_SYSTEM_PROMPT,
    QUESTIONER_RESPONSE_SCHEMA,
)

# Import thinking indicator from shared utils
from mythos.utils.ui_utils import print_thinking


class StoryQuestioner:
    """
    Interactive story refinement through natural conversation.
    

    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.conversation = []
        self.exchanges_count = 0
        self.max_exchanges = 50  # Safety limit only - LLM should decide when to stop
        self._last_ready_to_stop = False  # Track if LLM is ready to stop

    def conduct_interview(self, initial_prompt: str) -> str:
        """
        Have a natural conversation to refine the story concept.
        
        Args:
            initial_prompt: The user's original story idea
            
        Returns:
            Refined and enriched story prompt
        """
        # Initialize conversation with developer role first
        self.conversation = [
            {"role": "developer", "content": QUESTIONER_SYSTEM_PROMPT},
            {"role": "user", "content": initial_prompt}
        ]
        
        print("Let's chat about your story idea!\n")
        print("💡 (Type 'done' anytime to start writing)\n")
        print()
        
        try:
            # For the first exchange, generate a special opening question from the AI.
            ai_response = self._generate_first_conversation_response(initial_prompt)
            print(f"💬 {ai_response}")
            
            # Check if LLM wants to stop after first response
            if self._llm_wants_to_stop(ai_response):
                print("Perfect! Let's start developing your story.")
                return self._build_refined_prompt(initial_prompt)
            
            user_response = self._get_user_response()
            if self._should_exit(user_response):
                print("Let's create your story.")
                return self._build_refined_prompt(initial_prompt)
            self._record_exchange(ai_response, user_response)
            self.exchanges_count += 1
            
            while self.exchanges_count < self.max_exchanges:
                # Generate natural conversational response
                ai_response = self._generate_conversation_response()
                
                # Show AI's response
                print(f"💬 {ai_response}")
                
                # Get user's response
                user_response = self._get_user_response()
                
                # Check for early exit
                if self._should_exit(user_response):
                    print("Let's create your story.")
                    break
                
                # Record the exchange
                self._record_exchange(ai_response, user_response)
                self.exchanges_count += 1
                
                # Check if LLM indicated it's ready to stop
                if self._llm_wants_to_stop(ai_response):
                    print("Perfect! Let's start developing your story.")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error during conversation: {e}")
            print("Let's start writing with what we have!")
        
        # Safety check - if we hit max exchanges without LLM stopping
        if self.exchanges_count >= self.max_exchanges:
            print(f"\n💡 We've had a great long conversation! Let's start creating your story.")
        
        # Add wrap-up message to set clear expectations
        print("\n✅ Great! I've gathered enough details about your story.")
        print("🎯 Now I'll use everything we discussed to create your enhanced story concept.")
        
        # Build final refined prompt
        refined_prompt = self._build_refined_prompt(initial_prompt)
        self.logger.info(f"Conversation complete. Had {self.exchanges_count} exchanges.")
        
        return refined_prompt

    def _llm_wants_to_stop(self, ai_response: str) -> bool:
        """Check if LLM has indicated it's ready to stop questioning."""
        return self._last_ready_to_stop

    def _generate_conversation_response(self) -> str:
        """Generate natural conversational response from AI."""
        
        # Show thinking indicator before LLM call
        print("\n🤔 Thinking of the next question...")
        
        # Build the full conversation context
        messages = self.conversation.copy()
        
        # Add current context
        messages.append({
            "role": "user", 
            "content": f"Original story concept: {self.conversation[1]['content']}\n\nConversation so far:\n{self._format_conversation()}"
        })
        
        try:
            response = call_OpenAI_API(
                input=messages,
                json_output=True,
                json_schema=QUESTIONER_RESPONSE_SCHEMA
            )
            
            # Handle both dict and string responses
            if isinstance(response, dict):
                # Store the ready_to_stop flag for later checking
                self._last_ready_to_stop = response.get('ready_to_stop', False)
                return response.get('response', '').strip()
            else:
                # Try to parse JSON string
                try:
                    import json
                    parsed_response = json.loads(response)
                    self._last_ready_to_stop = parsed_response.get('ready_to_stop', False)
                    return parsed_response.get('response', '').strip()
                except (json.JSONDecodeError, AttributeError):
                    # Fallback for non-JSON string responses
                    self.logger.warning("Received non-JSON string response, using fallback")
                    self._last_ready_to_stop = False
                    return str(response).strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            self._last_ready_to_stop = False
            return "Tell me more about what excites you most about this story!"

    def _generate_first_conversation_response(self, initial_prompt: str) -> str:
        """Generate the opening conversational response from AI for the first exchange."""
        
        # Show thinking indicator before LLM call
        print("\n🤔 Thinking of questions to help develop your story...")
        
        prompt = f"""
        The user has shared this story concept: {initial_prompt}
        
        This is the very first exchange. Generate an engaging opening question or comment 
        that will help explore and develop their story idea further.
        """
        
        try:
            # Convert to message format using helper function
            messages = create_messages(prompt, QUESTIONER_SYSTEM_PROMPT)
            
            response = call_OpenAI_API(
                input=messages,
                json_output=True,
                json_schema=QUESTIONER_RESPONSE_SCHEMA
            )
            
            # Handle both dict and string responses
            if isinstance(response, dict):
                # Store the ready_to_stop flag for later checking
                self._last_ready_to_stop = response.get('ready_to_stop', False)
                return response.get('response', '').strip()
            else:
                # Try to parse JSON string
                try:
                    import json
                    parsed_response = json.loads(response)
                    self._last_ready_to_stop = parsed_response.get('ready_to_stop', False)
                    return parsed_response.get('response', '').strip()
                except (json.JSONDecodeError, AttributeError):
                    # Fallback for non-JSON string responses
                    self.logger.warning("Received non-JSON string response, using fallback")
                    self._last_ready_to_stop = False
                    return str(response).strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate first response: {e}")
            self._last_ready_to_stop = False
            return "That's an interesting concept! What drew you to this particular story idea?"

    def _get_user_response(self) -> str:
        """Get user's conversational response."""
        while True:
            try:
                user_input = input("\n💭 ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['done', 'skip', 'enough', 'stop', 'that\'s it']:
                    return user_input.lower()
                
                if user_input:
                    return user_input
                else:
                    print("💡 Please share your thoughts or type 'done' to finish")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Stopping conversation...")
                return "done"
            except Exception as e:
                self.logger.error(f"Error getting user input: {e}")
                print("💡 Please try again or type 'done' to finish")

    def _should_exit(self, response: str) -> bool:
        """Check if user wants to exit."""
        return response.lower() in ['done', 'skip', 'enough', 'stop', 'that\'s it']

    def _record_exchange(self, ai_response: str, user_response: str):
        """Record conversation exchange."""
        if not self._should_exit(user_response):
            self.conversation.append({"role": "assistant", "content": ai_response})
            self.conversation.append({"role": "user", "content": user_response})

    def _format_conversation(self) -> str:
        """Format conversation for context."""
        if len(self.conversation) <= 1:
            return "Just getting started!"
        
        formatted = []
        for i, msg in enumerate(self.conversation[1:], 1):  # Skip initial concept
            role = "You" if msg["role"] == "assistant" else "User"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted) if formatted else "Just getting started!"

    def _build_refined_prompt(self, original_prompt: str) -> str:
        """Compile conversation into a detailed story prompt."""
        if len(self.conversation) <= 1:
            return original_prompt
        
        # Start with original concept
        refined_parts = [f"Story Concept: {original_prompt}"]
        
        # Add conversation insights
        user_responses = []
        for i in range(2, len(self.conversation), 2):  # Skip initial, take user responses
            if i < len(self.conversation):
                response = self.conversation[i]['content']
                user_responses.append(f"• {response}")
        
        if user_responses:
            refined_parts.append("\nAdditional Details:")
            refined_parts.extend(user_responses)
        
        refined_prompt = "\n".join(refined_parts)
        
        print(f"\n✨ Your enhanced story concept:\n{refined_prompt}\n")
        
        return refined_prompt 