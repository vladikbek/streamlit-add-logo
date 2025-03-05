# Image Processor with Logo

A Streamlit app that processes images by:
1. Resizing them to 3000x3000 pixels (without stretching)
2. Adding the Hop logo to the bottom right corner
3. Matching the logo color to the dominant color in the image

## Features

- Upload JPG or PNG images
- Automatic resizing to 3000x3000 (preserving aspect ratio)
- Logo placement with 100px spacing from bottom and right edges
- Color matching between logo and image
- Download processed images

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Open your web browser to the URL displayed in the terminal (typically http://localhost:8501)
3. Upload an image using the file uploader
4. View the processed image and download it if desired

## Requirements

- Python 3.7+
- Streamlit
- Pillow
- NumPy
- scikit-learn
- CairoSVG

## Note

The app requires the `hop.svg` file to be in the same directory as `app.py`. 