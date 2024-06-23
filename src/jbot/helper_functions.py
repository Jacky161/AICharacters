"""
Helper functions used in JBot
"""


def paragraph_split(text: str, max_per_chunk: int = 1024) -> list[str]:
    """
    Splits a text into (maximum) 1024 character chunks. Tries to split cleanly along sentences whenever possible.
    """
    # Split into paragraphs (\n)
    paragraphs = text.split("\n")
    chunks = []

    # Process all paragraphs
    while len(paragraphs) > 0:
        cur_chunk = ""

        # Keep adding until we cannot cleanly add anymore paragraphs without reaching the limit
        while len(paragraphs[0]) + len(cur_chunk) + 1 <= max_per_chunk:
            cur_chunk += paragraphs.pop(0) + "\n"

            if len(paragraphs) == 0:
                break

        # Case where we have one paragraph 1024 characters or longer.
        if cur_chunk == "" and len(paragraphs) > 0:
            punctuations = [".", "?", "!"]

            # Split based on punctuation if possible, otherwise it splits on the 1023 characters mark.
            # Subtract 1 to account for the "\n" character
            cur_chunk, paragraphs[0] = split_substring_before(paragraphs[0], punctuations, max_per_chunk - 1)
            cur_chunk += "\n"

        # We have our chunk, add it into the list
        chunks.append(cur_chunk)

    return chunks


def split_substring_before(text: str, substrings: list[str], before: int) -> tuple[str, str]:
    """
    Splits a given text on any of the substrings given. The substrings are searched for in the index values before
    the one provided. If no substrings are found, we split the text in two pieces. All text before the "before index"
    and all text after it.
    """
    search_segment = text[:before]

    # Search for the last piece of any substring
    last_substring_idx = find_substring_last(search_segment, substrings)

    if last_substring_idx == -1:
        # Didn't find any substrings
        return text[:before], text[before:]

    # Found a substring, split on it
    return text[:last_substring_idx], text[last_substring_idx:]


def find_substring_last(text: str, substrings: list[str]) -> int:
    """
    Finds the last occurrence of ANY substring in the provided list. Returns -1 if no substrings are found.
    """
    max_idx = -1
    for substring in substrings:
        cur_idx = text.rfind(substring)

        if cur_idx > max_idx:
            max_idx = cur_idx

    return max_idx
