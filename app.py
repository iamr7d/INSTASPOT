from flask import Flask, render_template, request, jsonify
from gemini_integration import process_image_with_gemini
from spotify_enhanced import get_enhanced_malayalam_songs, get_enhanced_songs
from gemini_direct import describe_image, extract_keyword_from_description, search_spotify_tracks, analyze_image_attributes
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Spotify API Setup
SPOTIFY_CLIENT_ID = "af052d02571c4335bcce9dce3d755c7e"
SPOTIFY_CLIENT_SECRET = "d46b38860c86452280e8e653209e1298"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read the image file
        image_data = image_file.read()
        
        # Analyze the image using Gemini API
        description = describe_image(image_data)
        
        # Extract keywords from the description
        keywords, primary_keyword = extract_keyword_from_description(description)
        
        # Extract Instagram caption if available
        instagram_caption = ""
        if "**Instagram Caption:**" in description:
            caption_section = description.split("**Instagram Caption:**")[1].strip()
            instagram_caption = caption_section.split("**")[0].strip() if "**" in caption_section else caption_section
        
        # Get clean description without the formatting
        clean_description = description
        if "**Description:**" in description:
            desc_section = description.split("**Description:**")[1].strip()
            clean_description = desc_section.split("**")[0].strip() if "**" in desc_section else desc_section
        
        # Analyze image for scene, mood, emotion, and dominant color
        scene, mood, emotion, dominant_color = analyze_image_attributes(image_data)
        
        # Search for tracks on Spotify based on the extracted keywords
        track_strings, formatted_tracks = search_spotify_tracks(keywords)
        
        # Add relevance scores and match types to tracks
        for i, track in enumerate(formatted_tracks):
            # Calculate relevance score (0-100) based on position and popularity
            position_score = max(0, 100 - (i * 10))  # First tracks get higher scores
            popularity_score = track.get('popularity', 50)
            relevance_score = (position_score * 0.7) + (popularity_score * 0.3)
            track['relevance'] = min(100, relevance_score)
            
            # Determine match type based on keywords
            if i < len(keywords):
                track['match_type'] = keywords[i]
            else:
                # For tracks beyond the number of keywords, assign mood or emotion
                if i % 2 == 0 and mood:
                    track['match_type'] = mood
                else:
                    track['match_type'] = emotion if emotion else "related"
        
        # Return the results
        return jsonify({
            'imageDescription': clean_description,
            'imageKeywords': keywords,
            'primaryKeyword': primary_keyword,
            'instagramCaption': instagram_caption,
            'spotifyTracks': formatted_tracks,
            'scene': scene,
            'mood': mood,
            'emotion': emotion,
            'dominantColor': dominant_color
        })
    
    except Exception as e:
        print(f"Error in analyze route: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
