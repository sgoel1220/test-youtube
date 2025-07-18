import tempfile
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, afx, ColorClip, vfx
import numpy as np

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

def create_background_clip(bg_path, duration, size, ImageClip_factory, ColorClip_factory, blur_radius=0):
    # Load the background image
    bg_image_clip = ImageClip_factory(bg_path)

    # Calculate scaling to cover the canvas
    img_width, img_height = bg_image_clip.size
    canvas_width, canvas_height = size

    # Determine the scale factor to cover the canvas
    scale_factor = max(canvas_width / img_width, canvas_height / img_height)

    # Resize the image clip to cover the canvas
    resized_bg_image_clip = bg_image_clip.resize(width=int(img_width * scale_factor), height=int(img_height * scale_factor))

    # Crop the image to the canvas size after scaling
    final_bg_clip = (resized_bg_image_clip
                     .set_duration(duration)
                     .set_position("center")
                     .crop(x_center=resized_bg_image_clip.w / 2, y_center=resized_bg_image_clip.h / 2, width=canvas_width, height=canvas_height))

    # Apply blur if blur_radius is greater than 0
    if blur_radius > 0:
        def blur_frame(image):
            pil_image = Image.fromarray(image.astype('uint8'))
            blurred_pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            return np.array(blurred_pil_image)
        final_bg_clip = final_bg_clip.fl_image(blur_frame)

    return final_bg_clip

def create_outro_clip(img_path, duration, size, ImageClip_factory, ColorClip_factory, overlay_enabled=False, overlay_opacity=0.0):
    # Create a base black background clip of the canvas size
    base_clip = ColorClip_factory(size, color=(0, 0, 0), duration=duration)

    # Load the outro image
    outro_image_clip = ImageClip_factory(img_path)

    # Calculate new dimensions to fit within 'size' while maintaining aspect ratio
    img_width, img_height = outro_image_clip.size
    canvas_width, canvas_height = size

    aspect_ratio_img = img_width / img_height
    aspect_ratio_canvas = canvas_width / canvas_height

    if aspect_ratio_img > aspect_ratio_canvas:
        # Image is wider than canvas, fit by width
        new_width = canvas_width
        new_height = int(canvas_width / aspect_ratio_img)
    else:
        # Image is taller than canvas, fit by height
        new_height = canvas_height
        new_width = int(canvas_height * aspect_ratio_img)

    # Resize the image clip
    resized_outro_image_clip = outro_image_clip.resize((new_width, new_height))

    # Set duration and position (center) on the base clip
    final_outro_clip = (resized_outro_image_clip
                        .set_duration(duration)
                        .set_position("center"))

    # Composite the resized image onto the black base clip
    composed_clip = CompositeVideoClip([base_clip, final_outro_clip], size=size)

    if overlay_enabled:
        overlay_color = (0, 0, 0) # Black overlay
        overlay_clip = ColorClip(size, color=overlay_color, duration=duration).set_opacity(overlay_opacity)
        composed_clip = CompositeVideoClip([composed_clip, overlay_clip], size=size)

    return composed_clip


def get_char_position(side, size):
    if side == "left":
        return (size[0] // 2 - 550, size[1] // 2 - 200)
    else:
        return (size[0] // 2 - 200, size[1] // 2 - 80)

def create_scene_clips(char_image_path, text_image_path, start_time, duration, size, side, ImageClip_factory):
    char_clip = (ImageClip_factory(char_image_path)
                 .set_start(start_time)
                 .set_duration(duration)
                 .resize(height=size[1] // 2)
                 .set_position(get_char_position(side, size)))

    text_clip = (ImageClip_factory(text_image_path, transparent=True)
                 .set_start(start_time)
                 .set_duration(duration)
                 .set_position(("center", 100)))

    return [char_clip, text_clip]