# utils/audio_utils.py
import discord
import queue
from typing import Optional

class StreamingFFmpegAudio(discord.AudioSource):
    """Custom audio source for streaming audio chunks to Discord."""
    
    def __init__(self):
        self.stream_queue = queue.Queue()
        self.exhausted = False
        
    def write_chunk(self, chunk: bytes):
        """Add an audio chunk to the queue."""
        if chunk:
            self.stream_queue.put(chunk)
            
    def mark_exhausted(self):
        """Mark the stream as exhausted (no more data coming)."""
        self.exhausted = True
        
    def read(self) -> Optional[bytes]:
        """Read 20ms of audio data (required by Discord voice)."""
        if self.stream_queue.empty() and self.exhausted:
            return None
            
        try:
            # Get chunk from queue, don't wait if empty
            data = self.stream_queue.get_nowait()
            return data
        except queue.Empty:
            # Return silence if no data available yet
            return b'\x00' * 3840  # 20ms of silence
            
    def cleanup(self):
        """Cleanup resources."""
        self.exhausted = True
        # Clear any remaining items in queue
        while not self.stream_queue.empty():
            try:
                self.stream_queue.get_nowait()
            except queue.Empty:
                break

    def is_opus(self) -> bool:
        """Tell Discord this is not encoded as Opus."""
        return False