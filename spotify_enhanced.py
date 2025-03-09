import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
from datetime import datetime
import random

# Set environment variables (replace with your actual values)
SPOTIFY_CLIENT_ID = "af052d02571c4335bcce9dce3d755c7e"
SPOTIFY_CLIENT_SECRET = "d46b38860c86452280e8e653209e1298"

# Initialize Spotify client
def initialize_spotify_client():
    """
    Initialize and return a Spotify client using the client credentials flow.
    
    Returns:
        spotipy.Spotify: A configured Spotify client
    """
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        print(f"Error initializing Spotify client: {e}")
        return None

# Enhanced song recommendation function
def get_enhanced_songs(analysis_json):
    """
    Get enhanced song recommendations based on image analysis.
    
    Args:
        analysis_json (dict): Analysis JSON from Gemini
        
    Returns:
        list: Song recommendations
    """
    try:
        # Initialize Spotify client
        sp = initialize_spotify_client()
        if not sp:
            return get_fallback_songs()
        
        # Extract all relevant information from the analysis
        mood = analysis_json.get('mood', '')
        emotion = analysis_json.get('emotion', '')
        scene_type = analysis_json.get('scene_type', '')
        time_of_day = analysis_json.get('time_of_day', '')
        dominant_colors = analysis_json.get('dominant_colors', [])
        characteristics = analysis_json.get('characteristics', [])
        
        # Get additional context if available
        context = analysis_json.get('context', {})
        energy_level = context.get('energy_level', 'medium')
        tempo = context.get('tempo', 'moderate')
        genre_hints = context.get('genre_hints', [])
        
        print(f"Analysis - Mood: {mood}, Emotion: {emotion}, Scene: {scene_type}")
        print(f"Context - Energy: {energy_level}, Tempo: {tempo}, Genres: {genre_hints}")
        
        # Build search queries based on analysis
        search_queries = []
        
        # Add mood and emotion based queries
        if mood and emotion:
            search_queries.append(f"{mood} {emotion}")
        elif mood:
            search_queries.append(mood)
        elif emotion:
            search_queries.append(emotion)
        
        # Add scene type based queries
        if scene_type:
            search_queries.append(scene_type)
            # Combine scene with mood/emotion for more specific results
            if mood:
                search_queries.append(f"{scene_type} {mood}")
        
        # Add genre-based queries
        for genre in genre_hints[:3]:  # Use top 3 genre hints
            search_queries.append(genre)
            # Combine genre with mood for more specific results
            if mood:
                search_queries.append(f"{genre} {mood}")
        
        # Add tempo and energy based queries
        if tempo and energy_level:
            search_queries.append(f"{tempo} {energy_level}")
        
        # Add time of day based queries
        if time_of_day:
            search_queries.append(time_of_day)
            # Combine time with mood for more specific results
            if mood:
                search_queries.append(f"{time_of_day} {mood}")
        
        # Add characteristic based queries
        for characteristic in characteristics[:2]:
            search_queries.append(characteristic)
        
        # Ensure we have at least some search queries
        if not search_queries:
            search_queries = ['popular', 'trending', 'top hits']
        
        # Remove duplicates while preserving order
        search_queries = list(dict.fromkeys(search_queries))
        
        print(f"Search queries: {search_queries}")
        
        # Get recommendations
        recommendations = []
        seen_tracks = set()  # Track IDs we've already added
        
        # Try different search approaches with varying limits to ensure diversity
        for i, query in enumerate(search_queries):
            try:
                # Adjust limit based on query position to prioritize more relevant queries
                limit = 10 if i < 2 else 5
                
                # Search for tracks with the query
                results = sp.search(q=query, type='track', limit=limit)
                
                if results and 'tracks' in results and 'items' in results['tracks']:
                    for track in results['tracks']['items']:
                        # Skip if we've already added this track
                        if track['id'] in seen_tracks:
                            continue
                            
                        # Create song object
                        song = {
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                            'album': track['album']['name'] if 'album' in track else 'Unknown',
                            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'popularity': track['popularity'],
                            'release_date': track['album']['release_date'] if 'album' in track and 'release_date' in track['album'] else None,
                            'preview_url': track['preview_url'],
                            'spotify_url': track['external_urls']['spotify'] if 'external_urls' in track and 'spotify' in track['external_urls'] else None,
                            'match_type': get_match_type(query, mood, emotion, genre_hints),
                            'query': query  # Store the query that found this song for debugging
                        }
                        
                        # Add to recommendations and mark as seen
                        recommendations.append(song)
                        seen_tracks.add(track['id'])
                        
                        # Break early if we have enough recommendations
                        if len(recommendations) >= 30:
                            break
                            
                # Break early if we have enough recommendations
                if len(recommendations) >= 30:
                    break
                    
            except Exception as e:
                print(f"Error searching for term '{query}': {e}")
                continue
        
        # If we don't have enough recommendations, try seed-based recommendations
        if len(recommendations) < 10:
            try:
                # Get seed tracks from what we have so far
                seed_tracks = [r['id'] for r in recommendations[:5]]
                
                # Get seed genres from genre hints
                seed_genres = [g.replace(' ', '-').lower() for g in genre_hints[:5]]
                seed_genres = [g for g in seed_genres if len(g.split('-')) == 1]  # Spotify only accepts single-word genres
                
                # Set target attributes based on analysis
                target_attributes = {}
                
                # Set energy based on energy_level
                if energy_level == "high":
                    target_attributes['target_energy'] = 0.8
                elif energy_level == "low":
                    target_attributes['target_energy'] = 0.3
                
                # Set tempo based on tempo
                if tempo == "fast":
                    target_attributes['target_tempo'] = 120
                elif tempo == "slow":
                    target_attributes['target_tempo'] = 80
                
                # Set valence (happiness) based on mood
                if mood in ["happy", "excited", "energetic"]:
                    target_attributes['target_valence'] = 0.8
                elif mood in ["sad", "melancholy"]:
                    target_attributes['target_valence'] = 0.2
                
                # Get recommendations using seeds
                if seed_tracks or seed_genres:
                    rec_results = sp.recommendations(
                        seed_tracks=seed_tracks[:2],
                        seed_genres=seed_genres[:3],
                        limit=20,
                        **target_attributes
                    )
                    
                    if rec_results and 'tracks' in rec_results:
                        for track in rec_results['tracks']:
                            # Skip if we've already added this track
                            if track['id'] in seen_tracks:
                                continue
                                
                            # Create song object
                            song = {
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                                'album': track['album']['name'] if 'album' in track else 'Unknown',
                                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                                'popularity': track['popularity'],
                                'release_date': track['album']['release_date'] if 'album' in track and 'release_date' in track['album'] else None,
                                'preview_url': track['preview_url'],
                                'spotify_url': track['external_urls']['spotify'] if 'external_urls' in track and 'spotify' in track['external_urls'] else None,
                                'match_type': 'Recommended',
                                'query': 'seed_recommendation'
                            }
                            
                            # Add to recommendations and mark as seen
                            recommendations.append(song)
                            seen_tracks.add(track['id'])
            except Exception as e:
                print(f"Error getting seed-based recommendations: {e}")
        
        # If we still don't have recommendations, try a general search
        if not recommendations:
            try:
                results = sp.search(q='popular', type='track', limit=15)
                
                if results and 'tracks' in results and 'items' in results['tracks']:
                    for track in results['tracks']['items']:
                        # Create song object
                        song = {
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                            'album': track['album']['name'] if 'album' in track else 'Unknown',
                            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'popularity': track['popularity'],
                            'release_date': track['album']['release_date'] if 'album' in track and 'release_date' in track['album'] else None,
                            'preview_url': track['preview_url'],
                            'spotify_url': track['external_urls']['spotify'] if 'external_urls' in track and 'spotify' in track['external_urls'] else None,
                            'match_type': 'Popular',
                            'query': 'popular'
                        }
                        
                        recommendations.append(song)
            except Exception as e:
                print(f"Error getting general recommendations: {e}")
        
        # If we still don't have recommendations, return fallback
        if not recommendations:
            return get_fallback_songs()
        
        # Sort recommendations to prioritize diversity and relevance
        # First sort by popularity
        recommendations.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        
        # Then reorder to ensure diversity of match types in the top results
        if len(recommendations) > 10:
            # Group by match_type
            match_types = {}
            for rec in recommendations:
                match_type = rec.get('match_type', 'Other')
                if match_type not in match_types:
                    match_types[match_type] = []
                match_types[match_type].append(rec)
            
            # Create a new ordered list with diversity
            diverse_recommendations = []
            remaining = []
            
            # Take top items from each match type
            for match_type, recs in match_types.items():
                diverse_recommendations.extend(recs[:3])  # Take top 3 from each match type
                remaining.extend(recs[3:])  # Keep the rest for later
            
            # Sort remaining by popularity
            remaining.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
            # Combine lists
            recommendations = diverse_recommendations + remaining
        
        return recommendations[:15]  # Return top 15 songs
        
    except Exception as e:
        print(f"Error getting enhanced songs: {e}")
        return get_fallback_songs()

def get_match_type(query, mood, emotion, genre_hints):
    """Determine the match type for a song based on the query that found it"""
    if query == f"{mood} {emotion}":
        return f"{mood.capitalize()} {emotion.capitalize()}"
    elif query == mood:
        return f"{mood.capitalize()} Mood"
    elif query == emotion:
        return f"{emotion.capitalize()} Emotion"
    elif query in genre_hints:
        return f"{query.capitalize()} Genre"
    elif "tempo" in query or "energy" in query:
        return "Tempo Match"
    else:
        return "Scene Match"

# Fallback song recommendation function
def get_fallback_songs():
    """
    Get fallback song recommendations when the Spotify API fails
    
    Returns:
        list: Fallback song recommendations
    """
    # Hardcoded fallback songs
    fallback_songs = [
        {
            'id': '1',
            'name': 'Shape of You',
            'artist': 'Ed Sheeran',
            'album': '÷ (Divide)',
            'image': 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96',
            'popularity': 95,
            'release_date': '2017-03-03',
            'preview_url': 'https://p.scdn.co/mp3-preview/7339624dbd0f57833e0f58f7a995b95b5a522933',
            'spotify_url': 'https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3',
            'is_related': False
        },
        {
            'id': '2',
            'name': 'Blinding Lights',
            'artist': 'The Weeknd',
            'album': 'After Hours',
            'image': 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36',
            'popularity': 93,
            'release_date': '2020-03-20',
            'preview_url': 'https://p.scdn.co/mp3-preview/8b6e544b2f31f3b5533d2307e8a5e4f0bf2d95b8',
            'spotify_url': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b',
            'is_related': False
        },
        {
            'id': '3',
            'name': 'Dance Monkey',
            'artist': 'Tones and I',
            'album': 'The Kids Are Coming',
            'image': 'https://i.scdn.co/image/ab67616d0000b2739f39192eea82c38ffa2e2c33',
            'popularity': 91,
            'release_date': '2019-05-10',
            'preview_url': 'https://p.scdn.co/mp3-preview/5f3dab0b2a4e3d8d1a3e17c4a5d1af3b2c9b6a9e',
            'spotify_url': 'https://open.spotify.com/track/2XU0oxnq2qxCpomAAuJY8K',
            'is_related': False
        },
        {
            'id': '4',
            'name': 'Someone You Loved',
            'artist': 'Lewis Capaldi',
            'album': 'Divinely Uninspired To A Hellish Extent',
            'image': 'https://i.scdn.co/image/ab67616d0000b273fc2101e6889d6ce9025f85f2',
            'popularity': 90,
            'release_date': '2019-05-17',
            'preview_url': 'https://p.scdn.co/mp3-preview/6de1a3aa0f98b32c5c722a9e7d4e92f8f6b4c3c0',
            'spotify_url': 'https://open.spotify.com/track/7qEHsqek33rTcFNT9PFqLf',
            'is_related': False
        },
        {
            'id': '5',
            'name': 'Watermelon Sugar',
            'artist': 'Harry Styles',
            'album': 'Fine Line',
            'image': 'https://i.scdn.co/image/ab67616d0000b273d9194aa18fa4c9362b47464f',
            'popularity': 89,
            'release_date': '2019-12-13',
            'preview_url': 'https://p.scdn.co/mp3-preview/9de3a752af1c9a52a5d3267b843c48983f2b7cd6',
            'spotify_url': 'https://open.spotify.com/track/6UelLqGlWMcVH1E5c4H7lY',
            'is_related': False
        }
    ]
    
    return fallback_songs

# Function to get song preview URLs
def get_song_previews(song_recommendations):
    """
    Get preview URLs for the recommended songs.
    
    Args:
        song_recommendations (list): List of song recommendations
        
    Returns:
        list: Updated list with preview URLs
    """
    try:
        sp = initialize_spotify_client()
        if not sp:
            return song_recommendations
            
        enhanced_recommendations = []
        
        for rec in song_recommendations:
            # Extract Spotify track ID from the link
            track_id = rec['spotify_url'].split('/')[-1]
            
            # Get track details including preview URL
            track_info = sp.track(track_id)
            preview_url = track_info.get('preview_url', None)
            
            # Get album image
            album_image = None
            if track_info['album']['images']:
                album_image = track_info['album']['images'][0]['url']
                
            # Add to enhanced recommendations
            enhanced_recommendations.append({
                'name': rec['name'],
                'artist': rec['artist'],
                'link': rec['spotify_url'],
                'album': rec['album'],
                'popularity': rec['popularity'],
                'release_date': rec['release_date'],
                'preview_url': preview_url,
                'album_image': album_image
            })
            
        return enhanced_recommendations
        
    except Exception as e:
        print(f"Error getting song previews: {e}")
        return song_recommendations

# Format recommendations for the web app
def format_recommendations_for_web(recommendations):
    """
    Format song recommendations for the web application.
    
    Args:
        recommendations (list): List of song recommendations
        
    Returns:
        list: Formatted recommendations as dictionaries
    """
    formatted = []
    
    for rec in recommendations:
        if len(rec) >= 8:  # Enhanced format with preview and image
            name, artist, link, album, popularity, release_date, preview_url, album_image = rec
            formatted.append({
                'name': name,
                'artist': artist,
                'link': link,
                'album': album,
                'popularity': popularity,
                'release_date': release_date,
                'preview_url': preview_url,
                'album_image': album_image
            })
        elif len(rec) >= 6:  # Basic format with popularity and release date
            name, artist, link, album, popularity, release_date = rec
            formatted.append({
                'name': name,
                'artist': artist,
                'link': link,
                'album': album,
                'popularity': popularity,
                'release_date': release_date,
                'preview_url': None,
                'album_image': None
            })
        else:  # Minimal format
            name, artist, link, album = rec
            formatted.append({
                'name': name,
                'artist': artist,
                'link': link,
                'album': album,
                'popularity': 50,  # Default popularity
                'release_date': '2025',  # Default current year
                'preview_url': None,
                'album_image': None
            })
    
    return formatted

# Function to get enhanced Malayalam songs based on image analysis
def get_enhanced_malayalam_songs(analysis_json):
    """
    Get enhanced Malayalam song recommendations based on image analysis.
    
    Args:
        analysis_json (dict): Analysis JSON from Gemini
        
    Returns:
        list: Song recommendations
    """
    try:
        # Initialize Spotify client
        sp = initialize_spotify_client()
        if not sp:
            return get_fallback_malayalam_songs()
        
        # Extract all relevant information from the analysis
        mood = analysis_json.get('mood', '')
        emotion = analysis_json.get('emotion', '')
        scene_type = analysis_json.get('scene_type', '')
        time_of_day = analysis_json.get('time_of_day', '')
        
        # Get additional context if available
        context = analysis_json.get('context', {})
        energy_level = context.get('energy_level', 'medium')
        tempo = context.get('tempo', 'moderate')
        
        print(f"Malayalam Analysis - Mood: {mood}, Emotion: {emotion}, Scene: {scene_type}")
        
        # Build search queries based on analysis
        search_queries = []
        
        # Add Malayalam-specific mood and emotion based queries
        if mood and emotion:
            search_queries.append(f"Malayalam {mood} {emotion}")
        elif mood:
            search_queries.append(f"Malayalam {mood}")
        elif emotion:
            search_queries.append(f"Malayalam {emotion}")
        
        # Add Malayalam artists based on mood
        if mood in ["happy", "energetic", "excited"]:
            artists = ["Vidhu Prathap", "Vineeth Sreenivasan", "Najim Arshad", "KS Harisankar"]
        elif mood in ["sad", "melancholy"]:
            artists = ["KS Chithra", "KJ Yesudas", "Sithara Krishnakumar", "Shreya Ghoshal"]
        elif mood in ["romantic", "nostalgic"]:
            artists = ["Haricharan", "Karthik", "Shweta Mohan", "Manjari"]
        elif mood in ["calm", "peaceful"]:
            artists = ["Madhu Balakrishnan", "Swetha Mohan", "Unni Menon", "Venugopal"]
        else:
            artists = ["KS Chithra", "KJ Yesudas", "Vineeth Sreenivasan", "Vidhu Prathap"]
        
        # Add artist-based queries
        for artist in artists:
            search_queries.append(f"{artist} Malayalam")
        
        # Add popular Malayalam movie music directors
        directors = ["AR Rahman", "Vidyasagar", "M Jayachandran", "Gopi Sundar", "Bijibal", "Sushin Shyam"]
        for director in directors[:2]:  # Use top 2
            search_queries.append(f"{director} Malayalam {mood}")
        
        # Add scene-specific queries
        if scene_type:
            search_queries.append(f"Malayalam {scene_type}")
        
        # Add time of day specific queries
        if time_of_day:
            search_queries.append(f"Malayalam {time_of_day}")
        
        # Add specific Malayalam genres based on mood/scene
        if mood in ["happy", "energetic", "excited"]:
            search_queries.append("Malayalam pop")
            search_queries.append("Malayalam dance")
        elif mood in ["romantic", "nostalgic"]:
            search_queries.append("Malayalam romantic")
            search_queries.append("Malayalam melody")
        elif mood in ["sad", "melancholy"]:
            search_queries.append("Malayalam melody")
            search_queries.append("Malayalam sad")
        elif scene_type in ["nature", "beach", "mountains"]:
            search_queries.append("Malayalam folk")
            search_queries.append("Malayalam traditional")
        
        # Always add some general Malayalam music queries
        search_queries.extend(["Malayalam songs", "Malayalam hits", "Malayalam trending"])
        
        # Remove duplicates while preserving order
        search_queries = list(dict.fromkeys(search_queries))
        
        print(f"Malayalam search queries: {search_queries}")
        
        # Get recommendations
        recommendations = []
        seen_tracks = set()  # Track IDs we've already added
        
        # Try different search approaches
        for i, query in enumerate(search_queries):
            try:
                # Adjust limit based on query position
                limit = 8 if i < 3 else 5
                
                # Search for tracks with the query
                results = sp.search(q=query, type='track', limit=limit)
                
                if results and 'tracks' in results and 'items' in results['tracks']:
                    for track in results['tracks']['items']:
                        # Skip if we've already added this track
                        if track['id'] in seen_tracks:
                            continue
                            
                        # Check if it's likely a Malayalam song (by artist or track name)
                        is_malayalam = False
                        
                        # Check artist names for common Malayalam artist names
                        artist_name = track['artists'][0]['name'] if track['artists'] else ''
                        malayalam_artists = ["KS Chithra", "KJ Yesudas", "Vineeth Sreenivasan", "Vidhu Prathap", 
                                           "Najim Arshad", "Sithara", "Shreya Ghoshal", "Haricharan", "Karthik", 
                                           "Shweta Mohan", "Manjari", "Madhu Balakrishnan", "Swetha Mohan", 
                                           "Unni Menon", "Venugopal", "Pradeep Somasundaran", "Shankar Mahadevan"]
                        
                        # Check for partial matches in artist name
                        for mal_artist in malayalam_artists:
                            if mal_artist.lower() in artist_name.lower():
                                is_malayalam = True
                                break
                        
                        # Check album and track name for Malayalam indicators
                        if not is_malayalam:
                            track_name = track['name'].lower()
                            album_name = track['album']['name'].lower() if 'album' in track else ''
                            
                            malayalam_indicators = ["malayalam", "malayali", "mallu", "kerala", "mollywood"]
                            for indicator in malayalam_indicators:
                                if (indicator in track_name or indicator in album_name or 
                                    indicator in artist_name.lower()):
                                    is_malayalam = True
                                    break
                        
                        # If it's a Malayalam song, add it to recommendations
                        if is_malayalam or "malayalam" in query.lower():
                            # Create song object
                            song = {
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                                'album': track['album']['name'] if 'album' in track else 'Unknown',
                                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                                'popularity': track['popularity'],
                                'release_date': track['album']['release_date'] if 'album' in track and 'release_date' in track['album'] else None,
                                'preview_url': track['preview_url'],
                                'spotify_url': track['external_urls']['spotify'] if 'external_urls' in track and 'spotify' in track['external_urls'] else None,
                                'match_type': 'Malayalam ' + get_match_type(query, mood, emotion, []),
                                'query': query
                            }
                            
                            # Add to recommendations and mark as seen
                            recommendations.append(song)
                            seen_tracks.add(track['id'])
                            
                            # Break early if we have enough recommendations
                            if len(recommendations) >= 20:
                                break
                
                # Break early if we have enough recommendations
                if len(recommendations) >= 20:
                    break
                    
            except Exception as e:
                print(f"Error searching for Malayalam term '{query}': {e}")
                continue
        
        # If we don't have enough recommendations, try a general Malayalam search
        if len(recommendations) < 5:
            try:
                results = sp.search(q='Malayalam popular', type='track', limit=10)
                
                if results and 'tracks' in results and 'items' in results['tracks']:
                    for track in results['tracks']['items']:
                        # Skip if we've already added this track
                        if track['id'] in seen_tracks:
                            continue
                            
                        # Create song object
                        song = {
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                            'album': track['album']['name'] if 'album' in track else 'Unknown',
                            'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'popularity': track['popularity'],
                            'release_date': track['album']['release_date'] if 'album' in track and 'release_date' in track['album'] else None,
                            'preview_url': track['preview_url'],
                            'spotify_url': track['external_urls']['spotify'] if 'external_urls' in track and 'spotify' in track['external_urls'] else None,
                            'match_type': 'Popular Malayalam',
                            'query': 'Malayalam popular'
                        }
                        
                        recommendations.append(song)
                        seen_tracks.add(track['id'])
            except Exception as e:
                print(f"Error getting general Malayalam recommendations: {e}")
        
        # If we still don't have recommendations, return fallback
        if not recommendations:
            return get_fallback_malayalam_songs()
        
        # Sort by popularity
        recommendations.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        
        return recommendations[:15]  # Return top 15 songs
        
    except Exception as e:
        print(f"Error getting enhanced Malayalam songs: {e}")
        return get_fallback_malayalam_songs()

def get_fallback_malayalam_songs():
    """
    Get fallback Malayalam song recommendations when the Spotify API fails
    
    Returns:
        list: Fallback Malayalam song recommendations
    """
    # Hardcoded fallback Malayalam songs
    fallback_songs = [
        {
            'id': 'ml1',
            'name': 'Enthanentharo',
            'artist': 'KS Chithra',
            'album': 'Devasuram',
            'image': 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96',
            'popularity': 85,
            'release_date': '1993-04-14',
            'preview_url': None,
            'spotify_url': 'https://open.spotify.com/track/5FJCvPFQsJQWcf4sVMhpM7',
            'match_type': 'Classic Malayalam',
            'query': 'fallback'
        },
        {
            'id': 'ml2',
            'name': 'Aaromale',
            'artist': 'Benny Dayal',
            'album': 'Vinnaithandi Varuvaya',
            'image': 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36',
            'popularity': 82,
            'release_date': '2010-01-21',
            'preview_url': None,
            'spotify_url': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b',
            'match_type': 'Popular Malayalam',
            'query': 'fallback'
        },
        {
            'id': 'ml3',
            'name': 'Malare',
            'artist': 'Vijay Yesudas',
            'album': 'Premam',
            'image': 'https://i.scdn.co/image/ab67616d0000b2739f39192eea82c38ffa2e2c33',
            'popularity': 80,
            'release_date': '2015-05-29',
            'preview_url': None,
            'spotify_url': 'https://open.spotify.com/track/2XU0oxnq2qxCpomAAuJY8K',
            'match_type': 'Popular Malayalam',
            'query': 'fallback'
        },
        {
            'id': 'ml4',
            'name': 'Jeevamshamayi',
            'artist': 'Shreya Ghoshal',
            'album': 'Theevandi',
            'image': 'https://i.scdn.co/image/ab67616d0000b273fc2101e6889d6ce9025f85f2',
            'popularity': 78,
            'release_date': '2018-09-07',
            'preview_url': None,
            'spotify_url': 'https://open.spotify.com/track/7qEHsqek33rTcFNT9PFqLf',
            'match_type': 'Popular Malayalam',
            'query': 'fallback'
        },
        {
            'id': 'ml5',
            'name': 'Kaikkottum Kandittilla',
            'artist': 'Haricharan',
            'album': 'Dhamaka',
            'image': 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96',
            'popularity': 75,
            'release_date': '2020-01-01',
            'preview_url': None,
            'spotify_url': 'https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3',
            'match_type': 'Recent Malayalam',
            'query': 'fallback'
        }
    ]
    
    return fallback_songs

# Main function to get recommendations
def get_trending_songs(analysis_json):
    """
    Wrapper function to get trending songs based on image analysis
    
    Args:
        analysis_json (dict): Analysis JSON from Gemini
        
    Returns:
        list: Song recommendations
    """
    # If analysis_json is a string, parse it
    if isinstance(analysis_json, str):
        try:
            analysis_json = json.loads(analysis_json)
        except Exception as e:
            print(f"Error parsing analysis JSON: {e}")
            return []
    
    # Get enhanced song recommendations
    return get_enhanced_songs(analysis_json)
