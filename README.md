# Instagram Story Song Suggester

A modern web application that uses Gemini AI and Spotify to suggest trending Malayalam songs for your Instagram stories based on image analysis.

![Instagram Story Song Suggester](https://i.imgur.com/placeholder.jpg)

## Features

- **AI-Powered Image Analysis**: Upload any image you plan to use for your Instagram story and our application will analyze it using Google's Gemini AI to determine the mood, emotions, and characteristics.
- **Intelligent Song Recommendations**: Based on the image analysis, the application suggests trending Malayalam songs that match the mood and emotional context of your image.
- **Trending Malayalam Focus**: Specifically designed to recommend the latest and most popular Malayalam songs, keeping your Instagram stories culturally relevant.
- **Song Previews**: Listen to song previews directly within the application before choosing the perfect song for your story.
- **Spotify Integration**: Seamlessly connect to Spotify to listen to the full songs.
- **Beautiful, Responsive UI**: Enjoy a modern, user-friendly interface that works on both desktop and mobile devices.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account (for API credentials)
- Google Gemini API Key

### Installation

1. Clone the repository or download the source code:
   ```
   git clone <repository-url>
   cd SPOTIFY
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - For Spotify API:
     ```
     export SPOTIFY_CLIENT_ID="your-spotify-client-id"
     export SPOTIFY_CLIENT_SECRET="your-spotify-client-secret"
     ```
   - For Gemini API:
     ```
     export GEMINI_API_KEY="your-gemini-api-key"
     ```

   On Windows, use:
   ```
   set SPOTIFY_CLIENT_ID=your-spotify-client-id
   set SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
   set GEMINI_API_KEY=your-gemini-api-key
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## How It Works

1. **Upload an Image**: Upload the image you plan to use for your Instagram story.
2. **AI Analysis**: The application uses Gemini AI to analyze the image and determine its mood, emotions, and characteristics.
3. **Song Matching**: Based on the analysis, the application searches for trending Malayalam songs on Spotify that match the mood and emotional context of your image.
4. **Preview and Select**: Preview the recommended songs directly within the application and select the perfect one for your Instagram story.

## Project Structure

- `app.py`: Main Flask application that handles routes and requests.
- `gemini_integration.py`: Handles image processing and analysis with Google's Gemini AI.
- `spotify_enhanced.py`: Contains the logic for fetching and processing trending Malayalam song recommendations from Spotify.
- `spotify.py`: Original Spotify integration code (kept for reference).
- `templates/`: Contains HTML templates for the web application.
- `static/`: Contains CSS, JavaScript, and other static files.
  - `css/style.css`: Styling for the web application.
  - `js/main.js`: JavaScript functionality for the web application.

## API Keys and Security

This application requires API keys for both Spotify and Google Gemini. For security reasons, these keys should be stored as environment variables and not hardcoded in the source code.

- **Spotify API**: You need to create a Spotify Developer account and register an application to get your client ID and client secret.
- **Gemini API**: You need to sign up for Google's Gemini API and obtain an API key.

## Customization

You can customize the application to focus on different languages or genres by modifying the `spotify_enhanced.py` file. Look for the following variables:

- `malayalam_artists`: List of popular artists in your target language.
- `recent_films`: List of recent popular films in your target language.
- `emotion_mood_mapping`: Mapping of emotions and moods to relevant terms in your target language.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Spotify API](https://developer.spotify.com/documentation/web-api/) for providing access to music data.
- [Google Gemini AI](https://ai.google.dev/) for powerful image analysis capabilities.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Spotipy](https://spotipy.readthedocs.io/) for the Spotify API wrapper.

## Contact

If you have any questions or feedback, please open an issue on this repository.
