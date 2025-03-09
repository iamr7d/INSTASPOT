const { createClient } = require('@netlify/functions');
const fetch = require('node-fetch');
const FormData = require('form-data');
const multipart = require('parse-multipart-data');

// Replace with your actual backend API URL
const BACKEND_API_URL = 'https://your-backend-api-url.com/analyze';

exports.handler = async (event, context) => {
  try {
    // Only allow POST requests
    if (event.httpMethod !== 'POST') {
      return {
        statusCode: 405,
        body: JSON.stringify({ error: 'Method Not Allowed' }),
      };
    }

    // Parse the multipart form data to get the image
    const boundary = multipart.getBoundary(event.headers['content-type']);
    const parts = multipart.parse(Buffer.from(event.body, 'base64'), boundary);
    const imagePart = parts.find(part => part.name === 'image');

    if (!imagePart) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'No image provided' }),
      };
    }

    // Create a new form data to forward to the backend
    const formData = new FormData();
    formData.append('image', imagePart.data, {
      filename: imagePart.filename,
      contentType: imagePart.type,
    });

    // Forward the request to the backend API
    const response = await fetch(BACKEND_API_URL, {
      method: 'POST',
      body: formData,
      headers: {
        ...formData.getHeaders(),
      },
    });

    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}`);
    }

    const data = await response.json();

    // Return the response from the backend
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    };
  } catch (error) {
    console.error('Error in serverless function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error', message: error.message }),
    };
  }
};
