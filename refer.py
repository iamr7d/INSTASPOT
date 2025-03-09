import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from PIL import Image
import io
import base64
from google.colab import files
import google.generativeai as genai
import random
import re
from datetime import datetime
import requests

# Set environment variables (replace with your actual values)
SPOTIFY_CLIENT_ID = "af052d02571c4335bcce9dce3d755c7e"
SPOTIFY_CLIENT_SECRET = "d46b38860c86452280e8e653209e1298"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual Gemini API key

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def image_to_base64(image_data):
    """Convert image data to base64 string"""
    return base64.b64encode(image_data).decode('utf-8')

def analyze_image_with_gemini(image_data):
    """
    Analyze the image using Google's Gemini API to understand content and emotions.

    Args:
        image_data (bytes): Image data in bytes.

    Returns:
        dict: A dictionary with the Gemini analysis and music recommendations.
    """
    try:
        # Convert image to base64 for Gemini API
        base64_image = image_to_base64(image_data)

        # Initialize Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-pro-vision')

        # Create the prompt for Gemini
        prompt = """
        Analyze this image in detail and provide the following information in JSON format:

        1. Describe what's in the image (people, objects, setting, activities)
        2. Identify the dominant emotions and mood conveyed by the image
        3. Analyze the visual aesthetics (colors, lighting, composition)
        4. Based on the image, recommend appropriate music characteristics:
           - Specific genres that would pair well with this image
           - Mood of music that would complement this image
           - Tempo/pace of music that would fit (slow, medium, fast, with BPM range)
           - Any specific instruments or sounds that would pair well
           - Cultural context if applicable (especially Malayalam music context)

        Format your response as a valid JSON object with these keys:
        {
          "image_content": { detailed description of visual elements },
          "emotional_analysis": { emotions and mood analysis },
          "visual_aesthetics": { color and composition analysis },
          "music_recommendations": { detailed music suggestions }
        }

        For the music recommendations, specifically consider Malayalam music options if appropriate for the image.
        """

        # Send request to Gemini
        response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': base64_image}])

        # Extract JSON from response
        response_text = response.text

        # Find JSON content in the response (handle potential text before/after JSON)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text  # Use whole response as fallback

        # Parse the JSON
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError:
            # If direct parsing fails, try to clean the string
            cleaned_json_str = re.sub(r'[^\x00-\x7F]+', '', json_str)  # Remove non-ASCII chars
            analysis = json.loads(cleaned_json_str)

        print("✅ Gemini analysis complete!")
        return analysis

    except Exception as e:
        print(f"❌ Error in Gemini analysis: {e}")
        # Return a basic structure as fallback
        return {
            "image_content": {"description": "Unable to analyze image content"},
            "emotional_analysis": {"dominant_emotion": "neutral", "mood": "neutral"},
            "visual_aesthetics": {"colors": ["unknown"], "composition": "unknown"},
            "music_recommendations": {
                "genres": ["Malayalam", "Pop"],
                "mood": "neutral",
                "tempo": "medium",
                "instruments": ["vocals", "guitar"],
                "cultural_context": "general"
            }
        }

def ask_gemini_for_song_suggestions(analysis):
    """
    Ask Gemini for specific Malayalam song suggestions based on the image analysis.

    Args:
        analysis (dict): The image analysis from analyze_image_with_gemini

    Returns:
        dict: Enhanced analysis with specific song suggestions
    """
    try:
        # Create a prompt with the analysis for more specific song suggestions
        prompt = f"""
        Based on the following image analysis, suggest 5-7 specific Malayalam songs that would perfectly match the image for an Instagram story:

        IMAGE CONTENT: {analysis.get('image_content', {})}

        EMOTIONAL MOOD: {analysis.get('emotional_analysis', {})}

        VISUAL AESTHETICS: {analysis.get('visual_aesthetics', {})}

        MUSIC RECOMMENDATIONS: {analysis.get('music_recommendations', {})}

        For each song, provide:
        1. Song title
        2. Artist/singer name
        3. Movie/album name (if applicable)
        4. Year of release (approximate is fine)
        5. Brief explanation of why this song matches the image

        Focus on a mix of trending recent Malayalam songs and classics that fit the mood.
        Include songs from recent Malayalam movies if they match the mood.

        Format your response as a valid JSON object with this structure:
        {
          "suggested_songs": [
            {
              "title": "Song name",
              "artist": "Artist name",
              "movie": "Movie name",
              "year": "Year",
              "match_reason": "Why this matches"
            },
            ...
          ]
        }
        """

        # Initialize Gemini model (text-only is fine here)
        model = genai.GenerativeModel('gemini-pro')

        # Send request to Gemini
        response = model.generate_content(prompt)

        # Extract JSON from response
        response_text = response.text

        # Find JSON content in the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text

        # Parse the JSON
        try:
            song_suggestions = json.loads(json_str)
        except json.JSONDecodeError:
            # If direct parsing fails, try to clean the string
            cleaned_json_str = re.sub(r'[^\x00-\x7F]+', '', json_str)  # Remove non-ASCII chars
            song_suggestions = json.loads(cleaned_json_str)

        # Add these suggestions to our analysis
        analysis['gemini_song_suggestions'] = song_suggestions.get('suggested_songs', [])
        print("✅ Gemini song suggestions received!")

        return analysis

    except Exception as e:
        print(f"❌ Error getting Gemini song suggestions: {e}")
        analysis['gemini_song_suggestions'] = []
        return analysis

def get_spotify_malayalam_songs(analysis):
    """
    Fetches Spotify Malayalam song recommendations based on the Gemini analysis.
    Uses suggested songs from Gemini if available, otherwise searches based on mood.

    Args:
        analysis (dict): The complete image analysis including Gemini suggestions

    Returns:
        list: A list of tuples with song details
    """
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        all_songs = []

        # First try to find the specific songs suggested by Gemini
        gemini_suggestions = analysis.get('gemini_song_suggestions', [])

        if gemini_suggestions:
            print(f"🔍 Searching for {len(gemini_suggestions)} Gemini-suggested Malayalam songs...")

            for suggestion in gemini_suggestions:
                song_title = suggestion.get('title', '')
                artist = suggestion.get('artist', '')
                movie = suggestion.get('movie', '')

                # Create search query - try both specific and broader searches
                specific_query = f"track:{song_title} artist:{artist}"
                broader_query = f"{song_title} {artist} {movie} Malayalam"

                # Try specific search first
                specific_results = sp.search(q=specific_query, type='track', limit=3)

                if specific_results and specific_results['tracks']['items']:
                    track = specific_results['tracks']['items'][0]  # Take first match
                else:
                    # Try broader search
                    broader_results = sp.search(q=broader_query, type='track', limit=5)
                    if broader_results and broader_results['tracks']['items']:
                        # Find best match by comparing title similarity
                        best_match = None
                        highest_score = 0

                        for track in broader_results['tracks']['items']:
                            # Simple similarity score based on song title
                            title_words = set(song_title.lower().split())
                            track_words = set(track['name'].lower().split())
                            common_words = title_words.intersection(track_words)

                            if len(title_words) > 0:
                                similarity = len(common_words) / len(title_words)

                                if similarity > highest_score:
                                    highest_score = similarity
                                    best_match = track

                        if best_match and highest_score > 0.3:  # Threshold for match
                            track = best_match
                        else:
                            continue  # Skip if no good match
                    else:
                        continue  # Skip if no results at all

                # Extract track info
                formatted_name = track['name']
                artist_name = track['artists'][0]['name']
                link = track['external_urls']['spotify']
                album = track['album']['name']
                popularity = track['popularity']
                release_date = track['album']['release_date']

                # Add match reason from Gemini
                match_reason = suggestion.get('match_reason', '')

                # Create unique ID to avoid duplicates
                song_id = f"{formatted_name}|{artist_name}"

                if not any(song_id == f"{name}|{art}" for name, art, _, _, _, _, _ in all_songs):
                    all_songs.append((formatted_name, artist_name, link, album, popularity, release_date, match_reason))

        # If we didn't get enough songs from specific suggestions, add more based on mood
        if len(all_songs) < 7:
            print("🔍 Finding additional trending Malayalam songs based on mood...")

            # Extract mood and genre from analysis
            music_rec = analysis.get('music_recommendations', {})
            mood = music_rec.get('mood', 'neutral')

            if isinstance(mood, list) and len(mood) > 0:
                mood = mood[0]  # Take first mood if it's a list

            # Get genres, handling different possible structures
            genres = music_rec.get('genres', [])
            if not genres and 'genre' in music_rec:
                genres = [music_rec.get('genre')]

            if isinstance(genres, str):
                genres = [genres]

            # Ensure we have Malayalam as a focus
            if 'Malayalam' not in genres and 'malayalam' not in genres:
                genres.append('Malayalam')

            # Popular Malayalam artists to search
            malayalam_artists = ["KS Chithra", "Yesudas", "Shreya Ghoshal Malayalam",
                                "Vidhu Prathap", "Sujatha", "Vineeth Sreenivasan",
                                "Prithviraj", "Unni Menon", "Haricharan"]

            # Recent popular Malayalam films
            recent_films = ["Manjummel Boys", "Premalu", "Bramayugam", "Aadujeevitham",
                          "Guruvayoor Ambalanadayil", "Aavesham", "Ullozhukku",
                          "Turbo", "Maharaja"]

            # Build search queries
            search_queries = []

            # Mood-based searches
            search_queries.append(f"Malayalam {mood}")

            # Genre-based searches
            for genre in genres:
                search_queries.append(f"{genre} {mood}")

            # Artist-based searches
            for artist in malayalam_artists[:5]:  # Limit to first 5 artists
                search_queries.append(f"{artist} {mood}")

            # Film-based searches
            for film in recent_films[:5]:  # Limit to first 5 films
                search_queries.append(f"{film} songs")

            # Perform searches
            for query in search_queries[:10]:  # Limit to first 10 queries
                results = sp.search(q=query, type='track', limit=5)

                if results and results['tracks']['items']:
                    for track in results['tracks']['items']:
                        # Extract track info
                        formatted_name = track['name']
                        artist_name = track['artists'][0]['name']
                        link = track['external_urls']['spotify']
                        album = track['album']['name']
                        popularity = track['popularity']
                        release_date = track['album']['release_date']

                        # Generic match reason
                        match_reason = f"Matches the {mood} mood of your image"

                        # Create unique ID to avoid duplicates
                        song_id = f"{formatted_name}|{artist_name}"

                        if not any(song_id == f"{name}|{art}" for name, art, _, _, _, _, _ in all_songs):
                            all_songs.append((formatted_name, artist_name, link, album, popularity, release_date, match_reason))

        # Sort songs by popularity and recency
        if all_songs:
            # Calculate recency score (higher for newer songs)
            current_year = datetime.now().year

            # Sort by a weighted score of popularity and recency
            sorted_songs = sorted(all_songs,
                                key=lambda x: (
                                    x[4] * 0.7 +  # 70% weight on popularity
                                    (current_year - int(x[5][:4] if len(x[5]) >= 4 else 2000)) * -8  # Recency bonus
                                ),
                                reverse=True)

            # Format final output
            final_songs = [(name, artist, link, album, reason)
                          for name, artist, link, album, _, _, reason in sorted_songs]

            return final_songs[:10]  # Return top 10 songs

        return []  # Return empty list if no songs found

    except Exception as e:
        print(f"❌ Error in Spotify search: {e}")
        import traceback
        traceback.print_exc()
        return []

def describe_image(image_path):
    # Changed model to gemini-1.5-flash as gemini-pro-vision is deprecated
    gemini = genai.GenerativeModel("gemini-1.5-flash")  
    with open(image_path, "rb") as image_file:
        image_data = Image.open(io.BytesIO(image_file.read()))
    response = gemini.generate_content(["Describe this image briefly and suggest a related keyword for music search.", image_data])
    return response.text.strip()

def search_spotify_tracks(keyword):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=keyword, limit=5, type='track')
    tracks = results['tracks']['items']
    return [f"🎵 {track['name']} by {track['artists'][0]['name']}" for track in tracks]

def display_recommendations(song_recommendations, analysis):
    """
    Display song recommendations with image analysis context.

    Args:
        song_recommendations: List of tuples with song info
        analysis: The complete image analysis
    """
    if not song_recommendations:
        print("\n❌ No Malayalam songs found matching the image mood.")
        return

    # Extract image content and mood for context
    image_content = analysis.get('image_content', {}).get('description', 'your image')
    mood = analysis.get('emotional_analysis', {}).get('dominant_emotion', 'neutral')

    if isinstance(mood, list) and len(mood) > 0:
        mood = mood[0]

    print("\n" + "=" * 70)
    print("🎵  MALAYALAM SONG RECOMMENDATIONS FOR YOUR INSTAGRAM STORY  🎵")
    print("=" * 70)

    print(f"\n📷 IMAGE ANALYSIS:")
    print(f"Gemini detected: {image_content}")
    print(f"Dominant mood: {mood}")

    print("\n🎧 RECOMMENDED SONGS:")
    print("-" * 70)

    for i, (name, artist, link, album, reason) in enumerate(song_recommendations, 1):
        print(f"{i}. {name}")
        print(f"   👤 Artist: {artist}")
        print(f"   💿 Album: {album}")
        print(f"   🔍 Why it matches: {reason}")
        print(f"   🔗 Spotify: {link}")
        print("-" * 70)

    print("\n💡 TIP: These songs are trending in Malayalam music and match your image's mood!")
    print("📱 Simply click any link to preview before adding to your Instagram story.")
    print("=" * 70)

# Main execution block
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎵  MALAYALAM INSTAGRAM STORY SONG RECOMMENDER  🎵")
    print("Powered by Google Gemini AI + Spotify")
    print("=" * 70)
    print("\nUpload an image to get Malayalam song recommendations that match the mood!")
    print("Our AI will analyze your image and find perfect songs for your story.")

    # Image Upload Option (Colab)
    uploaded = files.upload()

    if uploaded:
        image_name = list(uploaded.keys())[0]
        image_data = uploaded[image_name]

        print(f"\n📷 Processing image: {image_name}")

        # STEP 1: Analyze image with Gemini
        print("🧠 Analyzing image with Google Gemini AI...")
        analysis = analyze_image_with_gemini(image_data)

        # STEP 2: Ask Gemini for specific song suggestions
        print("🎵 Asking Gemini for Malayalam song suggestions...")
        enhanced_analysis = ask_gemini_for_song_suggestions(analysis)

        # STEP 3: Describe image and suggest keyword
        print("🖼️ Describing image and suggesting keyword...")
        description = describe_image(image_name)
        print(f"🖼️ Image Description: {description}")

        # Extract keyword from description (mock logic)
        keyword = description.split()[-1]  # Example: Last word as keyword for simplicity
        print(f"🔍 Suggested Keyword for Spotify: {keyword}")

        # STEP 4: Search Spotify for the songs
        print("🔍 Searching Spotify for these songs...")
        malayalam_songs = search_spotify_tracks(keyword)

        # STEP 5: Display recommendations
        display_recommendations(malayalam_songs, enhanced_analysis)

    else:
        print("\n❌ No image uploaded. Please upload an image to get song recommendations.")