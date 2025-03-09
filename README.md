# InstaMatch 🎵 📸

<div align="center">

![InstaMatch Logo](static/img/logo.svg)

**AI-Powered Instagram Story Song Recommender**

[![Netlify Status](https://api.netlify.com/api/v1/badges/your-netlify-id/deploy-status)](https://app.netlify.com/sites/instaspot/deploys)
[![GitHub license](https://img.shields.io/github/license/iamr7d/INSTASPOT?color=blue)](https://github.com/iamr7d/INSTASPOT/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/iamr7d/INSTASPOT)](https://github.com/iamr7d/INSTASPOT/stargazers)

[Demo](https://instaspot.netlify.app) • [Features](#features) • [Installation](#installation) • [How It Works](#how-it-works) • [Contributing](#contributing)

</div>

---

## 🚀 Overview

InstaMatch is a cutting-edge web application that uses **Google's Gemini AI** and the **Spotify API** to suggest the perfect songs for your Instagram stories based on intelligent image analysis. Simply upload an image, and our AI will analyze its mood, emotions, and characteristics to recommend trending songs that match the vibe of your visual content.

<div align="center">
  <img src="https://i.imgur.com/placeholder.jpg" alt="InstaMatch Demo" width="80%">
</div>

## ✨ Features

- **🧠 AI-Powered Image Analysis** - Upload any image and get detailed analysis of mood, emotions, and scene type
- **🎵 Intelligent Song Recommendations** - Receive song suggestions that perfectly match your image's vibe
- **📱 Instagram Caption Generation** - Get AI-generated captions ready to use with your Instagram stories
- **🎧 Song Previews** - Listen to song previews directly in the app before making your choice
- **🔗 Spotify Integration** - Seamlessly connect to Spotify to listen to full songs
- **🎨 Beautiful UI/UX** - Enjoy a modern, responsive interface that works on all devices

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Spotify Developer Account
- Google Gemini API Key

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/iamr7d/INSTASPOT.git
cd INSTASPOT
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

4. **Run the application**

```bash
python app.py
```

5. **Open your browser**

Navigate to `http://127.0.0.1:5000`

## 🔍 How It Works

<div align="center">
  <img src="https://i.imgur.com/placeholder2.jpg" alt="How InstaMatch Works" width="80%">
</div>

1. **Upload an Image** - Select the image you want to use for your Instagram story
2. **AI Analysis** - Gemini AI analyzes your image to determine mood, emotions, and scene type
3. **Keyword Extraction** - The system extracts relevant music keywords from the analysis
4. **Song Matching** - Spotify API is queried to find songs matching the extracted keywords
5. **Relevance Scoring** - Songs are ranked based on their relevance to your image
6. **Preview & Select** - Listen to previews and select the perfect song for your story

## 🧩 Project Structure

```
INSTASPOT/
├── app.py                # Main Flask application
├── gemini_direct.py      # Gemini AI integration
├── spotify.py            # Spotify API integration
├── requirements.txt      # Python dependencies
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── img/              # Images and icons
├── templates/            # HTML templates
└── functions/            # Netlify serverless functions
```

## 🌐 Deployment

### Netlify Deployment

1. Fork this repository
2. Sign up on [Netlify](https://www.netlify.com/)
3. Create a new site from Git and select your forked repository
4. Configure the build settings:
   - Build command: (leave blank)
   - Publish directory: `static`
5. Add environment variables in the Netlify dashboard
6. Deploy!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Spotify API](https://developer.spotify.com/documentation/web-api/) for music data
- [Google Gemini AI](https://ai.google.dev/) for image analysis
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Netlify](https://www.netlify.com/) for hosting

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/iamr7d">iamr7d</a>
</div>
