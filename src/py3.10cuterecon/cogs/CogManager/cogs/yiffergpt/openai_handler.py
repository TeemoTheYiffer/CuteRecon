import openai
import base64
import requests
import cv2
import os
from io import BytesIO
from .utils.message_utils import ConversationManager
from .utils.logger_utils import setup_logger
from .constants import CHATTY_INSTRUCTIONS, OPENAI_API_KEY, OPENAI_ORGANIZATION

class OpenAIHandler:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        openai.organization = OPENAI_ORGANIZATION
        self.conversation_manager = ConversationManager(max_history=20)
        self.tts_voice = "onyx"
        self.instructions = CHATTY_INSTRUCTIONS
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'logs', 'openai.log')
        
        self.logger = setup_logger(
            'openai',
            log_file=log_file,
            level=20  # logging.INFO / 10=logging.debug
        )

    def openai_tts(self, input):
        """Generate text-to-speech using OpenAI's API."""
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1-hd",
            "input": input,
            "voice": self.tts_voice
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            return f"Error: {response.status_code} - {response.text}"

    async def process_image(self, image_url, user_query=None):
        """Process image for vision-based queries."""
        base64_image = base64.b64encode(requests.get(image_url).content).decode('utf-8')
        extra = [
            {
                "type": "text",
                "text": user_query if user_query else ""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]
        return extra

    async def process_video(self, video_url, user_query=None):
        """Process video for analysis."""
        video = cv2.VideoCapture(video_url)
        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        
        video.release()
        self.logger.info(f"{len(base64Frames)} frames read.")
        
        if not user_query:
            user_query = "Generate a compelling description for this video."
            
        combined_input = [
            user_query,
            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::10])
        ]
        return combined_input
    
    def sanitize_log_content(self, content):
        """
        Sanitize content for logging by replacing large binary/base64 data.
        
        Args:
            content: The content to sanitize (can be string, dict, or list)
        Returns:
            Sanitized content safe for logging
        """
        if isinstance(content, str):
            # If it looks like base64 data (long string with base64 chars)
            if len(content) > 100 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in content):
                return '[BASE64_DATA]'
            return content
        elif isinstance(content, dict):
            sanitized_dict = {}
            for key, value in content.items():
                if key == 'image':
                    sanitized_dict[key] = '[IMAGE_DATA]'
                else:
                    sanitized_dict[key] = self.sanitize_log_content(value)
            return sanitized_dict
        elif isinstance(content, list):
            return [self.sanitize_log_content(item) for item in content]
        return content

    async def ask_gpt(self, message, model="gpt-4o", instruction=None, combined_input=None, history=True, stream=False):
        """Send request to OpenAI API with conversation history and optional streaming."""
        try:
            if combined_input:
                log_content = self.sanitize_log_content(combined_input)
                self.logger.info(f"[USER → BOT] [User: {message.author.id}] [Channel: {message.channel.id}] {log_content}")
                if isinstance(combined_input, list) and any(isinstance(item, dict) and 'image' in item for item in combined_input):
                    # Extract text and images from combined input
                    text_content = next((item for item in combined_input if isinstance(item, str)), "Describe this image.")
                    image_contents = [item for item in combined_input if isinstance(item, dict) and 'image' in item]
                    
                    # Format content for vision API
                    formatted_content = [
                        {
                            "type": "text",
                            "text": text_content
                        }
                    ]
                    
                    # Add image contents
                    for img in image_contents:
                        formatted_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img['image']}"
                            }
                        })
                    
                    messages = [
                        {
                            "role": "user",
                            "content": formatted_content
                        }
                    ]
                else:
                    # Handle regular combined input
                    messages = [
                        {
                            "role": "system",
                            "content": instruction if instruction else self.instructions
                        },
                        {
                            "role": "user",
                            "content": combined_input
                        }
                    ]
            else:
                message_text = message.content
                log_content = self.sanitize_log_content(message_text)
                self.logger.info(f"[USER → BOT] [User: {message.author.id}] [Channel: {message.channel.id}] {log_content}")
                
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
                    
                messages = [
                    {
                        "role": "system",
                        "content": instruction if instruction else self.instructions
                    }
                ] + [
                    {
                        "role": msg["role"],
                        "content": msg["content"]
                    } for msg in history_messages
                ]
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=0.8,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stream=stream
            )

            if stream:
                async def content_generator():
                    async for chunk in response:
                        if hasattr(chunk.choices[0].delta, 'content'):
                            content = chunk.choices[0].delta.content
                            if content is not None:
                                yield content

                return content_generator()
            else:
                # Handle non-streaming response as before
                assistant_message = response['choices'][0]['message']['content'].strip()
                self.logger.info(f"[BOT → USER] [User: {message.author.id}] [Channel: {message.channel.id}] {assistant_message}...")

                if history:
                    self.conversation_manager.append_message(
                        message.author.id,
                        message.channel.id,
                        "assistant",
                        assistant_message
                    )

                return assistant_message

        except openai.error.RateLimitError as e:
            self.logger.error(f"Rate limit exceeded for User {message.author.id}: {str(e)}")
            return "Sorry, I'm a bit overwhelmed right now and hit the rate limit. Please try again in a few moments. 😅"
        except Exception as e:
            self.logger.error(f"Error for User {message.author.id}: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
        
    def set_voice(self, voice):
        """Update TTS voice setting."""
        self.tts_voice = voice

    def get_voice(self):
        """Get current TTS voice setting."""
        return self.tts_voice

    def set_instructions(self, new_instructions):
        """Update system instructions."""
        self.instructions = new_instructions

    def get_instructions(self):
        """Get current system instructions."""
        return self.instructions

    def get_conversation_history(self, author_id, channel_id):
        """Get conversation history for a user in a channel."""
        return self.conversation_manager.get_history(author_id, channel_id)