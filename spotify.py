import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from PIL import Image
import io
import base64
import random
import re

# Set environment variables (replace with your actual values)
SPOTIFY_CLIENT_ID = "af052d02571c4335bcce9dce3d755c7e"
SPOTIFY_CLIENT_SECRET = "d46b38860c86452280e8e653209e1298"

def get_spotify_malayalam_songs(analysis_json):
    """
    Fetches Spotify Malayalam song recommendations based on the provided JSON analysis.
    Prioritizes trending Malayalam songs that match the mood and characteristics.

    Args:
        analysis_json (dict): A dictionary containing the JSON analysis of an image.

    Returns:
        list: A list of tuples, where each tuple contains the song name, artist, Spotify link, and album.
              Returns an empty list if no songs are found.
    """

    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Extract relevant information from the analysis JSON
        mood = analysis_json['music_recommendations']['primary_matches'][0]['mood']
        key_characteristics = analysis_json['music_recommendations']['primary_matches'][0]['key_characteristics']
        tempo_range_str = analysis_json['music_recommendations']['primary_matches'][0]['tempo_range']
        
        # Extract primary emotion for better matching
        primary_emotion = analysis_json['emotional_mapping']['primary']['emotion']
        
        # Map emotions and moods to Malayalam music relevant terms
        emotion_mood_mapping = {
            "Serenity": ["melancholic", "romantic", "peaceful"],
            "Calmness": ["soothing", "melodious", "peaceful"],
            "Joy": ["upbeat", "celebration", "festive"],
            "Excitement": ["energetic", "dance", "upbeat"],
            "Nostalgia": ["classic", "retro", "old"],
            "Contentment": ["melodious", "soothing"],
            "Reflection": ["thoughtful", "philosophical"],
            "Serene": ["peaceful", "romantic", "melodious"],
            "Reflective": ["thoughtful", "introspective"],
            "Contemplative": ["philosophical", "deep"]
        }
        
        # Get mapped terms for both mood and emotion
        mood_terms = emotion_mood_mapping.get(mood, [mood.lower()])
        emotion_terms = emotion_mood_mapping.get(primary_emotion, [primary_emotion.lower()])
        
        # Combine all terms
        all_terms = mood_terms + emotion_terms
        
        # Try to extract a tempo value from the tempo range string
        try:
            tempo_min, tempo_max = map(int, re.findall(r'\d+', tempo_range_str))
            tempo_avg = (tempo_min + tempo_max) / 2
        except (ValueError, IndexError):
            tempo_avg = None
            
        # Build search queries - we'll perform multiple searches to increase diversity
        search_queries = []
        
        # Base Malayalam search with mood
        malayalam_terms = ["Malayalam", "Malayali", "Malayalam songs", "Malayalam music"]
        
        # Mix up different search combinations for better results
        for base_term in malayalam_terms:
            # Add mood-based searches
            for term in all_terms:
                search_queries.append(f"{base_term} {term}")
            
            # Add specific artist searches for popular Malayalam artists
            malayalam_artists = ["KS Chithra", "Yesudas", "Shreya Ghoshal Malayalam", 
                                "Vidhu Prathap", "Sujatha", "Vineeth Sreenivasan", 
                                "Prithviraj", "Unni Menon", "Haricharan Malayalam"]
            
            for artist in malayalam_artists:
                for term in all_terms[:2]:  # Use first two mood terms for each artist
                    search_queries.append(f"{artist} {term}")
        
        # Add film-specific searches for recent popular Malayalam films
        recent_films = ["Manjummel Boys", "Premalu", "Bramayugam", "Aadujeevitham", 
                       "Guruvayoor Ambalanadayil", "Aavesham", "Ullozhukku"]
        
        for film in recent_films:
            search_queries.append(f"{film} songs")
        
        # Will store all songs found
        all_songs = []
        
        # Perform searches with all our queries
        for query in search_queries[:15]:  # Limit to first 15 queries to avoid rate limits
            results = sp.search(q=query, type='track', limit=10)
            
            if results and results['tracks']['items']:
                for track in results['tracks']['items']:
                    # Check if song is likely Malayalam by checking artist and track name
                    artist_name = track['artists'][0]['name']
                    song_name = track['name']
                    
                    # Various ways to detect Malayalam content
                    is_malayalam = any([
                        "malayalam" in song_name.lower(),
                        "malayalam" in artist_name.lower(),
                        any(artist['name'] in malayalam_artists for artist in track['artists']),
                        any(film in song_name for film in recent_films),
                        # Last resort - rely on Spotify's search relevance
                    ])
                    
                    if is_malayalam or "malayalam" in query.lower():
                        # Format song info
                        formatted_name = track['name']
                        artist = track['artists'][0]['name']
                        link = track['external_urls']['spotify']
                        album = track['album']['name']
                        popularity = track['popularity']
                        release_date = track['album']['release_date']
                        
                        # Create a unique identifier to avoid duplicates
                        song_id = f"{formatted_name}|{artist}"
                        
                        # Check if this song is already in our list
                        if not any(song_id == f"{name}|{art}" for name, art, _, _, _, _ in all_songs):
                            all_songs.append((formatted_name, artist, link, album, popularity, release_date))
        
        # If we have songs, sort by popularity and recency
        if all_songs:
            # Sort by a combination of popularity and recency
            # This favors newer, popular songs (trending) over older popular songs
            sorted_songs = sorted(all_songs, 
                                 key=lambda x: (x[4] * 0.7 + (2025 - int(x[5][:4])) * -10), 
                                 reverse=True)
            
            # Format the final output (remove popularity and release_date)
            final_songs = [(name, artist, link, album) for name, artist, link, album, _, _ in sorted_songs]
            
            return final_songs[:10]  # Return top 10 trending Malayalam songs
        
        return []  # Return empty list if no songs are found

    except Exception as e:
        print(f"An error occurred in get_spotify_malayalam_songs: {e}")
        return []

def analyze_image_with_gemini(image_data):
    """
    Analyze the image using Google's Gemini API.
    This is a placeholder - you'll need to implement this with the actual Gemini API call.

    Args:
        image_data (bytes): Image data in bytes.

    Returns:
        dict: A dictionary representing the JSON analysis of the image.
    """
    # Placeholder - Replace with your actual Gemini API implementation
    print("Analyzing image with Gemini API...")
    
    # For now, we're returning the example JSON - replace this with your actual API call
    # You would need to:
    # 1. Convert image_data to the format required by Gemini API (likely base64)
    # 2. Construct and send the API request to Gemini
    # 3. Process the response and format it like the example_json_string
    
    return json.loads(example_json_string)

def display_recommendations(song_recommendations):
    """
    Display song recommendations in a more user-friendly format.
    
    Args:
        song_recommendations: List of tuples with song info
    """
    if not song_recommendations:
        return []
        
    return song_recommendations

# Example JSON (unchanged from your original)
example_json_string = """
{
    "color_analysis": {
        "dominant_colors": [
            {
                "hex": "#F0E68C",
                "name": "Khaki",
                "saturation": 20,
                "brightness": 94,
                "psychological_impact": "Calming, sophisticated, suggests stability and warmth."
            },
            {
                "hex": "#A9A9A9",
                "name": "DarkGray",
                "saturation": 0,
                "brightness": 66,
                "psychological_impact": "Neutral, balanced, creates a sense of calm and composure."
            },
            {
                "hex": "#D3D3D3",
                "name": "LightGray",
                "saturation": 0,
                "brightness": 83,
                "psychological_impact": "Clean, airy, can be associated with modernity and efficiency."
            }
        ],
        "harmony": {
            "type": "Monochromatic",
            "strength": 8,
            "complementary_elements": ["Neutral Tones", "Soft Highlights", "Balanced Contrast"]
        },
        "temperature": {
            "overall": "Neutral-Warm",
            "distribution": ["Background Warmth", "Foreground Coolness"],
            "contrast_ratio": 2.5
        },
        "transitions": {
            "gradient_patterns": ["Subtle Shading", "Soft Blending"],
            "smoothness": 7,
            "direction": "Horizontal"
        }
    },
    "emotional_mapping": {
        "primary": {
            "emotion": "Serenity",
            "intensity": 6,
            "confidence": 8
        },
        "secondary": [
            {
                "emotion": "Calmness",
                "intensity": 7,
                "relation": "Supports primary"
            },
            {
                "emotion": "Contentment",
                "intensity": 5,
                "relation": "Subordinate to primary"
            },
            {
                "emotion": "Reflection",
                "intensity": 4,
                "relation": "Adds depth to primary"
            }
        ],
        "complexity": {
            "score": 4,
            "factors": ["Subtle Nuance", "Gentle Atmosphere"],
            "progression": ["Static", "Contemplative"]
        },
        "engagement": {
            "predicted_level": 5,
            "key_drivers": ["Visual Appeal", "Relaxing Quality"],
            "attention_points": ["Soft Textures", "Balanced Composition"]
        }
    },
    "composition": {
        "structure": {
            "golden_ratio_elements": ["Background Horizon", "Main Subject Placement"],
            "symmetry_type": "Asymmetrical Balance",
            "balance_score": 7
        },
        "dynamics": {
            "movement_patterns": ["Gentle Sweep", "Subtle Flow"],
            "tension_points": ["Areas of Contrast", "Visual Anchor"],
            "flow_direction": "Horizontal"
        },
        "space_utilization": {
            "negative_space": 30,
            "density_map": ["Sparse Background", "Moderate Foreground"],
            "focus_areas": ["Central Subject", "Leading Lines"]
        }
    },
    "musical_correlation": {
        "tempo": {
            "suggested_bpm": 60,
            "range": "50-70",
            "variation_tolerance": 10
        },
        "genre_affinities": [
            {
                "genre": "Ambient",
                "confidence": 9,
                "matching_elements": ["Soft Textures", "Harmonic Simplicity"]
            },
            {
                "genre": "Lo-Fi",
                "confidence": 7,
                "matching_elements": ["Mellow Vibe", "Relaxed Tempo"]
            },
            {
                "genre": "Classical",
                "confidence": 6,
                "matching_elements": ["Gentle Melodies", "Harmonic Purity"]
            }
        ],
        "instrumental_suggestions": {
            "primary": ["Piano", "Strings"],
            "textures": ["Pads", "Reverb"],
            "production_style": "Minimalist"
        },
        "dynamic_requirements": {
            "range": "Quiet",
            "key_moments": ["Subtle Crescendos", "Gentle Decresendos"],
            "intensity_progression": ["Low", "Medium"]
        }
    },
    "contextual_optimization": {
        "platform_fit": {
            "instagram_story_score": 8,
            "optimal_duration": 15,
            "engagement_factors": ["Visual Storytelling", "Emotional Resonance"]
        },
        "demographic_alignment": {
            "primary_audience": "Young Adults",
            "age_range": "18-35",
            "cultural_contexts": ["Urban Lifestyle", "Relaxation Culture"]
        },
        "trend_relevance": {
            "current_trends": ["Mindfulness", "Self-Care"],
            "seasonality": "Autumn",
            "viral_potential": 6
        }
    },
    "music_recommendations": {
        "primary_matches": [
            {
                "genre": "Ambient",
                "style": "Chillout",
                "mood": "Serene",
                "tempo_range": "55-65 bpm",
                "key_characteristics": ["Soft Pads", "Ethereal Vocals"],
                "match_confidence": 9
            },
            {
                "genre": "Lo-Fi",
                "style": "Bedroom Pop",
                "mood": "Reflective",
                "tempo_range": "60-70 bpm",
                "key_characteristics": ["Mellow Beats", "Dreamy Synth"],
                "match_confidence": 8
            },
             {
                "genre": "Classical",
                "style": "Modern Classical",
                "mood": "Contemplative",
                "tempo_range": "50-60 bpm",
                "key_characteristics": ["Solo Piano", "String Ensemble"],
                "match_confidence": 7
            }
        ],
        "alternative_suggestions": [
            {
                "genre": "Electronic",
                "style": "Downtempo",
                "contrast_reason": "Adds a subtle energy lift",
                "match_confidence": 6
            },
            {
                "genre": "Folk",
                "style": "Acoustic",
                "contrast_reason": "Offers organic warmth",
                "match_confidence": 5
            }
        ]
    }
}
"""

# Main execution block
if __name__ == "__main__":
    print("This module is designed to be imported, not run directly.")