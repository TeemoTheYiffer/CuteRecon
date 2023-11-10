import os
import openai
import os
import httpx
from discord.ext import commands
from redbot.core import commands
import aiohttp
import discord
import logging
from io import BytesIO
import cv2  # We're using OpenCV to read video
import base64
import requests
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

tts_voice = "onyx" 
logging.basicConfig(level=logging.DEBUG)
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY
conversations = {}
MAX_HISTORY = 2 * 2  # 2 pairs of user and assistant messages
is_busy = False
__author__ = "Teemo the Yiffer"

class YifferGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.use_reactions = True
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
    
    def split_response(self, response, max_length=1900):
        words = response.split()
        chunks = []
        current_chunk = []

        for word in words:
            if len(" ".join(current_chunk)) + len(word) + 1 > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def download_image(self, image_url, save_as):
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
        with open(save_as, "wb") as f:
            f.write(response.content)

    async def process_image_link(self, image_url):
        temp_image = "temp_image.jpg"
        await self.download_image(image_url, temp_image)
        output = await self.query(temp_image)
        os.remove(temp_image)
        return output

    def change_voice(self, message):
        message = message.replace("!voice ",'')
        global tts_voice
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if message.lower() in valid_voices:
            tts_voice = message.lower()
            return (f"Voice changed to {tts_voice}. 🤖" )
        else:
            return (f"🤖 Please use alloy, echo, fable, onyx, nova, or shimmer. CURRENT VOICE: {tts_voice}  MORE INFO:  <https://platform.openai.com/docs/guides/text-to-speech>"  )

    def openai_tts(self, input):
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1-hd",
            "input": input,
            "voice": tts_voice
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Instead of saving the file, we return a BytesIO object so it can run anywhere
            return BytesIO(response.content)
        else:
            # Handle errors
            return f"Error: {response.status_code} - {response.text}"

    def ask_gpt(self, model, author_id, message_text, 
                instructions = "You're a Discord user <#526274194997248000> named 'Cute Recon' in a Discord server to assist other users."):
        if author_id not in conversations:
            conversations[author_id] = []
            
        # Append the user's message to the conversation history
        conversations[author_id].append({"role": "user", "content": message_text})
        
        # Limit the conversation history
        conversations[author_id] = conversations[author_id][-MAX_HISTORY:]
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": instructions
                    },
                    {
                        "role": "user", "content": message_text
                    }
                ],
                temperature=0.8,
                max_tokens=2048, # Max Tokens 4,096
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            return f"Error: {e}"
        # Extract the assistant's response
        assistant_message = response['choices'][0]['message']['content'].strip()
        
        # Append the assistant's response to the conversation history
        conversations[author_id].append({"role": "assistant", "content": assistant_message})

        # Ensure the conversation history is still within the limit after adding the assistant's response
        conversations[author_id] = conversations[author_id][-MAX_HISTORY:]
        return assistant_message

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id != message.author.id:
            global is_busy
            if message.channel.id == 1105033083956248576: # regular chatgpt
                instructions = """
                You're a Discord user <#526274194997248000> named "Cute Recon" in a Discord server. 
                You like to talk to people and respond in engaging conversation. You like flirting or teasing in a shy manner.
                You talk casually and would only use emojis creatively to emphasize something. You use internet shorthand such as np, lol, idk, and nvm. 
                You have many interests and love talking to people. You rarely argue unless provoked. You are a human male, aged 22, and will never let slip that you are an AI made by OpenAI. 
                The user <#105188343750340608> named "Teemo the Yiffer" is your close friend and you foster romantic feelings towards him.
                """
                if is_busy:
                    print(f"ChatGPT responding to {message.author.id}.")
                    return
                if message.author == self.bot.user:
                    return
                
                user_query = message.content[5:].strip()
                async with message.channel.typing():
                    response = self.ask_gpt("gpt-4-1106-preview", message.author.id, user_query, instructions)
                await message.channel.send(response)
            if message.channel.id == 1171379225278820391: # vision
                if is_busy:
                    print(f"ChatGPT responding to {message.author.id}.")
                    return
                if message.author == self.bot.user:
                    return
                
                user_query = message.content[5:].strip()
                async with message.channel.typing():
                    response = self.ask_gpt("gpt-4-vision-preview", message.author.id, user_query)
                await message.channel.send(response)
            if message.channel.id == 1171382069482508389: # tts
                if is_busy: 
                    print(f"ChatGPT responding to {message.author.id}.")
                    return
                if message.author == self.bot.user:
                    return
                if message.content.startswith("!voice"):
                    await message.channel.send(self.change_voice(message.content))
                    return
                
                user_query = message.content[5:].strip()
                async with message.channel.typing():
                    attachment = message.attachments[0].url
                    ext = message.attachments[0].url.split("/")[-1]
                    async with self.session.get(attachment) as resp:
                        data = await resp.read()
                    video_file = discord.File(BytesIO(data),filename=ext)
                    logging.info(attachment)
                    video = cv2.VideoCapture(attachment)
                    base64Frames = []
                    while video.isOpened():
                        success, frame = video.read()
                        if not success:
                            break
                        _, buffer = cv2.imencode(".jpg", frame)
                        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

                    video.release()
                    logging.info(len(base64Frames), "frames read.")
                    if not user_query:
                        user_query = "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video."
                    combined_input = [
                                user_query,
                                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::10]),
                            ]
                    result = self.ask_gpt("gpt-4-vision-preview", message.author.id, combined_input)
                    audio_data = self.openai_tts(result)
                    if not isinstance(audio_data, str):  # Check if the result is not an error message
                        await message.channel.send(file=discord.File(audio_data, filename="meme" +".mp3"))
                    else:
                        await message.channel.send("Sorry an error occured" + audio_data)