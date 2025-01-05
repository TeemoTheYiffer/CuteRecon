import logging
import re
import discord

def format_ai_response(response):
    """Format AI response for Discord markdown formatting."""
    # First, standardize newlines
    response = response.replace('\r\n', '\n')
    
    # Handle code blocks first
    code_blocks = []
    def replace_code_block(match):
        # Extract language if specified
        lang = match.group(1) or ''  # Group 1 is the language (if any)
        code = match.group(2).strip()  # Group 2 is the code
        code_blocks.append((lang, code))
        return f"CODE_BLOCK_{len(code_blocks)-1}"
    
    # Temporarily remove code blocks, capturing language specification
    response = re.sub(r'```(?:([\w+#]+)\n)?(.*?)```', replace_code_block, response, flags=re.DOTALL)
    
    # Process the text
    lines = response.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Handle headers
        if line.startswith('**') and line.endswith('**:'):
            if formatted_lines:  # Add extra newline before headers if not first line
                formatted_lines.append('')
            formatted_lines.append(line)
            formatted_lines.append('')
            continue
            
        # Handle bullet points
        if line.startswith('-') or line.startswith('•'):
            if not in_list and formatted_lines:  # Add space before first bullet point
                formatted_lines.append('')
            line = '•' + line[1:] if line.startswith('-') else line
            formatted_lines.append(line)
            in_list = True
            continue
            
        # Handle examples
        if line.lower().startswith('example:'):
            formatted_lines.extend(['', '**Example:**', ''])
            continue
            
        # Regular text
        if in_list:  # Add space after list ends
            formatted_lines.append('')
            in_list = False
        formatted_lines.append(line)
    
    # Join lines with newlines
    response = '\n'.join(formatted_lines)
    
    # Restore code blocks with proper spacing and original language
    for i, (lang, code) in enumerate(code_blocks):
        lang_spec = f'{lang}\n' if lang else ''
        response = response.replace(
            f"CODE_BLOCK_{i}",
            f"```{lang_spec}{code}```"
        )
    
    # Ensure proper spacing around code blocks (but not after)
    response = re.sub(r'\n```', '\n\n```', response)  # Space before code block
    response = re.sub(r'```\n', '```\n', response)    # No extra space after code block
    
    # Final cleanup
    response = re.sub(r'\n{3,}', '\n\n', response)  # Replace multiple newlines with double newlines
    response = response.strip()
    
    return response

def split_discord_message(response, max_length=1900):
    """
    Split messages into chunks while preserving markdown formatting.
    Ensures each chunk is under Discord's limit.
    """
    if len(response) <= max_length:
        return [response]
        
    chunks = []
    lines = response.split('\n')
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_with_newline = line + '\n'
        line_length = len(line_with_newline)
        
        # If this single line is too long, split it
        if line_length > max_length:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # Split long line into smaller chunks
            words = line.split(' ')
            current_line = []
            current_line_length = 0
            
            for word in words:
                word_length = len(word) + 1  # +1 for space
                if current_line_length + word_length > max_length:
                    if current_line:
                        chunks.append(' '.join(current_line))
                        current_line = []
                        current_line_length = 0
                current_line.append(word)
                current_line_length += word_length
                
            if current_line:
                chunks.append(' '.join(current_line))
            continue
            
        # If adding this line would exceed the limit
        if current_length + line_length > max_length:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(line)
        current_length += line_length
    
    # Add any remaining content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

async def send_discord_message(message, response, logging_enabled=True):
    """Send a formatted message through Discord."""
    try:
        formatted_response = format_ai_response(response)
        
        if logging_enabled:
            logging.info(f"Formatted response:\n{formatted_response}")
        
        chunks = split_discord_message(formatted_response)
        
        for i, chunk in enumerate(chunks):
            if logging_enabled:
                logging.info(f"Sending chunk {i+1}/{len(chunks)}")
                
            # Verify chunk length before sending
            if len(chunk) >= 2000:
                logging.warning(f"Chunk {i+1} exceeds Discord's limit, further splitting required")
                subchunks = split_discord_message(chunk, max_length=1900)
                for subchunk in subchunks:
                    if i == 0:
                        await message.reply(subchunk)
                    else:
                        await message.channel.send(subchunk)
            else:
                if i == 0:
                    await message.reply(chunk)
                else:
                    await message.channel.send(chunk)
                    
    except Exception as e:
        logging.error(f"Error sending Discord message: {str(e)}", exc_info=True)
        raise

async def send_discord_message(message, response, logging_enabled=True):
    """
    Format, split if necessary, and send a message through Discord.
    
    Args:
        message (discord.Message): The original Discord message to reply to
        response (str): The response text to send
        logging_enabled (bool): Whether to log the response chunks
    """
    #if logging_enabled:
    #    logging.info(f"Pre-formatting response:\n{response}")
    
    formatted_response = format_ai_response(response)
    
    #if logging_enabled:
    #    logging.info(f"Post-formatting response:\n{formatted_response}")
    
    # Split into chunks if necessary
    chunks = split_discord_message(formatted_response)
    
    for chunk in chunks:
        if logging_enabled:
            logging.info(f"Sending chunk to {message.author.name}: {chunk[:100]}...")
        await message.reply(chunk)

async def send_discord_file(channel, file_data, filename, content=None):
    """
    Send a file through Discord with optional message content.
    
    Args:
        channel (discord.TextChannel): The Discord channel to send to
        file_data (BytesIO/str): The file data to send
        filename (str): Name of the file
        content (str, optional): Additional message content
    """
    if isinstance(file_data, str):  # Error message
        await channel.send(f"Sorry, an error occurred: {file_data}")
    else:
        await channel.send(
            content=content,
            file=discord.File(file_data, filename=filename)
        )