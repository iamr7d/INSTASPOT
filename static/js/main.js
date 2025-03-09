// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadContainer = document.getElementById('uploadContainer');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const uploadedImage = document.getElementById('uploadedImage');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const analysisContainer = document.getElementById('analysisContainer');
    const geminiVisionContainer = document.getElementById('geminiVisionContainer');
    const recommendationsContainer = document.getElementById('recommendationsContainer');
    const songsContainer = document.getElementById('songsContainer');
    const audioPlayer = document.getElementById('audioPlayer');
    
    // Analysis elements
    const sceneType = document.getElementById('sceneType');
    const mood = document.getElementById('mood');
    const emotion = document.getElementById('emotion');
    const dominantColor = document.getElementById('dominantColor');
    const imageDescription = document.getElementById('imageDescription');
    const musicKeywordsContainer = document.getElementById('musicKeywordsContainer');
    const objectsContainer = document.getElementById('objectsContainer');
    const colorsContainer = document.getElementById('colorsContainer');
    const characteristicsContainer = document.getElementById('characteristicsContainer');

    // Variables
    let selectedFile = null;
    let currentPlayingButton = null;

    // Event Listeners
    uploadBtn.addEventListener('click', () => fileInput.click());

    changeImageBtn.addEventListener('click', () => {
        resetUploadUI();
        fileInput.click();
    });

    fileInput.addEventListener('change', handleFileSelect);

    analyzeBtn.addEventListener('click', analyzeImage);

    // Drag and Drop functionality
    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.classList.add('drag-over');
    });

    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.classList.remove('drag-over');
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('drag-over');

        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Functions
    function handleFileSelect(e) {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    }

    function handleFile(file) {
        // Check if file is an image
        if (!file.type.match('image.*')) {
            alert('Please select an image file');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImage.src = e.target.result;
            uploadPlaceholder.style.display = 'none';
            uploadedImage.style.display = 'block';
            changeImageBtn.style.display = 'flex';
            uploadContainer.classList.add('has-image');
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function resetUploadUI() {
        uploadPlaceholder.style.display = 'block';
        uploadedImage.style.display = 'none';
        changeImageBtn.style.display = 'none';
        uploadContainer.classList.remove('has-image');
        analyzeBtn.disabled = true;
        selectedFile = null;
        fileInput.value = '';
    }

    function analyzeImage() {
        if (!selectedFile) {
            alert('Please select an image first');
            return;
        }
        
        // Show loading state
        loadingContainer.style.display = 'flex';
        analysisContainer.style.display = 'none';
        geminiVisionContainer.style.display = 'none';
        recommendationsContainer.style.display = 'none';
        
        // Create form data
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        // Determine the API endpoint based on environment
        let apiUrl = '/analyze';
        
        // If we're on Netlify, use the serverless function
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            apiUrl = '/.netlify/functions/analyze';
        }
        
        // Send request to server
        fetch(apiUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading state
            loadingContainer.style.display = 'none';
            
            // Display results
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingContainer.style.display = 'none';
            alert('An error occurred while analyzing the image. Please try again.');
        });
    }

    function displayResults(data) {
        // Clear previous results
        analysisContainer.innerHTML = '';
        geminiVisionContainer.innerHTML = '';
        songsContainer.innerHTML = '';
        
        // Basic analysis cards
        sceneType.textContent = data.scene || 'Unknown';
        mood.textContent = data.mood || 'Unknown';
        emotion.textContent = data.emotion || 'Unknown';

        // Set dominant color (first color from the list)
        if (data.dominantColor) {
            const color = data.dominantColor;
            dominantColor.textContent = color;
            dominantColor.style.color = color;
            dominantColor.style.textShadow = isLightColor(color) ? '0 0 1px #000' : 'none';
        } else {
            dominantColor.textContent = 'Unknown';
        }

        // Show the analysis container
        analysisContainer.style.display = 'block';
        
        // Display image description
        if (data.imageDescription) {
            imageDescription.innerHTML = data.imageDescription;
        } else {
            imageDescription.textContent = 'No description available';
        }
        
        // Set music keywords
        musicKeywordsContainer.innerHTML = '';
        
        // Add the primary keyword if available
        if (data.primaryKeyword) {
            const keywordTag = document.createElement('span');
            keywordTag.className = 'keyword-tag highlight';
            keywordTag.innerHTML = `<i class="fas fa-search"></i> ${data.primaryKeyword}`;
            musicKeywordsContainer.appendChild(keywordTag);
        }
        
        // Add other keywords
        if (data.imageKeywords && data.imageKeywords.length > 0) {
            data.imageKeywords.forEach(keyword => {
                // Skip the primary keyword as it's already added
                if (keyword === data.primaryKeyword) return;
                
                const keywordTag = document.createElement('span');
                keywordTag.className = 'keyword-tag';
                keywordTag.innerHTML = `<i class="fas fa-music"></i> ${keyword}`;
                musicKeywordsContainer.appendChild(keywordTag);
            });
        } else if (!data.primaryKeyword) {
            musicKeywordsContainer.innerHTML = '<span class="no-data">No music keywords available</span>';
        }
        
        // Add Instagram caption if available
        if (data.instagramCaption) {
            // Create a container for the Instagram caption
            const captionContainer = document.createElement('div');
            captionContainer.className = 'image-description-box';
            
            // Add the caption header
            const captionHeader = document.createElement('h3');
            captionHeader.innerHTML = '<i class="fab fa-instagram"></i> Instagram Caption';
            captionContainer.appendChild(captionHeader);
            
            // Add the caption content
            const captionContent = document.createElement('p');
            captionContent.className = 'description-text';
            captionContent.textContent = data.instagramCaption;
            captionContainer.appendChild(captionContent);
            
            // Add a copy button
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy Caption';
            copyButton.onclick = function() {
                navigator.clipboard.writeText(data.instagramCaption)
                    .then(() => {
                        copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy Caption';
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Could not copy text: ', err);
                    });
            };
            captionContainer.appendChild(copyButton);
            
            // Add the caption container to the Gemini vision container
            geminiVisionContainer.appendChild(captionContainer);
        }
        
        // Show the Gemini vision container
        geminiVisionContainer.style.display = 'block';
        
        // Display song recommendations
        displaySongs(data.spotifyTracks);
    }

    function displaySongs(tracks) {
        const songsContainer = document.getElementById('songsContainer');
        songsContainer.innerHTML = '';
        
        if (!tracks || tracks.length === 0) {
            const noSongsMessage = document.createElement('div');
            noSongsMessage.className = 'no-songs-message';
            noSongsMessage.innerHTML = '<i class="fas fa-music-slash"></i><p>No songs found. Try another image.</p>';
            songsContainer.appendChild(noSongsMessage);
            recommendationsContainer.style.display = 'block';
            return;
        }
        
        // Create song cards for each track
        tracks.forEach((track, index) => {
            // Create song card
            const songCard = document.createElement('div');
            songCard.className = 'song-card';
            
            // Create album art container
            const albumArtContainer = document.createElement('div');
            albumArtContainer.className = 'album-art-container';
            
            // Create album art
            const albumArt = document.createElement('img');
            albumArt.className = 'album-art';
            albumArt.src = track.album_art || 'static/img/default-album.jpg';
            albumArt.alt = `${track.name} album art`;
            albumArtContainer.appendChild(albumArt);
            
            // Create play button
            if (track.preview_url) {
                const playButton = document.createElement('button');
                playButton.className = 'play-button';
                playButton.innerHTML = '<i class="fas fa-play"></i>';
                playButton.onclick = function() {
                    playSongPreview(track.preview_url, this);
                };
                albumArtContainer.appendChild(playButton);
            }
            
            // Add album art container to song card
            songCard.appendChild(albumArtContainer);
            
            // Create song info container
            const songInfo = document.createElement('div');
            songInfo.className = 'song-info';
            
            // Create song title
            const songTitle = document.createElement('h3');
            songTitle.className = 'song-title';
            songTitle.textContent = track.name;
            songInfo.appendChild(songTitle);
            
            // Create artist name
            const artistName = document.createElement('p');
            artistName.className = 'artist-name';
            artistName.textContent = track.artist;
            songInfo.appendChild(artistName);
            
            // Create album name
            const albumName = document.createElement('p');
            albumName.className = 'album-name';
            albumName.textContent = track.album;
            songInfo.appendChild(albumName);
            
            // Create match info
            const matchInfo = document.createElement('div');
            matchInfo.className = 'match-info';
            
            // Create match type
            if (track.match_type) {
                const matchType = document.createElement('span');
                matchType.className = 'match-type';
                matchType.textContent = track.match_type;
                matchInfo.appendChild(matchType);
            }
            
            // Create relevance indicator
            if (track.relevance) {
                const relevanceContainer = document.createElement('div');
                relevanceContainer.className = 'relevance-container';
                
                const relevanceLabel = document.createElement('span');
                relevanceLabel.className = 'relevance-label';
                relevanceLabel.textContent = 'Match:';
                relevanceContainer.appendChild(relevanceLabel);
                
                const relevanceBar = document.createElement('div');
                relevanceBar.className = 'relevance-bar';
                
                const relevanceFill = document.createElement('div');
                relevanceFill.className = 'relevance-fill';
                relevanceFill.style.width = `${track.relevance}%`;
                
                // Set color based on relevance score
                if (track.relevance >= 80) {
                    relevanceFill.style.backgroundColor = '#4CAF50'; // Green
                } else if (track.relevance >= 60) {
                    relevanceFill.style.backgroundColor = '#8BC34A'; // Light green
                } else if (track.relevance >= 40) {
                    relevanceFill.style.backgroundColor = '#FFC107'; // Amber
                } else {
                    relevanceFill.style.backgroundColor = '#FF9800'; // Orange
                }
                
                relevanceBar.appendChild(relevanceFill);
                relevanceContainer.appendChild(relevanceBar);
                
                matchInfo.appendChild(relevanceContainer);
            }
            
            songInfo.appendChild(matchInfo);
            
            // Add song info to song card
            songCard.appendChild(songInfo);
            
            // Create action buttons container
            const actionButtons = document.createElement('div');
            actionButtons.className = 'action-buttons';
            
            // Create Spotify button
            const spotifyButton = document.createElement('a');
            spotifyButton.className = 'spotify-button';
            spotifyButton.href = track.spotify_url || '#';
            spotifyButton.target = '_blank';
            spotifyButton.innerHTML = '<i class="fab fa-spotify"></i> Open';
            actionButtons.appendChild(spotifyButton);
            
            // Add action buttons to song card
            songCard.appendChild(actionButtons);
            
            // Add song card to songs container
            songsContainer.appendChild(songCard);
        });
        
        // Show the recommendations container
        recommendationsContainer.style.display = 'block';
    }

    function playSongPreview(previewUrl, button) {
        const audioPlayer = document.getElementById('audioPlayer');
        
        // If the same song is clicked again, toggle play/pause
        if (audioPlayer.src === previewUrl && !audioPlayer.paused) {
            audioPlayer.pause();
            button.innerHTML = '<i class="fas fa-play"></i>';
            button.classList.remove('playing');
            return;
        }
        
        // Reset all play buttons
        const allPlayButtons = document.querySelectorAll('.play-button');
        allPlayButtons.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-play"></i>';
            btn.classList.remove('playing');
        });
        
        // Set the new source and play
        audioPlayer.src = previewUrl;
        audioPlayer.play()
            .then(() => {
                button.innerHTML = '<i class="fas fa-pause"></i>';
                button.classList.add('playing');
                
                // When audio ends, reset the button
                audioPlayer.onended = function() {
                    button.innerHTML = '<i class="fas fa-play"></i>';
                    button.classList.remove('playing');
                };
            })
            .catch(error => {
                console.error('Error playing audio:', error);
                button.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-play"></i>';
                }, 2000);
            });
    }

    function isLightColor(color) {
        // Convert hex to RGB
        let r, g, b;

        if (color.startsWith('#')) {
            // Hex color
            const hex = color.substring(1);
            r = parseInt(hex.substr(0, 2), 16);
            g = parseInt(hex.substr(2, 2), 16);
            b = parseInt(hex.substr(4, 2), 16);
        } else if (color.startsWith('rgb')) {
            // RGB color
            const rgb = color.match(/\d+/g);
            r = parseInt(rgb[0]);
            g = parseInt(rgb[1]);
            b = parseInt(rgb[2]);
        } else {
            // Default to dark
            return false;
        }

        // Calculate luminance
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance > 0.5;
    }
});

// Add a subtle animation to the analyze button when it becomes enabled
const analyzeBtn = document.getElementById('analyzeBtn');
if (analyzeBtn) {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'disabled' && !analyzeBtn.disabled) {
                analyzeBtn.classList.add('pulse');
                setTimeout(() => {
                    analyzeBtn.classList.remove('pulse');
                }, 1500);
            }
        });
    });
    
    observer.observe(analyzeBtn, { attributes: true });
}
