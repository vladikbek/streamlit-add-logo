import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImagePath
import numpy as np
import io
from sklearn.cluster import KMeans
import requests
import colorsys
import base64

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

def get_accent_color(image, n_colors=10):
    """Extract accent colors from image using K-means clustering and color analysis"""
    # Convert image to numpy array of RGB values
    img_array = np.array(image.convert('RGB'))
    
    # Reshape the array to be a list of RGB pixels
    pixels = img_array.reshape(-1, 3)
    
    # Sample pixels to speed up processing for large images
    sample_size = min(10000, len(pixels))
    sampled_pixels = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
    
    # Apply K-means clustering to find color clusters
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(sampled_pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Convert RGB to HSV for better color analysis
    hsv_colors = []
    for color in colors:
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hsv_colors.append((h, s, v, tuple(color)))
    
    # Filter for vibrant colors (high saturation and value, but not too bright)
    vibrant_colors = []
    for h, s, v, rgb in hsv_colors:
        # Look for colors with high saturation and good brightness
        if s > 0.4 and 0.3 < v < 0.9:
            # Calculate a "vibrancy" score
            vibrancy = s * v
            vibrant_colors.append((vibrancy, rgb))
    
    # If we found vibrant colors, return the most vibrant one
    if vibrant_colors:
        vibrant_colors.sort(reverse=True)  # Sort by vibrancy score
        return vibrant_colors[0][1]  # Return the RGB of the most vibrant color
    
    # Fallback: If no vibrant colors found, find the most colorful one
    # (avoiding very dark or very bright colors)
    filtered_colors = []
    for color in colors:
        r, g, b = color
        # Avoid very dark or very bright colors
        brightness = (r + g + b) / 3
        if 30 < brightness < 230:
            # Calculate color variance as a measure of "colorfulness"
            variance = np.var([r, g, b])
            filtered_colors.append((variance, tuple(color)))
    
    if filtered_colors:
        filtered_colors.sort(reverse=True)  # Sort by variance
        return filtered_colors[0][1]  # Return the most "colorful" color
    
    # If all else fails, return the first color from kmeans
    return tuple(colors[0])

def download_svg_from_url(url):
    """Download SVG content from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except Exception as e:
        st.error(f"Error downloading SVG: {e}")
        return None

def create_colored_svg(svg_content, color):
    """Replace black color in SVG with the specified color"""
    if svg_content:
        # Convert RGB to hex
        color_hex = "#{:02x}{:02x}{:02x}".format(*color)
        # Replace black with the specified color
        # This assumes the SVG uses fill="black" for the main shape
        colored_svg = svg_content.replace('fill="black"', f'fill="{color_hex}"')
        return colored_svg
    return None

def svg_to_png(svg_content, size=(300, 300)):
    """Convert SVG content to PNG using cairosvg or fallback to PIL"""
    if not svg_content:
        return None
    
    try:
        # Use cairosvg if available (better quality)
        try:
            import cairosvg
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size[0],
                output_height=size[1]
            )
            logo = Image.open(io.BytesIO(png_data))
        except ImportError:
            # Fallback to a simple generic shape
            logo = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(logo)
            
            # Draw a simple shape with the accent color
            width, height = size
            padding = width * 0.1  # 10% padding
            
            # Draw a rounded rectangle
            draw.rounded_rectangle(
                [(padding, padding), (width - padding, height - padding)],
                radius=width * 0.2,
                fill=(*color, 255)
            )
            
            # Add a simple inner circle
            center = width / 2
            radius = width * 0.25
            draw.ellipse(
                [(center - radius, center - radius), 
                 (center + radius, center + radius)],
                fill=(0, 0, 0, 0)
            )
    
    except Exception as e:
        st.error(f"Error processing SVG: {e}")
        return None
    
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
    
    # Convert back to RGB for JPG output
    if result.mode == 'RGBA':
        result = result.convert('RGB')
    
    return result

def main():
    st.title("Image Processor with Logo")
    st.write("Upload an image to resize it to 3000x3000 and add a logo")
    
    # Logo URL input
    logo_url = st.text_input("Enter logo URL (SVG format)", "https://houseofphonk.com/hop.svg")
    
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
        
        # Get accent color
        with st.spinner("Extracting accent color..."):
            accent_color = get_accent_color(resized_image)
            st.write(f"Accent color: RGB{accent_color}")
            
            # Display color sample
            color_sample = Image.new("RGB", (100, 100), accent_color)
            st.image(color_sample, width=100, caption="Accent Color")
        
        # Download and prepare logo
        with st.spinner("Preparing logo..."):
            # Download SVG from URL
            svg_content = download_svg_from_url(logo_url)
            
            if svg_content:
                # Create colored SVG
                colored_svg = create_colored_svg(svg_content, accent_color)
                
                # Convert SVG to PNG
                logo = svg_to_png(colored_svg)
                
                if logo is None:
                    st.error("Failed to process the logo. Using fallback method.")
                    # Fallback to a simple shape
                    logo = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(logo)
                    
                    # Draw a simple rounded rectangle with a hole
                    padding = 30  # 10% of 300
                    draw.rounded_rectangle(
                        [(padding, padding), (300 - padding, 300 - padding)],
                        radius=60,
                        fill=(*accent_color, 255)
                    )
                    
                    # Add a simple inner circle
                    center = 150
                    radius = 75
                    draw.ellipse(
                        [(center - radius, center - radius), 
                         (center + radius, center + radius)],
                        fill=(0, 0, 0, 0)
                    )
            else:
                st.error("Failed to download the logo. Using fallback method.")
                # Fallback to a simple shape
                logo = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
                draw = ImageDraw.Draw(logo)
                
                # Draw a simple rounded rectangle with a hole
                padding = 30  # 10% of 300
                draw.rounded_rectangle(
                    [(padding, padding), (300 - padding, 300 - padding)],
                    radius=60,
                    fill=(*accent_color, 255)
                )
                
                # Add a simple inner circle
                center = 150
                radius = 75
                draw.ellipse(
                    [(center - radius, center - radius), 
                     (center + radius, center + radius)],
                    fill=(0, 0, 0, 0)
                )
        
        # Add logo to image
        with st.spinner("Adding logo..."):
            final_image = add_logo_to_image(resized_image, logo)
        
        # Display final image
        st.subheader("Processed Image")
        st.image(final_image, use_column_width=True)
        
        # Allow downloading the processed image as JPG
        buf = io.BytesIO()
        final_image.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="Download Processed Image",
            data=buf.getvalue(),
            file_name="processed_image.jpg",
            mime="image/jpeg"
        )

if __name__ == "__main__":
    main() 