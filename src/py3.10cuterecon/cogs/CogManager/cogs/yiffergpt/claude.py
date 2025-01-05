import anthropic
from .utils.message_utils import ConversationManager
import os
import re
from .constants import CLAUDE_CONFIG, ANTHROPIC_API_KEY
from .utils.logger_utils import setup_logger

class ClaudeHandler:
    def __init__(self):
        self.client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
        self.conversation_manager = ConversationManager(max_history=10)
        self.instructions = CLAUDE_CONFIG.instructions
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'logs', 'claude.log')
        
        self.logger = setup_logger(
            'claude',
            log_file=log_file,
            level=20  # logging.INFO / 10=logging.debug
        )
        
    async def ask_claude(self, message, instruction=None, combined_input=None, history=True):
        """Send request to Claude API with conversation history."""
        try:
            message_text = combined_input if combined_input else message.content
            self.logger.info(f"[USER → BOT] [User: {message.author.id}] [Channel: {message.channel.id}] {message_text}")

            if instruction is None:
                instruction = self.instructions

            message_text = combined_input if combined_input else message.content
            
            if history:
                self.conversation_manager.append_message(
                    message.author.id,
                    message.channel.id,
                    "user",
                    message_text
                )
                history_messages = self.conversation_manager.get_history(
                    message.author.id,
                    message.channel.id
                )
            else:
                history_messages = [{"role": "user", "content": message_text}]

            system_prompt = f"{instruction}\n\nPrevious conversation context:"
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=2048,
                temperature=0.7,
                system=system_prompt,
                messages=history_messages
            )
            
            assistant_message = response.content[0].text
            self.logger.info(f"[BOT → USER] [User: {message.author.id}] [Channel: {message.channel.id}] {assistant_message}")

            if history:
                self.conversation_manager.append_message(
                    message.author.id,
                    message.channel.id,
                    "assistant",
                    assistant_message
                )
            
            return assistant_message

        except anthropic.RateLimitError as e:
            self.logger.error(f"Rate limit exceeded for User {message.author.id}: {str(e)}")
            return "Sorry, I'm a bit overwhelmed right now and hit the rate limit. Please try again in a few moments. 😅"
        except anthropic.APIError as e:
            self.logger.error(f"API error for User {message.author.id}: {str(e)}")
            return "I encountered an error. Please try again later."
        except Exception as e:
            self.logger.error(f"Unexpected error for User {message.author.id}: {str(e)}", exc_info=True)
            raise

    def set_instructions(self, new_instructions):
        """Update system instructions."""
        self.instructions = new_instructions

    def get_instructions(self):
        """Get current system instructions."""
        return self.instructions

    def get_conversation_history(self, author_id, channel_id):
        """Get conversation history for a user in a channel."""
        return self.conversation_manager.get_history(author_id, channel_id)