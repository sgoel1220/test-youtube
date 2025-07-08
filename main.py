import json
import tempfile
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    afx
)


def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


def mirror_image_with_pil(image_path):
    img = Image.open(image_path).convert("RGBA")
    mirrored = ImageOps.mirror(img)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    mirrored.save(temp_file.name, "PNG")
    return temp_file.name


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

    # Split into lines
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

    # Draw text with outline
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

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name, "PNG")
    return temp_file.name


def create_background(bg_path, duration, size):
    return (ImageClip(bg_path)
            .set_duration(duration)
            .resize(size)
            .set_position("center"))


def create_scene(image_path, start_time, duration, size, text, side, rotate=True):
    def char_position(t):
        if side == "left":
            return (size[0] // 2 - 550, size[1] // 2 - 200)
        else:
            return (size[0] // 2 - 200, size[1] // 2 - 80)

    if side == "right" and rotate:
        image_path = mirror_image_with_pil(image_path)

    char_clip = (ImageClip(image_path)
                 .set_start(start_time)
                 .set_duration(duration)
                 .resize(height=size[1] // 2)
                 .set_position(char_position))

    text_img_path = generate_text_image(text, align="center")
    text_clip = (ImageClip(text_img_path, transparent=True)
                 .set_start(start_time)
                 .set_duration(duration)
                 .set_position(("center", 100)))

    return [char_clip, text_clip]


def build_video(config):
    canvas_size = tuple(config.get("canvas_size", [720, 1280]))
    fps = config.get("fps", 24)
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_folder, f"{timestamp}.mp4")

    duration = max(c["start_time"] + c["duration"] for c in config["characters"])
    bg = create_background(config["background"], duration, canvas_size)

    scenes = []
    for c in config["characters"]:
        scene_clips = create_scene(
            image_path=c["image"],
            start_time=c["start_time"],
            duration=c["duration"],
            size=canvas_size,
            text=c.get("text", ""),
            side=c.get("side", "left"),
            rotate=c.get("rotate", True)
        )
        scenes.extend(scene_clips)

    video = CompositeVideoClip([bg] + scenes, size=canvas_size)

    music_path = config.get("music")
    if music_path:
        audio = AudioFileClip(music_path)
        if audio.duration < video.duration:
            audio = afx.audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
        video = video.set_audio(audio)

    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac"
    )


if __name__ == "__main__":
    config = load_config("config.json")
    build_video(config)