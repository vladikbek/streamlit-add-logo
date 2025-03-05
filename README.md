# Streamlit HOP Logo Image Processor

A simple Streamlit application that processes images by:
1. Resizing them to fit within a 3000x3000 canvas while maintaining aspect ratio
2. Extracting a bright accent color from the image
3. Adding a colored HOP logo to the bottom right corner
4. Providing a download option for the processed image

## Features

- Upload any image (JPG, JPEG, PNG)
- Automatic image resizing to 3000x3000 while maintaining aspect ratio
- Intelligent accent color extraction from the image
- Dynamic logo coloring based on the extracted accent color
- One-click download of the processed image

## How to Use

1. Upload an image using the file uploader
2. Wait for the image to be processed
3. View the processed image with the HOP logo added
4. Click the "Download Processed Image" link to save the result

## Technical Details

- Built with Streamlit, Pillow, and scikit-learn
- Uses K-means clustering to extract dominant colors
- Dynamically colors the SVG logo using cairosvg
- Maintains image quality throughout the processing

## Deployment

This app is designed to be deployed on Streamlit Cloud.

## Requirements

See `requirements.txt` for a list of dependencies. 