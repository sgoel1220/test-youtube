import json
import os
import tempfile
import shutil
from datetime import datetime
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from video_editor import VideoEditor
from video_utils import mirror_image, generate_text_image
from PIL import Image
import numpy as np

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    config = load_config("config.json")

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_folder, f"{timestamp}.mp4")

    pre_processed_dir = os.path.join(output_folder, "pre_processed")
    if not os.path.exists(pre_processed_dir):
        os.makedirs(pre_processed_dir)

    # Process characters to handle image paths and temporary files
    processed_characters = []
    image_counter = 0
    for char_config in config["characters"]:
        original_char_image_path = char_config["image"]
        text = char_config.get("text", "")
        side = char_config.get("side", "left")
        rotate = char_config.get("rotate", True)

        # Handle character image mirroring
        char_image = Image.open(original_char_image_path).convert("RGBA")
        if side == "right" and rotate:
            char_image = mirror_image(char_image)

        char_image_path_for_clip = os.path.join(pre_processed_dir, f"char_{image_counter}.png")
        char_image.save(char_image_path_for_clip, "PNG")

        # Handle text image generation
        text_img = generate_text_image(text, align="center")
        text_image_path_for_clip = os.path.join(pre_processed_dir, f"text_{image_counter}.png")
        text_img.save(text_image_path_for_clip, "PNG")
        image_counter += 1

        processed_characters.append({
            "image": np.array(Image.open(char_image_path_for_clip).convert("RGBA")),
            "text_image": np.array(Image.open(text_image_path_for_clip).convert("RGBA")),
            "start_time": char_config["start_time"],
            "duration": char_config["duration"],
            "side": side,
            "rotate": rotate
        })

    editor = VideoEditor(config, ImageClip_factory=ImageClip, AudioFileClip_factory=AudioFileClip, CompositeVideoClip_factory=CompositeVideoClip)
    final_video = editor.build_video(processed_characters)
    final_video.write_videofile(
        output_path,
        fps=editor.fps,
        codec="libx264",
        audio_codec="aac"
    )

    
