import re

def generate_basic_summary(text, num_sentences=3, max_chars=300):
    """
    Generates a very basic summary by taking the first few sentences
    or a character limit, whichever is shorter.
    """
    if not text:
        return ""

    # Split into sentences (basic split, not perfect for all cases)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    summary_sentences = []
    current_char_count = 0
    
    for sentence in sentences[:num_sentences]:
        if current_char_count + len(sentence) <= max_chars:
            summary_sentences.append(sentence)
            current_char_count += len(sentence) + 1 # +1 for space
        else:
            # If adding the full sentence exceeds max_chars, try to truncate it
            remaining_chars = max_chars - current_char_count
            if remaining_chars > 10: # Only add if there's reasonable space
                summary_sentences.append(sentence[:remaining_chars-3] + "...")
            break 
            
    if not summary_sentences: # Fallback if first sentence itself is too long
        return text[:max_chars-3] + "..." if len(text) > max_chars else text

    return " ".join(summary_sentences)
