import json
import websocket

def unicode_filter(text):
    """Replace common Unicode escape sequences with proper characters."""
    replacements = {
        "\\u201c": "“",  # Opening quotation mark
        "\\u201d": "”",  # Closing quotation mark
        "\\u2018": "‘",  # Single opening quotation mark
        "\\u2019": "’",  # Single closing quotation mark
        "\\u2026": "…",  # Ellipsis
        "\\u2013": "–",  # En dash
        "\\u2014": "—",  # Em dash
    }
    for unicode, char in replacements.items():
        text = text.replace(unicode, char)
    return text

def search_verse(book, chapter, verse, bible_data):
    """Search for a specific chapter and verse in the Bible JSON data."""
    book_data = bible_data.get(book)
    if not book_data:
        return f"Book '{book}' not found."
    chapter_data = book_data.get(str(chapter))
    if not chapter_data:
        return f"Chapter '{chapter}' not found in '{book}'."
    verse_text = chapter_data.get(str(verse))
    if not verse_text:
        return f"Verse '{verse}' not found in '{book} {chapter}'."
    
    # Apply Unicode filtering
    verse_text = unicode_filter(verse_text)
    
    return verse_text

def twitch_bible_bot(oauth_key, client_id, channel_name, username, json_file_path):
    # Load Bible JSON
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            bible_data = json.load(file)
    except FileNotFoundError:
        print("Bible JSON file not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding Bible JSON.")
        return

    # Twitch WebSocket connection
    ws_url = f"wss://irc-ws.chat.twitch.tv:443"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {oauth_key.replace('oauth:', '')}"  # Strip 'oauth:' for the Authorization header
    }
    try:
        ws = websocket.create_connection(ws_url, header=headers)
    except Exception as e:
        print(f"WebSocket error: {e}")
        return

    # Authenticate and join channel
    ws.send(f"PASS {oauth_key}")
    ws.send(f"NICK {username}")
    ws.send(f"JOIN #{channel_name}")

    try:
        while True:
            try:
                # Receive WebSocket message
                ws_data = ws.recv()
                print(f"Received: {ws_data}")

                # Process chat messages formatted as "Book Chapter:Verse"
                if ":" in ws_data:
                    parts = ws_data.split(" ")
                    if len(parts) > 1:
                        book = parts[0]
                        chapter_verse = parts[1]
                        if ":" in chapter_verse:
                            chapter, verse = map(int, chapter_verse.split(":"))
                            result = search_verse(book, chapter, verse, bible_data)
                            print(f"Search result: {result}")

                            # Send the verse to Twitch chat if found
                            if "not found" not in result:
                                ws.send(f"PRIVMSG #{channel_name} :{result}")
            except Exception as e:
                print(f"Error processing chat message: {e}")

    except Exception as e:
        print(f"General error: {e}")
    finally:
        ws.close()

# Example usage
twitch_bible_bot(
    oauth_key="oauth:CmsJiAttmBDJbOc6dsvOAm1t8aak3ixUiM/T56rqTZw=",  # Replace with your Twitch OAuth token
    client_id="fqykjvn3jeznc0courlywwy7orc6pa",  # Replace with your Twitch client ID
    channel_name="badnintendo",  # Replace with your Twitch channel name
    username="TheBiblesQuotes",  # Replace with your bot's Twitch username
    json_file_path="NKJV.json"  # Path to the JSON Bible file
)