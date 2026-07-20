import re
from typing import AsyncGenerator

async def chunk_sentences(async_text_gen: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Consumes an async generator of text chunks and yields complete sentences.
    """
    buffer = ""
    # Simple regex to split on sentence boundaries (. ! ?) followed by space
    # It keeps the punctuation with the sentence.
    sentence_end_re = re.compile(r'(.*?[.!?])(?:\s+|$)', re.DOTALL)
    
    async for chunk in async_text_gen:
        buffer += chunk
        
        while True:
            match = sentence_end_re.match(buffer)
            if match:
                sentence = match.group(1).strip()
                if sentence:
                    yield sentence
                buffer = buffer[match.end():]
            else:
                break
                
    # Yield any remaining text in the buffer
    buffer = buffer.strip()
    if buffer:
        yield buffer
