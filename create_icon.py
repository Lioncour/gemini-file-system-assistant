#!/usr/bin/env python3
"""
Create a custom icon for the AI File System Assistant.
This script generates an ICO file with a modern design.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a custom icon for the application."""
    
    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors for FloKroll Projects theme
    # Modern blue gradient theme
    primary_blue = (59, 130, 246)      # Blue-500
    secondary_blue = (37, 99, 235)     # Blue-600
    accent_blue = (29, 78, 216)        # Blue-700
    light_blue = (147, 197, 253)       # Blue-300
    white = (255, 255, 255)
    dark_gray = (31, 41, 55)           # Gray-800
    
    # Create gradient background circle
    center = size // 2
    radius = 100
    
    # Draw outer circle with gradient effect
    for i in range(radius, 0, -2):
        alpha = int(255 * (1 - i / radius) * 0.8)
        color = (*primary_blue, alpha)
        draw.ellipse([center - i, center - i, center + i, center + i], 
                    fill=color, outline=None)
    
    # Draw inner circle
    inner_radius = 80
    draw.ellipse([center - inner_radius, center - inner_radius, 
                 center + inner_radius, center + inner_radius], 
                fill=secondary_blue, outline=accent_blue, width=3)
    
    # Draw file/folder icon elements
    # Main folder shape
    folder_width = 60
    folder_height = 45
    folder_x = center - folder_width // 2
    folder_y = center - folder_height // 2 - 10
    
    # Folder base
    draw.rounded_rectangle([folder_x, folder_y + 8, 
                           folder_x + folder_width, folder_y + folder_height], 
                          radius=4, fill=white, outline=dark_gray, width=2)
    
    # Folder tab
    tab_width = 20
    tab_height = 8
    tab_x = folder_x + 5
    tab_y = folder_y
    draw.rounded_rectangle([tab_x, tab_y, tab_x + tab_width, tab_y + tab_height], 
                          radius=2, fill=white, outline=dark_gray, width=2)
    
    # AI/Neural network elements
    # Draw small circles representing AI nodes
    node_positions = [
        (center - 25, center - 25),  # Top left
        (center + 25, center - 25),  # Top right
        (center - 25, center + 25),  # Bottom left
        (center + 25, center + 25),  # Bottom right
        (center, center - 35),       # Top center
        (center, center + 35),       # Bottom center
    ]
    
    for pos in node_positions:
        draw.ellipse([pos[0] - 3, pos[1] - 3, pos[0] + 3, pos[1] + 3], 
                    fill=light_blue, outline=accent_blue, width=1)
    
    # Draw connections between nodes
    connections = [
        (node_positions[0], node_positions[1]),  # Top row
        (node_positions[1], node_positions[3]),  # Right side
        (node_positions[3], node_positions[2]),  # Bottom row
        (node_positions[2], node_positions[0]),  # Left side
        (node_positions[4], node_positions[0]),  # Top connections
        (node_positions[4], node_positions[1]),
        (node_positions[5], node_positions[2]),  # Bottom connections
        (node_positions[5], node_positions[3]),
    ]
    
    for start, end in connections:
        draw.line([start[0], start[1], end[0], end[1]], 
                 fill=light_blue, width=2)
    
    # Add "F" for FloKroll in the center
    try:
        # Try to use a system font
        font_size = 32
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "F" in the center
    text = "F"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = center - text_width // 2
    text_y = center - text_height // 2 + 5
    
    # Draw text with shadow
    draw.text((text_x + 1, text_y + 1), text, font=font, fill=dark_gray)
    draw.text((text_x, text_y), text, font=font, fill=white)
    
    # Save as ICO file
    ico_path = "ai_assistant_icon.ico"
    img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print(f"✅ Icon created successfully: {ico_path}")
    return ico_path

if __name__ == "__main__":
    try:
        icon_path = create_icon()
        print(f"🎨 Custom icon created: {icon_path}")
        print("The icon features:")
        print("- Modern blue gradient background")
        print("- File/folder representation")
        print("- AI neural network elements")
        print("- FloKroll 'F' branding")
        print("- Professional, clean design")
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        print("Creating a simple fallback icon...")
        
        # Create a simple fallback icon
        img = Image.new('RGBA', (256, 256), (59, 130, 246, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 50, 206, 206], fill=(255, 255, 255, 255))
        draw.text((100, 100), "F", fill=(59, 130, 246, 255))
        img.save("ai_assistant_icon.ico", format='ICO')
        print("✅ Fallback icon created")

