import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import io
from sklearn.cluster import KMeans
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

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

def convert_svg_to_png(svg_path, color, output_size=(300, 300)):
    """Convert SVG to PNG with specified color"""
    # Read the SVG file
    with open(svg_path, 'r') as f:
        svg_content = f.read()
    
    # Replace black with the specified color
    color_hex = "#{:02x}{:02x}{:02x}".format(*color)
    svg_content = svg_content.replace('fill="black"', f'fill="{color_hex}"')
    
    # Write the modified SVG to a temporary file
    temp_svg_path = "temp_colored.svg"
    with open(temp_svg_path, 'w') as f:
        f.write(svg_content)
    
    # Convert SVG to PNG using svglib and reportlab
    drawing = svg2rlg(temp_svg_path)
    
    # Create a BytesIO object to hold the PNG data
    png_data = io.BytesIO()
    renderPM.drawToFile(drawing, png_data, fmt="PNG")
    png_data.seek(0)
    
    # Create PIL Image from PNG data
    img = Image.open(png_data)
    
    # Resize to desired output size
    if img.size != output_size:
        img = img.resize(output_size, Image.LANCZOS)
    
    # Clean up temporary file
    os.remove(temp_svg_path)
    
    return img

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
        
        # Convert SVG to PNG with dominant color
        with st.spinner("Preparing logo..."):
            logo_path = "hop.svg"
            logo = convert_svg_to_png(logo_path, dominant_color)
        
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