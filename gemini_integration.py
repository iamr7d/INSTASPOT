import base64
import os
import json
import random
from PIL import Image
import io

# Mock Gemini API for demonstration purposes
def resize_image(image_data, max_size=(1024, 1024)):
    """
    Resize image to fit within max dimensions while preserving aspect ratio
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Convert to RGB if image has alpha channel
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_data

def encode_image_to_base64(image_data):
    """
    Encode image data to base64
    """
    try:
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def process_image_with_gemini(image_data):
    """
    Process an image with Gemini API and return analysis JSON.
    This is a mock implementation for demonstration purposes.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        str: JSON string with analysis results
    """
    try:
        # In a real implementation, this would call the Gemini API
        # For now, we'll return a mock response with more variability
        
        # Use image data as a seed for randomization to ensure different images get different results
        # This is a simple way to create image-dependent randomization in our mock implementation
        random_seed = sum(image_data[:100]) if len(image_data) >= 100 else sum(image_data)
        random.seed(random_seed)
        
        # Generate scene type and other elements with more variety
        scene_types = ["nature", "urban", "indoor", "beach", "mountains", "party", "celebration", 
                      "travel", "concert", "festival", "cafe", "restaurant", "sunset", "sunrise", 
                      "sports", "workout", "meditation", "study", "work", "family", "friends"]
        
        time_options = ["morning", "afternoon", "evening", "night", "dawn", "dusk", "midday", "midnight"]
        
        mood_options = ["happy", "sad", "energetic", "calm", "romantic", "nostalgic", "excited", 
                       "peaceful", "anxious", "hopeful", "determined", "reflective", "playful", 
                       "mysterious", "serene", "tense", "relaxed", "inspired", "focused"]
        
        emotion_options = ["joy", "love", "peace", "melancholy", "wonder", "amusement", "anticipation",
                          "satisfaction", "gratitude", "pride", "awe", "contentment", "enthusiasm",
                          "hope", "interest", "pleasure", "serenity", "surprise"]
        
        object_options = ["person", "tree", "car", "building", "water", "sky", "food", "animal", 
                         "flower", "mountain", "beach", "ocean", "river", "city", "street", "road",
                         "house", "apartment", "office", "park", "garden", "forest", "desert", 
                         "snow", "rain", "cloud", "sun", "moon", "star", "book", "phone", "laptop",
                         "coffee", "tea", "drink", "meal", "fruit", "vegetable", "pet", "bird",
                         "fish", "insect", "furniture", "art", "music", "instrument", "sport"]
        
        color_options = ["blue", "green", "red", "yellow", "purple", "orange", "pink", "black", 
                        "white", "brown", "gray", "teal", "navy", "maroon", "olive", "mint", 
                        "coral", "turquoise", "indigo", "violet", "magenta", "crimson", "gold",
                        "silver", "bronze", "beige", "ivory", "lavender", "peach", "aqua"]
        
        characteristic_options = ["bright", "dark", "colorful", "monochrome", "vibrant", "muted", 
                                 "sharp", "blurry", "high-contrast", "low-contrast", "saturated",
                                 "desaturated", "warm", "cool", "vintage", "modern", "minimalist",
                                 "busy", "clean", "messy", "symmetrical", "asymmetrical", "natural",
                                 "artificial", "rustic", "elegant", "casual", "formal", "abstract",
                                 "realistic", "dreamy", "harsh", "soft", "grainy", "smooth"]
        
        # Select elements with weighted randomness to create more realistic combinations
        scene_type = random.choice(scene_types)
        time_of_day = random.choice(time_options)
        
        # Select mood and emotion that are somewhat related
        mood = random.choice(mood_options)
        # Filter emotions that might go with the mood
        if mood in ["happy", "energetic", "excited", "playful"]:
            filtered_emotions = ["joy", "amusement", "enthusiasm", "anticipation", "pleasure", "surprise"]
        elif mood in ["sad", "melancholy", "reflective"]:
            filtered_emotions = ["melancholy", "wonder", "interest", "serenity", "peace"]
        elif mood in ["calm", "peaceful", "serene", "relaxed"]:
            filtered_emotions = ["peace", "contentment", "serenity", "love", "gratitude"]
        elif mood in ["romantic", "nostalgic"]:
            filtered_emotions = ["love", "wonder", "awe", "contentment", "joy", "hope"]
        else:
            filtered_emotions = emotion_options
            
        emotion = random.choice(filtered_emotions)
        
        # Select objects based on scene type
        if scene_type == "nature":
            object_weights = [3 if obj in ["tree", "water", "sky", "flower", "mountain", "beach", "ocean", 
                                          "river", "forest", "desert", "snow", "rain", "cloud", "sun", 
                                          "moon", "star", "animal", "bird", "fish", "insect"] else 1 
                             for obj in object_options]
        elif scene_type in ["urban", "city"]:
            object_weights = [3 if obj in ["building", "car", "street", "road", "person", "city", 
                                          "apartment", "office"] else 1 for obj in object_options]
        elif scene_type == "indoor":
            object_weights = [3 if obj in ["person", "furniture", "book", "phone", "laptop", "coffee", 
                                          "tea", "drink", "meal", "art", "music", "instrument"] else 1 
                             for obj in object_options]
        else:
            object_weights = [1 for _ in object_options]
            
        # Select 3-5 objects with weighted randomness
        num_objects = random.randint(3, 5)
        objects = random.choices(object_options, weights=object_weights, k=num_objects)
        objects = list(set(objects))  # Remove duplicates
        
        # Select 3-4 dominant colors
        num_colors = random.randint(3, 4)
        dominant_colors = random.sample(color_options, num_colors)
        
        # Select 3-5 characteristics
        num_characteristics = random.randint(3, 5)
        characteristics = random.sample(characteristic_options, num_characteristics)
        
        # Create a custom image description that matches the scene type and objects
        image_description = f"This {time_of_day} {scene_type} scene contains {', '.join(objects[:2])}. "
        image_description += f"The {mood} ambiance evokes {emotion} in the viewer. "
        image_description += f"The {', '.join(dominant_colors[:2])} color scheme complements the {characteristics[0]} visual style."
        
        # Generate keywords for Spotify searches
        music_keywords = objects[:2] + [mood, emotion] + dominant_colors[:2]
        
        # Add language-based song suggestions
        languages = ["Malayalam", "Hindi", "English", "Tamil", "Telugu", "Korean", "Spanish"]
        language_suggestions = {}
        
        for language in languages:
            artists = get_artists_for_language(language, mood)
            songs = get_songs_for_language(language, mood, emotion)
            language_suggestions[language] = {
                "artists": artists,
                "songs": songs,
                "description": f"The {mood} mood and {emotion} emotion in this {scene_type} scene would pair well with {language} music."
            }
        
        # Generate a more detailed analysis with image description
        analysis = {
            "mood": mood,
            "emotion": emotion,
            "scene_type": scene_type,
            "time_of_day": time_of_day,
            "dominant_colors": dominant_colors,
            "objects": objects,
            "characteristics": characteristics,
            "image_description": image_description,
            "music_keywords": music_keywords,
            "language_suggestions": language_suggestions,
            # Add additional context to help with song selection
            "context": {
                "energy_level": get_energy_level(mood, emotion),
                "tempo": get_tempo(mood, emotion),
                "genre_hints": get_genre_hints(scene_type, mood)
            }
        }
        
        return json.dumps(analysis)
    except Exception as e:
        print(f"Error processing image with Gemini: {e}")
        # Return a basic analysis as fallback
        return json.dumps({
            "mood": "neutral",
            "emotion": "neutral",
            "scene_type": "general",
            "time_of_day": "day",
            "dominant_colors": ["blue", "white"],
            "objects": ["scene"],
            "characteristics": ["general"],
            "image_description": "This appears to be an image that was uploaded for analysis.",
            "music_keywords": ["neutral"],
            "language_suggestions": {},
            "context": {}
        })

def describe_image_with_gemini(image_data):
    """
    Process an image with Gemini API to get a description and music keywords.
    This is a mock implementation for demonstration purposes.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        dict: Dictionary with description and music keyword
    """
    try:
        # In a real implementation, this would call the Gemini API with the prompt
        # "Describe this image briefly and suggest a related keyword for music search."
        
        # For now, we'll use our existing process_image_with_gemini function and extract what we need
        analysis_json = json.loads(process_image_with_gemini(image_data))
        
        # Extract the image description
        image_description = analysis_json.get('image_description', 'No description available')
        
        # Create a more detailed description with scene, mood, and objects
        scene_type = analysis_json.get('scene_type', '')
        mood = analysis_json.get('mood', '')
        emotion = analysis_json.get('emotion', '')
        objects = analysis_json.get('objects', [])
        time_of_day = analysis_json.get('time_of_day', '')
        
        # Format the description similar to the example
        detailed_description = f"**Description:** This {time_of_day} {scene_type} scene "
        if objects:
            detailed_description += f"contains {', '.join(objects[:3])}. "
        detailed_description += f"The image evokes a feeling of {mood} and {emotion}."
        
        # Generate a music keyword based on the analysis
        # Format similar to "Indie Folk World Music" from the example
        
        # Map scene types to music genres
        scene_to_genre = {
            "nature": "Ambient Nature",
            "mountains": "Mountain Folk",
            "beach": "Beach Acoustic",
            "forest": "Forest Ambient",
            "urban": "Urban",
            "city": "City Pop",
            "street": "Street",
            "party": "Party",
            "celebration": "Celebration",
            "concert": "Live Concert",
            "festival": "Festival",
            "cafe": "Cafe Jazz",
            "restaurant": "Dinner Jazz",
            "sunset": "Sunset Chill",
            "sunrise": "Morning Meditation",
            "travel": "World Music",
            "meditation": "Meditation",
            "study": "Study Focus",
            "work": "Work Focus"
        }
        
        # Map moods to music styles
        mood_to_style = {
            "happy": "Upbeat",
            "sad": "Melancholic",
            "energetic": "Energetic",
            "calm": "Calm",
            "romantic": "Romantic",
            "nostalgic": "Nostalgic",
            "excited": "Exciting",
            "peaceful": "Peaceful",
            "reflective": "Reflective",
            "playful": "Playful",
            "mysterious": "Mysterious",
            "serene": "Serene"
        }
        
        # Get genre from scene type
        genre = scene_to_genre.get(scene_type, "Contemporary")
        
        # Get style from mood
        style = mood_to_style.get(mood, "")
        
        # Create music keyword
        if scene_type in ["travel", "beach", "mountains", "nature", "forest"]:
            music_keyword = f"Indie Folk {genre}"
        elif scene_type in ["party", "celebration", "concert", "festival"]:
            music_keyword = f"{style} {genre} Music"
        elif mood in ["romantic", "nostalgic", "peaceful"]:
            music_keyword = f"Melodic {style} {genre}"
        elif mood in ["energetic", "excited"]:
            music_keyword = f"Energetic {genre}"
        else:
            music_keyword = f"{style} {genre} Music"
        
        # Clean up any double spaces
        music_keyword = " ".join(music_keyword.split())
        
        return {
            "description": detailed_description,
            "music_keyword": music_keyword
        }
    except Exception as e:
        print(f"Error describing image with Gemini: {e}")
        return {
            "description": "This appears to be an image that was uploaded for analysis.",
            "music_keyword": "Relaxing Music"
        }

def generate_musical_association_for_scene(scene_type, mood, emotion):
    """Generate a musical association that matches the scene type, mood, and emotion"""
    
    # Select appropriate genre based on scene type
    scene_to_genre = {
        "nature": ["ambient", "classical", "folk"],
        "urban": ["hip-hop", "electronic", "jazz", "rock"],
        "indoor": ["pop", "jazz", "acoustic"],
        "beach": ["reggae", "tropical", "chill"],
        "mountains": ["folk", "ambient", "cinematic"],
        "party": ["dance", "pop", "electronic"],
        "celebration": ["upbeat", "festive", "traditional Malayalam"],
        "travel": ["world music", "cinematic", "instrumental"]
    }
    
    # Select appropriate instruments based on mood
    mood_to_instruments = {
        "happy": ["guitar", "piano", "percussion", "flute"],
        "sad": ["violin", "piano", "cello", "vocals"],
        "energetic": ["drums", "electric guitar", "synthesizers", "percussion"],
        "calm": ["piano", "acoustic guitar", "strings", "flute"],
        "romantic": ["piano", "violin", "acoustic guitar", "vocals"],
        "nostalgic": ["piano", "strings", "acoustic guitar", "vocals"],
        "excited": ["drums", "electric guitar", "synthesizers", "brass"]
    }
    
    # Select appropriate tempo based on emotion
    emotion_to_tempo = {
        "joy": ["upbeat", "lively", "rhythmic"],
        "love": ["flowing", "gentle", "moderate"],
        "peace": ["slow", "gentle", "flowing"],
        "melancholy": ["slow", "deliberate", "gentle"],
        "wonder": ["flowing", "dynamic", "moderate"],
        "amusement": ["playful", "upbeat", "rhythmic"],
        "anticipation": ["building", "moderate", "dynamic"]
    }
    
    # Get random selections that match the scene, mood, and emotion
    genres = scene_to_genre.get(scene_type, ["classical", "pop", "traditional Malayalam"])
    instruments = mood_to_instruments.get(mood, ["piano", "guitar", "vocals"])
    tempos = emotion_to_tempo.get(emotion, ["moderate", "flowing", "gentle"])
    
    genre = random.choice(genres)
    instrument_pair = random.sample(instruments, min(2, len(instruments)))
    tempo = random.choice(tempos)
    characteristics = random.choice(["melodic", "harmonic", "atmospheric", "rhythmic", "textural", "emotional"])
    
    # Create the musical association
    return f"This image would pair beautifully with {genre} music featuring {' and '.join(instrument_pair)}. The {tempo} rhythm would complement the {mood} mood of the scene, perhaps something with {characteristics} qualities."

def get_artists_for_language(language, mood):
    """Get popular artists for a specific language and mood"""
    artists_by_language_mood = {
        "Malayalam": {
            "happy": ["Vineeth Sreenivasan", "Vidyadharan Master", "Pradeep Somasundaran", "KS Harisankar"],
            "sad": ["KS Chithra", "KJ Yesudas", "Sithara Krishnakumar", "Shreya Ghoshal"],
            "energetic": ["Vidhu Prathap", "Najim Arshad", "Shankar Mahadevan", "Sujatha"],
            "calm": ["Madhu Balakrishnan", "Swetha Mohan", "Unni Menon", "Venugopal"],
            "romantic": ["Haricharan", "Karthik", "Shweta Mohan", "Manjari"],
            "nostalgic": ["KJ Yesudas", "KS Chithra", "P Jayachandran", "S Janaki"],
            "excited": ["Vineeth Sreenivasan", "Najim Arshad", "Shankar Mahadevan", "Jassie Gift"]
        },
        "Hindi": {
            "happy": ["Arijit Singh", "Shreya Ghoshal", "Sonu Nigam", "Neha Kakkar"],
            "sad": ["Arijit Singh", "Atif Aslam", "Shreya Ghoshal", "Lata Mangeshkar"],
            "energetic": ["Badshah", "Honey Singh", "Diljit Dosanjh", "Neha Kakkar"],
            "calm": ["AR Rahman", "Shreya Ghoshal", "Arijit Singh", "Lata Mangeshkar"],
            "romantic": ["Arijit Singh", "Atif Aslam", "Shreya Ghoshal", "Kumar Sanu"],
            "nostalgic": ["Kishore Kumar", "Lata Mangeshkar", "Mohammad Rafi", "Asha Bhosle"],
            "excited": ["Mika Singh", "Neha Kakkar", "Badshah", "Honey Singh"]
        },
        "English": {
            "happy": ["Ed Sheeran", "Taylor Swift", "Bruno Mars", "Pharrell Williams"],
            "sad": ["Adele", "Sam Smith", "Billie Eilish", "Lana Del Rey"],
            "energetic": ["Dua Lipa", "The Weeknd", "Post Malone", "Ariana Grande"],
            "calm": ["Coldplay", "Billie Eilish", "Lana Del Rey", "Bon Iver"],
            "romantic": ["Ed Sheeran", "John Legend", "Adele", "Bruno Mars"],
            "nostalgic": ["The Beatles", "Queen", "Fleetwood Mac", "Elton John"],
            "excited": ["Dua Lipa", "The Weeknd", "Lady Gaga", "Beyoncé"]
        },
        "Tamil": {
            "happy": ["Anirudh Ravichander", "Sid Sriram", "AR Rahman", "Yuvan Shankar Raja"],
            "sad": ["AR Rahman", "Sid Sriram", "Shreya Ghoshal", "Chinmayi"],
            "energetic": ["Anirudh Ravichander", "Dhanush", "Yuvan Shankar Raja", "Benny Dayal"],
            "calm": ["AR Rahman", "Sid Sriram", "Chinmayi", "Karthik"],
            "romantic": ["Sid Sriram", "AR Rahman", "Chinmayi", "Haricharan"],
            "nostalgic": ["Ilaiyaraaja", "SP Balasubrahmanyam", "S Janaki", "KJ Yesudas"],
            "excited": ["Anirudh Ravichander", "Dhanush", "Yuvan Shankar Raja", "Benny Dayal"]
        },
        "Telugu": {
            "happy": ["SS Thaman", "Sid Sriram", "Anirudh Ravichander", "DSP"],
            "sad": ["Sid Sriram", "Shreya Ghoshal", "SP Balasubrahmanyam", "Chinmayi"],
            "energetic": ["SS Thaman", "DSP", "Anirudh Ravichander", "Nakash Aziz"],
            "calm": ["MM Keeravani", "Sid Sriram", "Shreya Ghoshal", "Karthik"],
            "romantic": ["Sid Sriram", "Shreya Ghoshal", "Chinmayi", "Armaan Malik"],
            "nostalgic": ["SP Balasubrahmanyam", "S Janaki", "P Susheela", "MM Keeravani"],
            "excited": ["SS Thaman", "DSP", "Anirudh Ravichander", "Nakash Aziz"]
        },
        "Korean": {
            "happy": ["BTS", "BLACKPINK", "TWICE", "Psy"],
            "sad": ["IU", "Taeyeon", "BTS", "AKMU"],
            "energetic": ["BTS", "BLACKPINK", "NCT 127", "Stray Kids"],
            "calm": ["IU", "Taeyeon", "AKMU", "Heize"],
            "romantic": ["IU", "Taeyeon", "Paul Kim", "Crush"],
            "nostalgic": ["Big Bang", "2NE1", "Wonder Girls", "TVXQ"],
            "excited": ["BTS", "BLACKPINK", "NCT 127", "Stray Kids"]
        },
        "Spanish": {
            "happy": ["J Balvin", "Bad Bunny", "Shakira", "Enrique Iglesias"],
            "sad": ["Alejandro Sanz", "Juanes", "Rosalía", "Enrique Iglesias"],
            "energetic": ["J Balvin", "Bad Bunny", "Daddy Yankee", "Ozuna"],
            "calm": ["Juanes", "Rosalía", "Alejandro Sanz", "Natalia Lafourcade"],
            "romantic": ["Enrique Iglesias", "Shakira", "Luis Fonsi", "Juanes"],
            "nostalgic": ["Julio Iglesias", "Gloria Estefan", "Juan Luis Guerra", "Celia Cruz"],
            "excited": ["J Balvin", "Bad Bunny", "Daddy Yankee", "Ozuna"]
        }
    }
    
    # Get artists for the specified language and mood, or return default artists if not found
    return artists_by_language_mood.get(language, {}).get(mood, ["Unknown Artist 1", "Unknown Artist 2"])

def get_songs_for_language(language, mood, emotion):
    """Get popular songs for a specific language, mood, and emotion"""
    songs_by_language_mood_emotion = {
        "Malayalam": {
            "happy": {
                "joy": ["Enthanentharo", "Jimikki Kammal", "Appangal Embadum"],
                "love": ["Pranayame", "Ee Shishirakaalam", "Malare"],
                "peace": ["Akale", "Karalinte Nattil", "Aaromale"],
                "melancholy": ["Etho Mazhayil", "Karalinte", "Aaromale"],
                "wonder": ["Ee Shishirakaalam", "Enthanentharo", "Akale"],
                "amusement": ["Jimikki Kammal", "Appangal Embadum", "Entammede Jimikki Kammal"],
                "anticipation": ["Pranayame", "Malare", "Jimikki Kammal"]
            },
            "sad": {
                "joy": ["Akale", "Aaromale", "Etho Mazhayil"],
                "love": ["Aaromale", "Karalinte", "Etho Mazhayil"],
                "peace": ["Akale", "Aaromale", "Karalinte"],
                "melancholy": ["Etho Mazhayil", "Karalinte", "Aaromale"],
                "wonder": ["Akale", "Etho Mazhayil", "Aaromale"],
                "amusement": ["Enthanentharo", "Jimikki Kammal", "Appangal Embadum"],
                "anticipation": ["Aaromale", "Akale", "Etho Mazhayil"]
            }
        },
        "English": {
            "happy": {
                "joy": ["Happy by Pharrell Williams", "Can't Stop the Feeling by Justin Timberlake", "Uptown Funk by Mark Ronson ft. Bruno Mars"],
                "love": ["Perfect by Ed Sheeran", "All of Me by John Legend", "Love On Top by Beyoncé"],
                "peace": ["Fix You by Coldplay", "Somewhere Over the Rainbow by Israel Kamakawiwo'ole", "What a Wonderful World by Louis Armstrong"],
                "melancholy": ["Someone Like You by Adele", "Hello by Adele", "All I Want by Kodaline"],
                "wonder": ["Yellow by Coldplay", "A Sky Full of Stars by Coldplay", "Stargazing by Kygo"],
                "amusement": ["Happy by Pharrell Williams", "Can't Stop the Feeling by Justin Timberlake", "Uptown Funk by Mark Ronson ft. Bruno Mars"],
                "anticipation": ["Viva La Vida by Coldplay", "Waiting All Night by Rudimental", "Waiting for Love by Avicii"]
            },
            "sad": {
                "joy": ["Fix You by Coldplay", "Yellow by Coldplay", "Someone Like You by Adele"],
                "love": ["All I Want by Kodaline", "Someone Like You by Adele", "Hello by Adele"],
                "peace": ["Fix You by Coldplay", "Somewhere Over the Rainbow by Israel Kamakawiwo'ole", "What a Wonderful World by Louis Armstrong"],
                "melancholy": ["Someone Like You by Adele", "Hello by Adele", "All I Want by Kodaline"],
                "wonder": ["Yellow by Coldplay", "A Sky Full of Stars by Coldplay", "Stargazing by Kygo"],
                "amusement": ["Happy by Pharrell Williams", "Can't Stop the Feeling by Justin Timberlake", "Uptown Funk by Mark Ronson ft. Bruno Mars"],
                "anticipation": ["Viva La Vida by Coldplay", "Waiting All Night by Rudimental", "Waiting for Love by Avicii"]
            }
        }
    }
    
    # Get songs for the specified language, mood, and emotion, or return default songs if not found
    default_songs = ["Song 1", "Song 2", "Song 3"]
    
    # Try to get songs for the specific language, mood, and emotion
    language_dict = songs_by_language_mood_emotion.get(language, {})
    mood_dict = language_dict.get(mood, {})
    songs = mood_dict.get(emotion, default_songs)
    
    # If no specific songs were found, try to get songs for just the language and mood
    if songs == default_songs and language in songs_by_language_mood_emotion:
        for emotion_key, emotion_songs in language_dict.get(mood, {}).items():
            if emotion_songs:
                songs = emotion_songs
                break
    
    return songs

def generate_image_description():
    """Generate a detailed image description"""
    
    # Generate random values for the templates
    scene_type = random.choice(["natural", "urban", "coastal", "mountainous", "rural", "indoor", "festive", "serene"])
    objects = ", ".join(random.sample(["people", "trees", "buildings", "water", "sky", "flowers", "animals", "vehicles", "food"], 2))
    time_of_day = random.choice(["morning", "afternoon", "evening", "night", "dawn", "dusk", "midday"])
    mood = random.choice(["peaceful", "energetic", "romantic", "nostalgic", "joyful", "dramatic", "mysterious", "playful"])
    emotion = random.choice(["happiness", "tranquility", "excitement", "wonder", "contentment", "inspiration", "awe", "delight"])
    characteristics = random.choice(["vibrant", "subtle", "contrasting", "harmonious", "dynamic", "balanced", "minimalist", "detailed"])
    colors = ", ".join(random.sample(["blue", "green", "red", "yellow", "purple", "orange", "teal", "gold", "silver"], 2))
    
    # Templates for different parts of the description
    scene_templates = [
        f"This image shows a {scene_type} scene with {objects}.",
        f"The photo captures a beautiful {scene_type} setting featuring {objects}.",
        f"A stunning {scene_type} view with {objects} visible in the frame.",
        f"This {time_of_day} {scene_type} scene contains {objects}.",
        f"The image depicts a {mood} {scene_type} environment with {objects}."
    ]
    
    mood_templates = [
        f"The overall mood is {mood} and conveys a sense of {emotion}.",
        f"There's a strong feeling of {emotion} that creates a {mood} atmosphere.",
        f"The {mood} ambiance evokes {emotion} in the viewer.",
        f"A {mood} scene that resonates with {emotion}.",
        f"The image has a distinctly {mood} quality that inspires {emotion}."
    ]
    
    visual_templates = [
        f"Visually, the image features {characteristics} elements with dominant {colors} tones.",
        f"The {characteristics} composition is enhanced by prominent {colors} colors.",
        f"The photographer captured {characteristics} details with {colors} hues dominating the palette.",
        f"The visual aesthetic is {characteristics}, with rich {colors} colors throughout.",
        f"The {colors} color scheme complements the {characteristics} visual style."
    ]
    
    # Format the templates
    scene_description = random.choice(scene_templates)
    mood_description = random.choice(mood_templates)
    visual_description = random.choice(visual_templates)
    
    # Combine all parts into a cohesive description
    full_description = f"{scene_description} {mood_description} {visual_description}"
    
    return full_description

def get_energy_level(mood, emotion):
    """Determine energy level based on mood and emotion"""
    high_energy_moods = ["happy", "energetic", "excited", "playful", "determined"]
    high_energy_emotions = ["joy", "enthusiasm", "anticipation", "surprise", "amusement"]
    
    low_energy_moods = ["calm", "peaceful", "sad", "reflective", "serene", "relaxed"]
    low_energy_emotions = ["melancholy", "peace", "contentment", "serenity"]
    
    # Count high and low energy indicators
    high_count = (mood in high_energy_moods) + (emotion in high_energy_emotions)
    low_count = (mood in low_energy_moods) + (emotion in low_energy_emotions)
    
    if high_count > low_count:
        return "high"
    elif low_count > high_count:
        return "low"
    else:
        return "medium"

def get_tempo(mood, emotion):
    """Determine suggested tempo based on mood and emotion"""
    fast_tempo_moods = ["energetic", "excited", "happy", "playful"]
    fast_tempo_emotions = ["joy", "enthusiasm", "anticipation", "surprise"]
    
    slow_tempo_moods = ["calm", "peaceful", "sad", "romantic", "nostalgic", "reflective"]
    slow_tempo_emotions = ["melancholy", "peace", "love", "contentment", "serenity"]
    
    # Count fast and slow indicators
    fast_count = (mood in fast_tempo_moods) + (emotion in fast_tempo_emotions)
    slow_count = (mood in slow_tempo_moods) + (emotion in slow_tempo_emotions)
    
    if fast_count > slow_count:
        return "fast"
    elif slow_count > fast_count:
        return "slow"
    else:
        return "moderate"

def get_genre_hints(scene_type, mood):
    """Get genre hints based on scene type and mood"""
    genre_map = {
        "nature": ["ambient", "folk", "classical", "instrumental"],
        "urban": ["hip-hop", "electronic", "pop", "r&b", "rock"],
        "indoor": ["jazz", "acoustic", "lo-fi", "indie"],
        "beach": ["reggae", "tropical", "surf rock", "chill"],
        "mountains": ["folk", "indie folk", "ambient", "cinematic"],
        "party": ["dance", "electronic", "pop", "hip-hop"],
        "celebration": ["pop", "dance", "festive", "traditional"],
        "travel": ["world music", "cinematic", "instrumental"],
        "concert": ["rock", "pop", "live music"],
        "festival": ["edm", "dance", "world music"],
        "cafe": ["jazz", "acoustic", "lo-fi", "bossa nova"],
        "restaurant": ["jazz", "classical", "ambient"],
        "sunset": ["chill", "ambient", "lo-fi", "acoustic"],
        "sunrise": ["ambient", "classical", "new age"],
        "sports": ["rock", "hip-hop", "electronic"],
        "workout": ["electronic", "hip-hop", "rock", "motivational"],
        "meditation": ["ambient", "new age", "classical", "instrumental"],
        "study": ["lo-fi", "classical", "instrumental", "ambient"],
        "work": ["lo-fi", "ambient", "instrumental", "jazz"],
        "family": ["pop", "folk", "acoustic"],
        "friends": ["pop", "rock", "hip-hop", "electronic"]
    }
    
    mood_genre_map = {
        "happy": ["pop", "dance", "indie pop", "funk"],
        "sad": ["indie folk", "piano", "ambient", "slow"],
        "energetic": ["electronic", "rock", "hip-hop", "dance"],
        "calm": ["ambient", "classical", "acoustic", "lo-fi"],
        "romantic": ["r&b", "soul", "acoustic", "jazz"],
        "nostalgic": ["oldies", "classic rock", "retro", "vintage"],
        "excited": ["dance", "electronic", "pop", "rock"],
        "peaceful": ["ambient", "new age", "classical", "acoustic"],
        "reflective": ["indie folk", "acoustic", "piano", "ambient"]
    }
    
    # Get genres from scene type
    scene_genres = genre_map.get(scene_type, ["pop", "rock", "electronic"])
    
    # Get genres from mood
    mood_genres = mood_genre_map.get(mood, ["pop", "rock"])
    
    # Combine and prioritize genres that appear in both lists
    combined_genres = []
    for genre in scene_genres:
        if genre in mood_genres:
            combined_genres.append(genre)
    
    # Add some unique genres from each list
    for genre in scene_genres:
        if genre not in combined_genres and len(combined_genres) < 5:
            combined_genres.append(genre)
            
    for genre in mood_genres:
        if genre not in combined_genres and len(combined_genres) < 5:
            combined_genres.append(genre)
    
    # Ensure we have at least 3 genres
    if len(combined_genres) < 3:
        combined_genres.extend(["pop", "rock", "electronic"][:3-len(combined_genres)])
    
    return combined_genres[:5]  # Return up to 5 genre hints
