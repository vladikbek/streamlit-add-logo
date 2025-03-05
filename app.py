import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from sklearn.cluster import KMeans
import base64

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

def create_colored_logo(color, size=(300, 300)):
    """Create a colored logo image using PIL."""
    # Create a transparent background
    logo = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Draw a more accurate representation of the HOP logo
    # Based on the SVG path but simplified for PIL
    
    # Main outer shape - rounded rectangle
    padding = 20
    radius = 30
    
    # Draw the main shape with the accent color
    # Top-left corner
    draw.pieslice([padding, padding, padding + 2 * radius, padding + 2 * radius], 
                  180, 270, fill=color + (255,))
    # Top-right corner
    draw.pieslice([size[0] - padding - 2 * radius, padding, 
                  size[0] - padding, padding + 2 * radius], 
                  270, 0, fill=color + (255,))
    # Bottom-right corner
    draw.pieslice([size[0] - padding - 2 * radius, size[1] - padding - 2 * radius, 
                  size[0] - padding, size[1] - padding], 
                  0, 90, fill=color + (255,))
    # Bottom-left corner
    draw.pieslice([padding, size[1] - padding - 2 * radius, 
                  padding + 2 * radius, size[1] - padding], 
                  90, 180, fill=color + (255,))
    
    # Rectangles to connect the corners
    draw.rectangle([padding + radius, padding, size[0] - padding - radius, padding + radius], 
                  fill=color + (255,))  # Top
    draw.rectangle([size[0] - padding - radius, padding + radius, 
                   size[0] - padding, size[1] - padding - radius], 
                  fill=color + (255,))  # Right
    draw.rectangle([padding + radius, size[1] - padding - radius, 
                   size[0] - padding - radius, size[1] - padding], 
                  fill=color + (255,))  # Bottom
    draw.rectangle([padding, padding + radius, 
                   padding + radius, size[1] - padding - radius], 
                  fill=color + (255,))  # Left
    
    # Fill the center
    draw.rectangle([padding + radius, padding + radius, 
                   size[0] - padding - radius, size[1] - padding - radius], 
                  fill=color + (255,))
    
    # Inner cutout for the "H" shape
    inner_padding = 80
    inner_size = 80
    draw.rectangle([inner_padding, inner_padding, 
                   inner_padding + inner_size, inner_padding + inner_size], 
                  fill=(0, 0, 0, 0))
    
    # Inner cutout for the "O" shape
    draw.ellipse([size[0] - inner_padding - inner_size, size[1] - inner_padding - inner_size, 
                 size[0] - inner_padding, size[1] - inner_padding], 
                fill=(0, 0, 0, 0))
    
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