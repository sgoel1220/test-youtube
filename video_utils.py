import tempfile
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, afx

def mirror_image(pil_image):
    mirrored = ImageOps.mirror(pil_image)
    return mirrored

def generate_text_image(text, width=800, height=200, font_size=60,
                        font_color="white", outline_color="black",
                        bg_color=(0, 0, 0, 0), align="center"):
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("assets/fonts/Anton-Regular.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    lines = []
    words = text.upper().split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font) <= width - 20:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    y = (height - (len(lines) * (font_size + 10))) // 2
    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = {
            "left": 10,
            "center": (width - line_width) // 2,
            "right": width - line_width - 10
        }.get(align, 10)

        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), line, font=font, fill=outline_color)

        draw.text((x, y), line, font=font, fill=font_color)
        y += font_size + 10

    return img

def create_background_clip(bg_path, duration, size):
    return (ImageClip(bg_path)
            .set_duration(duration)
            .resize(size)
            .set_position("center"))

def get_char_position(side, size):
    if side == "left":
        return (size[0] // 2 - 550, size[1] // 2 - 200)
    else:
        return (size[0] // 2 - 200, size[1] // 2 - 80)

def create_scene_clips(char_image_path, text_image_path, start_time, duration, size, side):
    char_clip = (ImageClip(char_image_path)
                 .set_start(start_time)
                 .set_duration(duration)
                 .resize(height=size[1] // 2)
                 .set_position(get_char_position(side, size)))

    text_clip = (ImageClip(text_image_path, transparent=True)
                 .set_start(start_time)
                 .set_duration(duration)
                 .set_position(("center", 100)))

    return [char_clip, text_clip]