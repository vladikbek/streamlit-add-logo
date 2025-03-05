import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImagePath
import numpy as np
import io
from sklearn.cluster import KMeans
import os
import xml.etree.ElementTree as ET
import re

def resize_image(image, target_size=3000):
    """Resize image to target_size x target_size without stretching"""
    width, height = image.size
    
    # Calculate the scaling factor to make the smaller dimension equal to target_size
    scale = max(target_size / width, target_size / height)
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # Create a new blank image with target dimensions
    new_image = Image.new("RGBA" if resized_image.mode == 'RGBA' else "RGB", (target_size, target_size), (255, 255, 255))
    
    # Calculate position to paste (center the image)
    paste_x = (target_size - new_width) // 2
    paste_y = (target_size - new_height) // 2
    
    # Paste the resized image onto the blank canvas
    new_image.paste(resized_image, (paste_x, paste_y))
    
    return new_image

def get_dominant_color(image, n_colors=5):
    """Extract dominant colors from image using K-means clustering"""
    # Convert image to numpy array of RGB values
    img_array = np.array(image.convert('RGB'))
    
    # Reshape the array to be a list of RGB pixels
    pixels = img_array.reshape(-1, 3)
    
    # Sample pixels to speed up processing for large images
    sample_size = min(10000, len(pixels))
    sampled_pixels = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(sampled_pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Return the most dominant color (first cluster center)
    return tuple(colors[0])

def create_hop_logo(color, size=(300, 300)):
    """Create a hop logo with the specified color and size"""
    # Create a transparent image
    logo = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Get the width and height
    width, height = size
    
    # Create a more accurate representation of the hop logo using paths
    # This is based on the SVG path data from the original hop.svg
    
    # Scale the coordinates to fit the desired size
    scale_x = width / 300
    scale_y = height / 300
    
    # Main outer shape
    outer_shape = [
        # Top left corner
        (59.084 * scale_x, 13.5652 * scale_y),
        # Top edge to right corner
        (239.084 * scale_x, 13.5652 * scale_y),
        # Right edge down to first indent
        (239.084 * scale_x, 47.258 * scale_y),
        # Right indent
        (252.67 * scale_x, 47.258 * scale_y),
        (252.67 * scale_x, 60.8232 * scale_y),
        (286.414 * scale_x, 60.8232 * scale_y),
        (286.414 * scale_x, 74.3884 * scale_y),
        (286.414 * scale_x, 108.081 * scale_y),
        (286.414 * scale_x, 121.646 * scale_y),
        (252.67 * scale_x, 121.646 * scale_y),
        (239.084 * scale_x, 121.646 * scale_y),
        (239.084 * scale_x, 135.212 * scale_y),
        (239.084 * scale_x, 164.788 * scale_y),
        (239.084 * scale_x, 178.354 * scale_y),
        (252.67 * scale_x, 178.354 * scale_y),
        (286.414 * scale_x, 178.354 * scale_y),
        (286.414 * scale_x, 191.919 * scale_y),
        (286.414 * scale_x, 225.612 * scale_y),
        (286.414 * scale_x, 239.177 * scale_y),
        (253.35 * scale_x, 239.177 * scale_y),
        (243.743 * scale_x, 243.15 * scale_y),
        (239.084 * scale_x, 253.421 * scale_y),
        (239.084 * scale_x, 286.435 * scale_y),
        (225.498 * scale_x, 300 * scale_y),
        (132.67 * scale_x, 300 * scale_y),
        (119.084 * scale_x, 286.435 * scale_y),
        (119.084 * scale_x, 252.742 * scale_y),
        (105.498 * scale_x, 239.177 * scale_y),
        (13.5859 * scale_x, 239.177 * scale_y),
        (0 * scale_x, 225.612 * scale_y),
        (0 * scale_x, 74.3884 * scale_y),
        (13.5859 * scale_x, 60.8232 * scale_y),
        (45.498 * scale_x, 60.8232 * scale_y),
        (59.084 * scale_x, 47.258 * scale_y),
        # Back to start
        (59.084 * scale_x, 13.5652 * scale_y),
    ]
    
    # Inner shapes (the holes in the logo)
    inner_shape1 = [
        (180 * scale_x, 192.834 * scale_y),
        (180 * scale_x, 225.612 * scale_y),
        (193.586 * scale_x, 239.177 * scale_y),
        (227.069 * scale_x, 239.177 * scale_y),
        (235.565 * scale_x, 235.663 * scale_y),
        (239.084 * scale_x, 227.181 * scale_y),
        (239.084 * scale_x, 192.834 * scale_y),
        (225.498 * scale_x, 179.268 * scale_y),
        (193.586 * scale_x, 179.268 * scale_y),
        (180 * scale_x, 192.834 * scale_y),
    ]
    
    inner_shape2 = [
        (119.084 * scale_x, 135.212 * scale_y),
        (119.084 * scale_x, 164.788 * scale_y),
        (132.67 * scale_x, 178.354 * scale_y),
        (164.582 * scale_x, 178.354 * scale_y),
        (178.168 * scale_x, 164.788 * scale_y),
        (178.168 * scale_x, 135.212 * scale_y),
        (164.582 * scale_x, 121.646 * scale_y),
        (132.67 * scale_x, 121.646 * scale_y),
        (119.084 * scale_x, 135.212 * scale_y),
    ]
    
    # Draw the shapes
    draw.polygon(outer_shape, fill=(*color, 255))
    draw.polygon(inner_shape1, fill=(0, 0, 0, 0))
    draw.polygon(inner_shape2, fill=(0, 0, 0, 0))
    
    return logo

def add_logo_to_image(image, logo, spacing=100):
    """Add logo to bottom right of image with specified spacing"""
    # Ensure image has alpha channel
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Calculate position for logo
    position = (image.width - logo.width - spacing, image.height - logo.height - spacing)
    
    # Create a copy of the image
    result = image.copy()
    
    # Paste logo onto image, using the logo's alpha channel as mask
    result.paste(logo, position, logo)
    
    return result

def main():
    st.title("Image Processor with Logo")
    st.write("Upload an image to resize it to 3000x3000 and add the Hop logo")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Load the image
        image = Image.open(uploaded_file)
        
        # Display original image
        st.subheader("Original Image")
        st.image(image, use_column_width=True)
        
        # Resize image
        with st.spinner("Resizing image..."):
            resized_image = resize_image(image)
        
        # Get dominant color
        with st.spinner("Extracting dominant color..."):
            dominant_color = get_dominant_color(resized_image)
            st.write(f"Dominant color: RGB{dominant_color}")
            
            # Display color sample
            color_sample = Image.new("RGB", (100, 100), dominant_color)
            st.image(color_sample, width=100, caption="Dominant Color")
        
        # Create logo with dominant color
        with st.spinner("Preparing logo..."):
            logo = create_hop_logo(dominant_color)
        
        # Add logo to image
        with st.spinner("Adding logo..."):
            final_image = add_logo_to_image(resized_image, logo)
        
        # Display final image
        st.subheader("Processed Image")
        st.image(final_image, use_column_width=True)
        
        # Allow downloading the processed image
        buf = io.BytesIO()
        final_image.save(buf, format="PNG")
        st.download_button(
            label="Download Processed Image",
            data=buf.getvalue(),
            file_name="processed_image.png",
            mime="image/png"
        )

if __name__ == "__main__":
    main() 