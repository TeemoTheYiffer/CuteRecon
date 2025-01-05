import os
import asyncio
from redbot.core import commands
import aiohttp
from .openai_handler import OpenAIHandler
from .claude import ClaudeHandler
from .utils import send_discord_message, send_discord_file
from .utils.logger_utils import setup_logger
from .eleven_labs_handler import ElevenLabsHandler  
from .constants import TTS_CONFIG 

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

class YifferGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.use_reactions = True
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.openai_handler = OpenAIHandler()
        self.claude_handler = ClaudeHandler()
        self.eleven_labs_handler = ElevenLabsHandler(bot)
        self.is_busy = False
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'logs', 'discord.log')
        
        self.logger = setup_logger(
            'discord',
            log_file=log_file,
            level=20  # logging.INFO / 10=logging.debug
        )

    async def handle_elevenlabs_tts(self, message):
        """Handle text-to-speech using websocket streaming."""
        try:
            if not message.author.voice or not message.author.voice.channel:
                await message.channel.send("Please join a voice channel first! 🎙️")
                return

            voice_channel = message.author.voice.channel
            status_msg = await message.channel.send("🎯 Processing your request...")

            try:
                # Connect to voice while getting OpenAI response
                voice_client = await self.eleven_labs_handler.connect_to_voice(voice_channel)
                
                # Get streaming response from OpenAI
                response_stream = await self.openai_handler.ask_gpt(
                    message,
                    instruction=TTS_CONFIG.instructions,
                    history=False,
                    stream=True
                )

                await status_msg.edit(content="🎙️ Starting voice stream...")

                # Create an async generator that yields text chunks
                async def text_iterator():
                    complete_text = ""
                    async for text in response_stream:
                        if text:
                            complete_text += text
                            yield text
                    
                    # Store the complete response
                    await message.channel.send(complete_text)

                # Stream directly to Discord voice
                await self.eleven_labs_handler.stream_to_discord(
                    text_iterator(),
                    voice_client
                )

                # Clean up
                await status_msg.delete()
                await self.eleven_labs_handler.disconnect_from_voice(message.guild.id)

            except Exception as e:
                await status_msg.edit(content=f"❌ Error: {str(e)}")
                self.logger.error(f"Error in TTS: {str(e)}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Error in message handling: {str(e)}", exc_info=True)

    @commands.command()
    async def leave_voice(self, ctx):
        """Command to make the bot leave the voice channel."""
        try:
            await self.eleven_labs_handler.disconnect_from_voice(ctx.guild.id)
            await ctx.send("Left the voice channel! 👋")
        except Exception as e:
            await ctx.send(f"Error leaving voice channel: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Main message handler that routes to appropriate AI service."""
        if message.author == self.bot.user:
            return

        if self.is_busy:
            self.logger.info(f"Bot is busy, skipping message from {message.author.id}")
            return

        try:
            self.is_busy = True

            # Route to appropriate handler based on channel
            if message.channel.id == 1105033083956248576:  # regular chatgpt
                await self.handle_openai_chat(message)
            elif message.channel.id == 1171379225278820391:  # vision
                await self.handle_openai_vision(message)
            elif message.channel.id == 1171382069482508389:  # tts
                await self.handle_openai_tts(message)
            elif message.channel.id == 1317970533488394261:  # claude-coding
                await self.handle_claude_chat(message)
            elif message.channel.id == 1319538789475160074:  # elevenlabs tts
                await self.handle_elevenlabs_tts(message)
                
        except Exception as e:
            self.logger.error(f"Error in message handling: {str(e)}", exc_info=True)
        finally:
            self.is_busy = False

    # Add voice command for ElevenLabs
    @commands.command()
    async def set_eleven_voice(self, ctx, voice_id):
        """Update ElevenLabs voice ID setting."""
        try:
            self.eleven_labs_handler.set_voice(voice_id)
            await ctx.channel.send(f"ElevenLabs voice changed to {voice_id} 🎙️")
        except Exception as e:
            await ctx.channel.send(f"Error changing voice: {str(e)}")

    @commands.command()
    async def get_eleven_voice(self, ctx):
        """Get current ElevenLabs voice ID setting."""
        voice_id = self.eleven_labs_handler.get_voice()
        await ctx.channel.send(f"Current ElevenLabs voice ID: `{voice_id}`")

    async def handle_openai_vision(self, message):
        """Handle OpenAI vision-based messages."""
        async def generate_response():
            if message.attachments:
                extra = await self.openai_handler.process_image(
                    message.attachments[0].url,
                    message.content
                )
                response = await self.openai_handler.ask_gpt(message, combined_input=extra)
                await send_discord_message(message, response)

        async with message.channel.typing():
            await asyncio.create_task(generate_response())

    async def handle_openai_tts(self, message):
        """Handle OpenAI text-to-speech messages."""
        async def generate_response():
            if message.attachments:
                combined_input = await self.openai_handler.process_video(
                    message.attachments[0].url,
                    message.content
                )
                result = await self.openai_handler.ask_gpt(
                    message,
                    combined_input=combined_input,
                    history=False
                )
                audio_data = self.openai_handler.openai_tts(result)
                await send_discord_file(
                    message.channel,
                    audio_data,
                    "response.mp3"
                )

        async with message.channel.typing():
            await asyncio.create_task(generate_response())

    async def handle_openai_chat(self, message):
        async def generate_response():
            response = await self.openai_handler.ask_gpt(message)
            await send_discord_message(message, response)

        async with message.channel.typing():
            await asyncio.create_task(generate_response())

    async def handle_claude_chat(self, message):
        async def generate_response():
            response = await self.claude_handler.ask_claude(message)
            await send_discord_message(message, response)

        async with message.channel.typing():
            await asyncio.create_task(generate_response())

    @commands.command()
    async def voice(self, ctx, new_voice):
        """Update TTS voice setting."""
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if new_voice.lower() in valid_voices:
            self.openai_handler.set_voice(new_voice.lower())
            await ctx.channel.send(f"Voice changed to {new_voice}. 🤖")
        else:
            current_voice = self.openai_handler.get_voice()
            await ctx.channel.send(
                f"🤖 Please use alloy, echo, fable, onyx, nova, or shimmer. "
                f"CURRENT VOICE: {current_voice}"
            )

    @commands.command()
    async def get_voice(self, ctx):
        """Get current TTS voice setting."""
        current_voice = self.openai_handler.get_voice()
        await ctx.channel.send(f"Current TTS Voice: `{current_voice}`")

    @commands.command()
    async def instruction(self, ctx):
        """Update AI instruction prompt."""
        new_instructions = ctx.message.content.replace("!instruction ", '')
        
        # Update instructions for both handlers
        if ctx.channel.id == 1317970533488394261:  # claude-coding channel
            self.claude_handler.set_instructions(new_instructions)
        else:
            self.openai_handler.set_instructions(new_instructions)
            
        await ctx.channel.send(f"Done! My new instructions are: `{new_instructions}`")

    @commands.command()
    async def get_instruction(self, ctx):
        """Get current instruction prompt."""
        if ctx.channel.id == 1317970533488394261:  # claude-coding channel
            current_instructions = self.claude_handler.get_instructions()
        else:
            current_instructions = self.openai_handler.get_instructions()
            
        await ctx.channel.send(f"Current Instructions: `{current_instructions}`")

    @commands.command()
    async def get_history(self, ctx):
        """Get conversation history for the current user."""
        if ctx.channel.id == 1317970533488394261:  # claude-coding channel
            history = self.claude_handler.get_conversation_history(
                ctx.message.author.id,
                ctx.channel.id
            )
        else:
            history = self.openai_handler.get_conversation_history(
                ctx.message.author.id,
                ctx.channel.id
            )

        if not history:
            await ctx.channel.send("No conversation history found.")
            return
            
        formatted_history = "\n".join(
            f"{msg['role']}: {msg['content'][:100]}..." 
            for msg in history
        )
        
        await ctx.channel.send(
            f"Your recent conversation history (truncated):\n```\n{formatted_history}\n```"
        )

    async def cleanup(self):
        """Cleanup method to close the aiohttp session."""
        if self.session:
            await self.session.close()