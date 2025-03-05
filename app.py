import streamlit as st
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from sklearn.cluster import KMeans
import base64
import cairosvg

st.set_page_config(page_title="HOP Logo Adder", layout="wide")

# GitHub raw URL for the SVG logo
LOGO_URL = "https://raw.githubusercontent.com/vladikbek/streamlit-add-logo/main/hop.svg"

def get_accent_color(img):
    """Extract a bright accent color from the image."""
    # Resize image for faster processing
    img_small = img.resize((100, 100))
    # Convert to RGB if it's not
    if img_small.mode != 'RGB':
        img_small = img_small.convert('RGB')
    
    # Get image data as numpy array
    img_array = np.array(img_small)
    # Reshape for KMeans
    pixels = img_array.reshape(-1, 3)
    
    # Use KMeans to find dominant colors
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculate brightness for each color
    brightness = np.sum(colors, axis=1) / 3
    
    # Filter out dark colors (brightness < 100)
    bright_colors = colors[brightness > 100]
    
    # If no bright colors found, return the brightest one
    if len(bright_colors) == 0:
        return tuple(colors[np.argmax(brightness)])
    
    # Return the brightest color
    return tuple(bright_colors[np.argmax(np.sum(bright_colors, axis=1))])

def create_colored_logo(color):
    """Create a colored logo image using cairosvg."""
    # Download the SVG
    response = requests.get(LOGO_URL)
    if response.status_code != 200:
        st.error("Failed to download logo from GitHub")
        return None
    
    # Convert RGB color to hex
    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
    
    # Replace the fill color in the SVG
    svg_content = response.text.replace('fill="black"', f'fill="{hex_color}"')
    
    # Convert SVG to PNG using cairosvg
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), 
                               output_width=300, 
                               output_height=300)
    
    # Create PIL Image from PNG data
    logo = Image.open(BytesIO(png_data))
    
    return logo

def process_image(uploaded_file):
    """Process the uploaded image and add the logo."""
    # Open the uploaded image
    image = Image.open(uploaded_file)
    
    # Get the original aspect ratio
    width, height = image.size
    aspect_ratio = width / height
    
    # Calculate new dimensions for 3000x3000 canvas
    if aspect_ratio > 1:  # Wider than tall
        new_width = 3000
        new_height = int(3000 / aspect_ratio)
    else:  # Taller than wide
        new_height = 3000
        new_width = int(3000 * aspect_ratio)
    
    # Resize the image while maintaining aspect ratio
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # Create a 3000x3000 canvas with white background
    canvas = Image.new('RGB', (3000, 3000), (255, 255, 255))
    
    # Paste the resized image in the center of the canvas
    paste_x = (3000 - new_width) // 2
    paste_y = (3000 - new_height) // 2
    canvas.paste(resized_image, (paste_x, paste_y))
    
    # Get accent color from the image
    accent_color = get_accent_color(canvas)
    
    # Create a colored logo
    logo = create_colored_logo(accent_color)
    if not logo:
        return None
    
    # Calculate position for logo (100px from bottom and right)
    logo_position = (3000 - 300 - 100, 3000 - 300 - 100)
    
    # Paste the logo onto the canvas
    canvas.paste(logo, logo_position, logo)
    
    return canvas

def get_image_download_link(img, filename="processed_image.jpg", text="Download Processed Image"):
    """Generate a download link for the processed image."""
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def main():
    st.title("HOP Logo Image Processor")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Process the image
        with st.spinner("Processing image..."):
            processed_image = process_image(uploaded_file)
        
        if processed_image:
            # Display the processed image
            st.image(processed_image, caption="Processed Image", use_column_width=True)
            
            # Provide download link
            st.markdown(
                get_image_download_link(processed_image),
                unsafe_allow_html=True
            )
        else:
            st.error("Error processing the image. Please try again.")

if __name__ == "__main__":
    main() 