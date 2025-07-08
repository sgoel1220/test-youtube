import json
import os
import tempfile
import shutil
from datetime import datetime
from video_editor import VideoEditor
from video_utils import mirror_image, generate_text_image
from PIL import Image

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

    temp_dir = None
    try:
        # Create a temporary directory for image assets
        temp_dir = tempfile.mkdtemp()

        # Process characters to handle image paths and temporary files
        processed_characters = []
        for char_config in config["characters"]:
            original_char_image_path = char_config["image"]
            text = char_config.get("text", "")
            side = char_config.get("side", "left")
            rotate = char_config.get("rotate", True)

            # Handle character image mirroring and temporary file creation
            char_image = Image.open(original_char_image_path).convert("RGBA")
            if side == "right" and rotate:
                char_image = mirror_image(char_image)

            temp_char_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=temp_dir)
            char_image.save(temp_char_file.name, "PNG")
            char_image_path_for_clip = temp_char_file.name
            temp_char_file.close()

            # Handle text image generation and temporary file creation
            text_img = generate_text_image(text, align="center")
            temp_text_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=temp_dir)
            text_img.save(temp_text_file.name, "PNG")
            text_image_path_for_clip = temp_text_file.name
            temp_text_file.close()

            processed_characters.append({
                "image_path": char_image_path_for_clip,
                "text_image_path": text_image_path_for_clip,
                "start_time": char_config["start_time"],
                "duration": char_config["duration"],
                "side": side,
                "rotate": rotate
            })

        editor = VideoEditor(config)
        final_video = editor.build_video(processed_characters)
        final_video.write_videofile(
            output_path,
            fps=editor.fps,
            codec="libx264",
            audio_codec="aac"
        )

    finally:
        # Clean up temporary directory and its contents
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
