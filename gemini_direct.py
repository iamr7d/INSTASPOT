import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
import io
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel

# Initialize Gemini API
GEMINI_API_KEY = "AIzaSyCrrI9afCEbsb2dEIBe1glgNYXPR2o4HJA"
genai.configure(api_key=GEMINI_API_KEY)

def describe_image(image_data):
    """
    Describe an image using Gemini API and suggest multiple related keywords for music search.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        str: Description and keyword suggestion
    """
    try:
        # Changed model to gemini-1.5-flash as gemini-pro-vision is deprecated
        gemini = GenerativeModel("gemini-1.5-flash")
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Create a more detailed prompt that asks for multiple keywords
        prompt = """
        Analyze this image in detail and provide the following:
        
        1. **Description:** Provide a detailed description of the image, including people, objects, setting, colors, and mood.
        
        2. **Music Keywords:** Suggest 5-7 music-related keywords that would match this image. Include a diverse mix of:
           - Genre keywords (e.g., Rock, Jazz, Classical, Hip-hop, EDM, Folk)
           - Mood keywords (e.g., Upbeat, Melancholic, Energetic, Calm)
           - Cultural keywords if applicable (e.g., Indian, Latin, African)
           - Instrumental keywords if applicable (e.g., Guitar-driven, Piano, Orchestral)
           - Era/decade keywords if applicable (e.g., 80s, Retro, Modern)
        
        3. **Instagram Caption:** Create a catchy, engaging Instagram caption that:
           - Captures the mood and essence of the image
           - Includes 1-2 relevant hashtags
           - Is between 1-3 sentences long
           - Has an emotional or inspirational tone
           - Would resonate with social media users
        
        Format your response exactly as follows:
        **Description:** [Your detailed description]
        
        **Music Keywords:** [Keyword 1], [Keyword 2], [Keyword 3], [Keyword 4], [Keyword 5], [Keyword 6], [Keyword 7]
        
        **Instagram Caption:** [Your caption suggestion]
        """
        
        # Generate content
        response = gemini.generate_content([prompt, image])
        
        return response.text.strip()
    except Exception as e:
        print(f"Error describing image: {e}")
        return "Could not describe the image. Please try again with a different image."

def extract_keyword_from_description(description):
    """
    Extract multiple keywords from the description for Spotify search.
    This is an intelligent implementation that extracts the most relevant music keywords.
    
    Args:
        description (str): Image description from Gemini
        
    Returns:
        list: List of keywords for Spotify search
        str: Primary keyword for Spotify search
    """
    try:
        # Define comprehensive lists of music-related terms
        # Expanded genre terms
        genre_terms = [
            # Western genres
            "Rock", "Pop", "Hip-hop", "Rap", "R&B", "Soul", "Jazz", "Blues", "Classical", 
            "Country", "Folk", "Electronic", "EDM", "Techno", "House", "Trance", "Ambient", 
            "Lo-fi", "Indie", "Alternative", "Metal", "Punk", "Grunge", "Disco", "Funk",
            "Reggae", "Ska", "Dubstep", "Drum and Bass", "Trap", "Gospel", "Christian",
            "New Age", "Experimental", "Psychedelic", "Progressive", "Synthwave", "Vaporwave",
            
            # Cultural/Regional genres
            "Indian", "Bollywood", "Rajasthani", "Carnatic", "Hindustani", "Bhangra", "Ghazal",
            "Latin", "Salsa", "Bachata", "Reggaeton", "Merengue", "Cumbia", "Bossa Nova", "Samba",
            "African", "Afrobeat", "Highlife", "Soukous", "Mbalax", "Juju", "Fuji",
            "Asian", "K-pop", "J-pop", "C-pop", "Mandopop", "Cantopop", "Anime", 
            "Middle Eastern", "Arabic", "Turkish", "Persian", "Rai", "Gnawa",
            "European", "Flamenco", "Fado", "Celtic", "Nordic", "Polka", "Balkan",
            
            # Fusion genres
            "World Music", "Fusion", "Crossover", "World Fusion", "Ethnic Fusion",
            "Jazz Fusion", "Classical Crossover", "Folk Rock", "Country Rock", "Pop Rock",
            "Rap Rock", "Nu Metal", "Industrial Metal", "Folk Metal", "Celtic Metal",
            "Latin Jazz", "Afro-Cuban", "Indo-Jazz", "Ethno-Jazz", "Tribal House"
        ]
        
        # Expanded mood terms
        mood_terms = [
            "Happy", "Sad", "Energetic", "Calm", "Relaxed", "Excited", "Nostalgic",
            "Romantic", "Melancholic", "Upbeat", "Chill", "Dreamy", "Intense",
            "Peaceful", "Joyful", "Somber", "Playful", "Reflective", "Passionate",
            "Angry", "Aggressive", "Anxious", "Hopeful", "Optimistic", "Pessimistic",
            "Gloomy", "Bright", "Dark", "Ethereal", "Mystical", "Spiritual", "Sacred",
            "Triumphant", "Victorious", "Defeated", "Lonely", "Isolated", "Connected",
            "Communal", "Festive", "Celebratory", "Solemn", "Reverent", "Irreverent",
            "Quirky", "Eccentric", "Conventional", "Traditional", "Modern", "Futuristic",
            "Retro", "Vintage", "Classic", "Timeless", "Ephemeral", "Fleeting", "Enduring",
            "Empowering", "Motivational", "Inspiring", "Depressing", "Uplifting", "Soothing"
        ]
        
        # Instrumental terms
        instrumental_terms = [
            "Guitar", "Piano", "Violin", "Cello", "Drums", "Bass", "Saxophone", "Trumpet",
            "Flute", "Clarinet", "Harp", "Ukulele", "Banjo", "Mandolin", "Accordion", 
            "Synthesizer", "Keyboard", "Organ", "Harmonica", "Bagpipes", "Sitar", "Tabla",
            "Santoor", "Sarod", "Veena", "Sarangi", "Bansuri", "Shehnai", "Mridangam",
            "Djembe", "Congas", "Bongos", "Marimba", "Xylophone", "Vibraphone", "Theremin",
            "Orchestral", "Symphonic", "Chamber", "String Quartet", "Brass Band", "Big Band",
            "Acoustic", "Electric", "Electronic", "Digital", "Analog", "Instrumental", "Vocal",
            "A Cappella", "Choral", "Operatic", "Falsetto", "Baritone", "Soprano", "Tenor",
            "Guitar-driven", "Piano-led", "Drum-heavy", "Bass-heavy", "String-laden", "Brass-heavy"
        ]
        
        # Era/time period terms
        era_terms = [
            "50s", "60s", "70s", "80s", "90s", "2000s", "2010s", "2020s",
            "Vintage", "Retro", "Classic", "Modern", "Contemporary", "Futuristic",
            "Old School", "New School", "Golden Age", "Renaissance", "Baroque", "Classical",
            "Romantic", "Medieval", "Ancient", "Traditional", "Progressive", "Avant-garde",
            "Underground", "Mainstream", "Alternative", "Independent", "Commercial", "Indie"
        ]
        
        # Location/setting terms
        location_terms = [
            "Beach", "Mountain", "Forest", "Desert", "Urban", "City", "Rural", "Countryside",
            "Ocean", "Sea", "Lake", "River", "Waterfall", "Island", "Coastal", "Tropical",
            "Arctic", "Snowy", "Rainy", "Sunny", "Cloudy", "Foggy", "Misty", "Stormy",
            "Dawn", "Dusk", "Sunrise", "Sunset", "Daytime", "Nighttime", "Midnight", "Noon",
            "Spring", "Summer", "Autumn", "Fall", "Winter", "Seasonal", "Holiday", "Festival",
            "Party", "Club", "Concert", "Stadium", "Arena", "Theater", "Cinema", "Cafe",
            "Restaurant", "Bar", "Pub", "Home", "Road", "Highway", "Street", "Alley",
            "Park", "Garden", "Meadow", "Field", "Farm", "Village", "Town", "Metropolis",
            "Suburban", "Industrial", "Post-industrial", "Futuristic", "Dystopian", "Utopian",
            "India", "Rajasthan", "Jaipur", "Delhi", "Mumbai", "Goa", "Kerala", "Himalayas"
        ]
        
        # Extract keywords from the Gemini response
        keywords = []
        
        # Look for "Music Keywords:" section in the description
        if "**Music Keywords:**" in description:
            # Extract the keywords after "Music Keywords:"
            keyword_section = description.split("**Music Keywords:**")[1].strip()
            
            # Extract until the next section or end of text
            if "**" in keyword_section:
                keyword_section = keyword_section.split("**")[0].strip()
            
            # Split by commas and clean up
            raw_keywords = [k.strip() for k in keyword_section.split(',')]
            
            # Remove quotes and clean up each keyword
            keywords = [k.replace('"', '').replace('"', '').replace('"', '').strip() for k in raw_keywords if k.strip()]
        
        # If we found keywords in the expected format, return them
        if keywords:
            # Return both the list of keywords and the first keyword as primary
            return keywords, keywords[0]
        
        # Extract Instagram caption if available (for possible keyword extraction)
        instagram_caption = ""
        if "**Instagram Caption:**" in description:
            caption_section = description.split("**Instagram Caption:**")[1].strip()
            instagram_caption = caption_section.split("**")[0].strip() if "**" in caption_section else caption_section
        
        # Look for terms in the description and caption
        found_terms = []
        
        # Convert description to lowercase for case-insensitive matching
        desc_lower = description.lower() + " " + instagram_caption.lower()
        
        # Check for genre terms
        for term in genre_terms:
            if term.lower() in desc_lower:
                found_terms.append(term)
        
        # Check for mood terms
        for term in mood_terms:
            if term.lower() in desc_lower:
                found_terms.append(term)
        
        # Check for instrumental terms
        for term in instrumental_terms:
            if term.lower() in desc_lower:
                found_terms.append(term)
        
        # Check for era terms
        for term in era_terms:
            if term.lower() in desc_lower:
                found_terms.append(term)
        
        # Check for location terms
        for term in location_terms:
            if term.lower() in desc_lower:
                found_terms.append(term)
        
        # If we found terms, create meaningful search queries
        if found_terms:
            # Deduplicate and limit to most relevant terms
            unique_terms = list(set(found_terms))
            
            # Prioritize by term type (genre > mood > instrumental > era > location)
            genre_matches = [term for term in unique_terms if term.lower() in [g.lower() for g in genre_terms]]
            mood_matches = [term for term in unique_terms if term.lower() in [m.lower() for m in mood_terms]]
            instrumental_matches = [term for term in unique_terms if term.lower() in [i.lower() for i in instrumental_terms]]
            era_matches = [term for term in unique_terms if term.lower() in [e.lower() for e in era_terms]]
            location_matches = [term for term in unique_terms if term.lower() in [l.lower() for l in location_terms]]
            
            # Create diverse keyword combinations
            keywords = []
            
            # Add genre-based keywords
            if genre_matches:
                for genre in genre_matches[:2]:  # Limit to top 2 genres
                    keywords.append(f"{genre} music")
                    
                    # Combine with mood if available
                    if mood_matches:
                        keywords.append(f"{mood_matches[0]} {genre}")
                    
                    # Combine with instrumental if available
                    if instrumental_matches:
                        keywords.append(f"{instrumental_matches[0]} {genre}")
            
            # Add mood-based keywords
            if mood_matches:
                for mood in mood_matches[:2]:  # Limit to top 2 moods
                    keywords.append(f"{mood} music")
            
            # Add location-based keywords
            if location_matches:
                for location in location_matches[:2]:  # Limit to top 2 locations
                    keywords.append(f"{location} music")
                    
                    # Combine with genre if available
                    if genre_matches:
                        keywords.append(f"{location} {genre_matches[0]}")
            
            # Add era-based keywords
            if era_matches:
                for era in era_matches[:1]:  # Limit to top era
                    keywords.append(f"{era} music")
                    
                    # Combine with genre if available
                    if genre_matches:
                        keywords.append(f"{era} {genre_matches[0]}")
            
            # Add instrumental-based keywords
            if instrumental_matches:
                for instrument in instrumental_matches[:1]:  # Limit to top instrument
                    keywords.append(f"{instrument} music")
            
            # Return both the list of keywords and the first keyword as primary
            return keywords, keywords[0]
        
        # If no specific terms found, extract nouns and adjectives as a fallback
        words = description.split()
        # Simple heuristic: words longer than 5 characters might be meaningful
        meaningful_words = [word for word in words if len(word) > 5 and word.isalpha()]
        
        if meaningful_words:
            # Use the most frequent meaningful words
            from collections import Counter
            word_counts = Counter(meaningful_words)
            top_words = [word for word, _ in word_counts.most_common(3)]
            
            # Create keywords from top words
            keywords = [f"{word} music" for word in top_words]
            
            # Return both the list of keywords and the first keyword as primary
            return keywords, keywords[0]
            
        # Ultimate fallback: use generic terms
        return ["Popular music", "Trending songs", "Recommended tracks"], "Popular music"
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return ["music", "popular", "recommended"], "music"

def analyze_image_attributes(image_data):
    """
    Analyze an image to extract scene type, mood, emotion, and dominant color.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        tuple: (scene, mood, emotion, dominant_color)
    """
    try:
        # Use gemini-1.5-flash model
        gemini = GenerativeModel("gemini-1.5-flash")
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Create a prompt for image attribute analysis
        prompt = """
        Analyze this image and provide ONLY the following attributes in JSON format:
        
        1. Scene: What type of scene or setting is depicted (e.g., beach, urban, forest, indoor, concert, etc.)
        2. Mood: The overall mood of the image (e.g., peaceful, energetic, romantic, mysterious, etc.)
        3. Emotion: The primary emotion evoked by the image (e.g., joy, nostalgia, wonder, melancholy, etc.)
        4. Dominant Color: The most prominent color in the image (use common color names)
        
        Format your response EXACTLY as follows (JSON format only, no additional text):
        {
            "scene": "your scene analysis",
            "mood": "your mood analysis",
            "emotion": "your emotion analysis",
            "dominant_color": "your color analysis"
        }
        """
        
        # Generate content
        response = gemini.generate_content([prompt, image])
        response_text = response.text.strip()
        
        # Extract JSON from response (handle cases where model might add extra text)
        import json
        import re
        
        # Try to find JSON pattern in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        try:
            # Parse the JSON response
            attributes = json.loads(response_text)
            
            # Extract the attributes
            scene = attributes.get('scene', 'Unknown')
            mood = attributes.get('mood', 'Neutral')
            emotion = attributes.get('emotion', 'Neutral')
            dominant_color = attributes.get('dominant_color', 'Unknown')
            
            return scene, mood, emotion, dominant_color
            
        except json.JSONDecodeError:
            # Fallback to simple extraction if JSON parsing fails
            lines = response_text.split('\n')
            scene = next((line.split(':')[1].strip() for line in lines if 'scene' in line.lower()), 'Unknown')
            mood = next((line.split(':')[1].strip() for line in lines if 'mood' in line.lower()), 'Neutral')
            emotion = next((line.split(':')[1].strip() for line in lines if 'emotion' in line.lower()), 'Neutral')
            dominant_color = next((line.split(':')[1].strip() for line in lines if 'color' in line.lower()), 'Unknown')
            
            return scene, mood, emotion, dominant_color
            
    except Exception as e:
        print(f"Error analyzing image attributes: {e}")
        return "Unknown", "Neutral", "Neutral", "Unknown"

def search_spotify_tracks(keywords, limit=10):
    """
    Search for tracks on Spotify based on keywords.
    Returns formatted track strings and structured track data.
    """
    if not keywords:
        return [], []
    
    all_tracks = []
    formatted_tracks = []
    
    # Strategy 1: Search for each keyword individually
    for keyword in keywords:
        try:
            # Search Spotify for tracks
            results = sp.search(q=keyword, limit=limit, type='track')
            tracks = results['tracks']['items']
            
            # Process each track
            for track in tracks:
                # Skip if we already have this track
                if any(t.get('id') == track['id'] for t in all_tracks):
                    continue
                
                # Format track information
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url'],
                    'spotify_url': track['external_urls']['spotify'],
                    'popularity': track['popularity'],
                    'match_type': keyword
                }
                
                # Add to our lists
                all_tracks.append(track_info)
                
                # Create a formatted string for display
                track_string = f"{track['name']} by {track_info['artist']} (Keyword: {keyword})"
                formatted_tracks.append(track_string)
        
        except Exception as e:
            print(f"Error searching for tracks with keyword '{keyword}': {str(e)}")
    
    # Strategy 2: If we don't have enough tracks, try a combined search
    if len(all_tracks) < 5 and len(keywords) > 1:
        try:
            combined_query = ' '.join(keywords[:3])  # Use first 3 keywords at most
            results = sp.search(q=combined_query, limit=limit, type='track')
            tracks = results['tracks']['items']
            
            for track in tracks:
                # Skip if we already have this track
                if any(t.get('id') == track['id'] for t in all_tracks):
                    continue
                
                # Format track information
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url'],
                    'spotify_url': track['external_urls']['spotify'],
                    'popularity': track['popularity'],
                    'match_type': 'Combined'
                }
                
                # Add to our lists
                all_tracks.append(track_info)
                
                # Create a formatted string for display
                track_string = f"{track['name']} by {track_info['artist']} (Combined keywords)"
                formatted_tracks.append(track_string)
        
        except Exception as e:
            print(f"Error searching for tracks with combined keywords: {str(e)}")
    
    # Limit the number of tracks to return
    max_tracks = min(10, len(all_tracks))
    
    return formatted_tracks[:max_tracks], all_tracks[:max_tracks]

# Spotify API credentials
client_id = "af052d02571c4335bcce9dce3d755c7e"
client_secret = "d46b38860c86452280e8e653209e1298"

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Example usage (commented out for import)
"""
# Main Flow
uploaded = files.upload()
image_path = list(uploaded.keys())[0]
with open(image_path, "rb") as f:
    image_data = f.read()

description = describe_image(image_data)
print(f" Image Description: {description}")

# Extract keyword from description
keyword = extract_keyword_from_description(description)
print(f" Suggested Keyword for Spotify: {keyword}")

# Spotify Search
track_strings, _ = search_spotify_tracks(keyword)
if track_strings:
    print("\n Recommended Songs:")
    for song in track_strings:
        print(song)
else:
    print(" No relevant songs found. Try a different image.")
"""
