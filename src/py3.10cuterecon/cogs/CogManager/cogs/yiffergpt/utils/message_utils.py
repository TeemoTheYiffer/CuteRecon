from collections import defaultdict

def split_response(response, max_length=1900):
    """Split long responses into chunks that Discord can handle."""
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

class ConversationManager:
    def __init__(self, max_history):
        self.conversations = defaultdict(lambda: defaultdict(list))
        self.max_history = max_history

    def append_message(self, author_id, channel_id, role, content):
        """Add a message to the conversation history."""
        if len(self.conversations[author_id][channel_id]) >= self.max_history:
            self.conversations[author_id][channel_id].pop(0)
        
        self.conversations[author_id][channel_id].append({
            "role": role,
            "content": content
        })

    def get_history(self, author_id, channel_id):
        """Get conversation history for a specific user and channel."""
        return self.conversations[author_id][channel_id]

    def clear_history(self, author_id, channel_id):
        """Clear conversation history for a specific user and channel."""
        self.conversations[author_id][channel_id] = []