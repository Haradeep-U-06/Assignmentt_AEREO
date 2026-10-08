from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import urllib.request

CERTIFICATE_DIR = "generated_certificates"
FONTS_DIR = "fonts"
os.makedirs(CERTIFICATE_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Font URLs
FONTS = {
    "title": "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf",
    "name": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "body": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "signature": "https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf"
}

def get_font(font_key: str, size: int) -> ImageFont.FreeTypeFont:
    font_path = os.path.join(FONTS_DIR, f"{font_key}.ttf")
    if not os.path.exists(font_path):
        try:
            print(f"Downloading font {font_key}...")
            urllib.request.urlretrieve(FONTS[font_key], font_path)
        except Exception as e:
            print(f"Error downloading font: {e}")
            return ImageFont.load_default(size=size) if hasattr(ImageFont, 'load_default') else ImageFont.load_default()
    
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default(size=size) if hasattr(ImageFont, 'load_default') else ImageFont.load_default()

def create_certificate_template():
    template_path = "template.jpg"
    
    # Always recreate for now to ensure we have the best version
    WIDTH, HEIGHT = 1600, 1100
    img = Image.new('RGB', (WIDTH, HEIGHT), color="#FDFBF7") # Warm off-white
    draw = ImageDraw.Draw(img)
    
    # Outer Border (Gold)
    draw.rectangle([40, 40, WIDTH-40, HEIGHT-40], outline="#C5A059", width=2)
    # Inner Border (Navy)
    draw.rectangle([55, 55, WIDTH-55, HEIGHT-55], outline="#1E293B", width=8)
    
    # Corner Accents
    accent_color = "#C5A059"
    for x_mod, y_mod in [(1,1), (-1,1), (1,-1), (-1,-1)]:
        x = 55 if x_mod == 1 else WIDTH-55
        y = 55 if y_mod == 1 else HEIGHT-55
        # Draw little squares at corners
        draw.rectangle([x - 10, y - 10, x + 10, y + 10], fill="#FDFBF7", outline=accent_color, width=3)

    # Header text
    font_title = get_font("title", 72)
    title_text = "CERTIFICATE OF COMPLETION"
    # Center title
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 140), title_text, fill="#1E293B", font=font_title)
    
    # Subtitle
    font_sub = get_font("body", 24)
    sub_text = "THIS IS PROUDLY PRESENTED TO"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 280), sub_text, fill="#64748B", font=font_sub)
    
    # Bottom Logos / Badges space
    # Draw a simple seal in the bottom center
    seal_r = 60
    seal_x, seal_y = WIDTH/2, HEIGHT - 180
    draw.ellipse([seal_x - seal_r, seal_y - seal_r, seal_x + seal_r, seal_y + seal_r], fill="#C5A059")
    draw.ellipse([seal_x - seal_r + 5, seal_y - seal_r + 5, seal_x + seal_r - 5, seal_y + seal_r - 5], outline="#FDFBF7", width=2)
    
    # Signatures lines
    sig_font = get_font("body", 18)
    # Left Signature
    draw.line([300, HEIGHT - 200, 600, HEIGHT - 200], fill="#1E293B", width=2)
    draw.text((400, HEIGHT - 190), "AUTHORIZED SIGNATURE", fill="#64748B", font=sig_font)
    
    # Right Signature
    draw.line([WIDTH - 600, HEIGHT - 200, WIDTH - 300, HEIGHT - 200], fill="#1E293B", width=2)
    draw.text((WIDTH - 500, HEIGHT - 190), "DATE ISSUED", fill="#64748B", font=sig_font)

    img.save(template_path, quality=95)
    return template_path

def generate_certificate(recipient_name: str, course_name: str) -> str:
    template_path = create_certificate_template()
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    WIDTH, HEIGHT = 1600, 1100
    
    if "FAIL" in recipient_name:
        raise ValueError("Simulated failure for recipient")

    # Draw Recipient Name
    font_name = get_font("name", 100)
    bbox = draw.textbbox((0, 0), recipient_name, font=font_name)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 400), recipient_name, fill="#C5A059", font=font_name)
    
    # Draw "for successfully completing"
    font_body = get_font("body", 28)
    body_text = "for successfully completing the course"
    bbox = draw.textbbox((0, 0), body_text, font=font_body)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 580), body_text, fill="#64748B", font=font_body)
    
    # Draw Course Name
    font_course = get_font("title", 50)
    bbox = draw.textbbox((0, 0), course_name.upper(), font=font_course)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) / 2, 660), course_name.upper(), fill="#1E293B", font=font_course)
    
    # Add dummy signature
    font_sig = get_font("signature", 60)
    draw.text((380, HEIGHT - 260), "Sign", fill="#1E293B", font=font_sig)
    
    # Add date
    from datetime import datetime
    date_str = datetime.now().strftime("%B %d, %Y")
    font_date = get_font("signature", 48)
    draw.text((WIDTH - 520, HEIGHT - 250), date_str, fill="#1E293B", font=font_date)
    
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(CERTIFICATE_DIR, filename)
    img.save(filepath, quality=95)
    return filepath
