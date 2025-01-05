import websockets
import json
import base64
import asyncio
import io
import os
from discord import FFmpegPCMAudio
from .utils.logger_utils import setup_logger
import tempfile

class ElevenLabsHandler:
    def __init__(self, bot):
        self.bot = bot  # Store bot instance
        self.api_key = os.environ["ELEVEN_LABS_API_KEY"]
        self.voice_id = "UgBBYS2sOqTuMpoF3BR0"
        self.websocket_uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input?model_id=eleven_flash_v2_5"
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'logs', 'elevenlabs.log')
        self.logger = setup_logger('elevenlabs', log_file=log_file, level=20)

    async def text_chunker(self, async_iterable):
        """Split text into chunks at natural break points."""
        splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
        buffer = ""

        try:
            async for text in async_iterable:
                if text is None:
                    continue
                    
                if buffer.endswith(splitters):
                    yield buffer + " "
                    buffer = text
                elif text.startswith(splitters):
                    yield buffer + text[0] + " "
                    buffer = text[1:]
                else:
                    buffer += text

            if buffer:
                yield buffer + " "
                
        except Exception as e:
            self.logger.error(f"Error in text chunker: {str(e)}")
            raise

    async def stream_to_discord(self, text_iterator, voice_client):
        """Stream audio to Discord using websockets."""
        try:
            if not voice_client.is_connected():
                return

            async with websockets.connect(self.websocket_uri) as websocket:
                # Initialize the stream
                await websocket.send(json.dumps({
                    "text": " ",
                    "voice_settings": {
                        "stability": 0.5, 
                        "similarity_boost": 0.8
                        #"speaking_rate": 0.85 
                    },
                    "xi_api_key": self.api_key,
                }))

                # Create a queue for audio chunks
                audio_queue = asyncio.Queue()
                first_chunk_event = asyncio.Event()
                
                # Audio processing coroutine
                async def process_websocket():
                    try:
                        while True:
                            message = await websocket.recv()
                            data = json.loads(message)
                            
                            if data.get("audio"):
                                chunk = base64.b64decode(data["audio"])
                                await audio_queue.put(chunk)
                                if not first_chunk_event.is_set():
                                    first_chunk_event.set()
                                    
                            elif data.get('isFinal'):
                                await audio_queue.put(None)  # Signal end of stream
                                break
                                
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.error("WebSocket connection closed unexpectedly")
                        await audio_queue.put(None)
                    except Exception as e:
                        self.logger.error(f"Error in websocket processing: {str(e)}")
                        await audio_queue.put(None)

                # Start websocket processing
                websocket_task = asyncio.create_task(process_websocket())

                # Send text chunks
                try:
                    async for text in self.text_chunker(text_iterator):
                        if text.strip():
                            await websocket.send(json.dumps({"text": text}))
                except Exception as e:
                    self.logger.error(f"Error sending text chunks: {str(e)}")
                    raise

                # Send empty text to signal the end
                await websocket.send(json.dumps({"text": ""}))

                # Wait for first chunk of audio
                await first_chunk_event.wait()

                # Process audio chunks
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_filename = temp_file.name
                    
                    while True:
                        chunk = await audio_queue.get()
                        if chunk is None:  # End of stream
                            break
                        temp_file.write(chunk)
                        temp_file.flush()

                    # Play the audio
                    if voice_client.is_playing():
                        voice_client.stop()

                    audio_source = FFmpegPCMAudio(
                        temp_filename,
                        options='-loglevel error -vn -filter:a "atempo=1.0"'
                    )
                    voice_client.play(audio_source)

                    # Wait for playback to complete
                    while voice_client.is_playing():
                        await asyncio.sleep(0.1)

                    # Cleanup
                    try:
                        os.unlink(temp_filename)
                    except Exception as e:
                        self.logger.error(f"Error cleaning up temp file: {str(e)}")

                # Wait for websocket processing to complete
                await websocket_task

        except Exception as e:
            self.logger.error(f"Error in websocket streaming: {str(e)}")
            raise

    async def connect_to_voice(self, voice_channel):
        """Connect to a voice channel."""
        try:
            #guild_id = voice_channel.guild.id
            
            # If bot is already connected to a voice channel in this guild
            if voice_channel.guild.voice_client is not None:
                existing_client = voice_channel.guild.voice_client
                
                # If already in the requested channel
                if existing_client.channel.id == voice_channel.id:
                    return existing_client
                
                # If in a different channel
                await existing_client.move_to(voice_channel)
                return existing_client
                
            # Not connected to any channel in this guild
            voice_client = await voice_channel.connect()
            return voice_client
                
        except Exception as e:
            self.logger.error(f"Error connecting to voice: {str(e)}", exc_info=True)
            raise

    async def disconnect_from_voice(self, guild_id):
        """Disconnect from a voice channel."""
        try:
            guild = self.bot.get_guild(guild_id)
            if guild and guild.voice_client:
                # Add a small delay before disconnecting
                await asyncio.sleep(0.5)
                
                if guild.voice_client.is_playing():
                    guild.voice_client.stop()
                
                await guild.voice_client.disconnect(force=False)
                
        except Exception as e:
            self.logger.error(f"Error disconnecting: {str(e)}", exc_info=True)

    def set_voice(self, voice_id):
        """Update the voice ID setting."""
        self.voice_id = voice_id
        
    def get_voice(self):
        """Get current voice ID setting."""
        return self.voice_id