import pytest
from PIL import Image, ImageOps
import os
import tempfile
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, afx, ColorClip

# Assuming video_utils.py is in the same directory or accessible via PYTHONPATH
from video_utils import mirror_image, generate_text_image, create_background_clip, get_char_position, create_scene_clips

# Helper function to create a dummy image for testing
@pytest.fixture
def dummy_image_path():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        img = Image.new('RGB', (100, 100))
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                pixels[x, y] = (x % 256, y % 256, (x + y) % 256) # Create a gradient image
        img.save(tmpfile.name)
    yield tmpfile.name
    os.remove(tmpfile.name)

# Test for mirror_image function
def test_mirror_image(dummy_image_path):
    original_image = Image.open(dummy_image_path)
    mirrored_image = mirror_image(original_image)

    assert isinstance(mirrored_image, Image.Image)
    assert mirrored_image.size == original_image.size
    # A simple check to see if mirroring had an effect (e.g., not identical to original)
    # This might need more robust checks depending on the image content
    assert list(original_image.getdata()) != list(mirrored_image.getdata())

# Test for generate_text_image function
def test_generate_text_image():
    text = "Hello World"
    img = generate_text_image(text)
    assert isinstance(img, Image.Image)
    assert img.size == (800, 200)
    assert img.mode == "RGBA"

    # Test with custom parameters
    img_custom = generate_text_image("Test", width=400, height=100, font_size=30, font_color="blue", outline_color="red")
    assert isinstance(img_custom, Image.Image)
    assert img_custom.size == (400, 100)

# Test for create_background_clip function
def test_create_background_clip(dummy_image_path):
    duration = 10
    size = (1920, 1080)
    clip = create_background_clip(dummy_image_path, duration, size, ImageClip, ColorClip)

    assert isinstance(clip, CompositeVideoClip)
    assert clip.duration == duration
    assert clip.size == size

# Test for get_char_position function
def test_get_char_position():
    size = (1920, 1080)
    left_pos = get_char_position("left", size)
    right_pos = get_char_position("right", size)

    assert left_pos == (size[0] // 2 - 550, size[1] // 2 - 200)
    assert right_pos == (size[0] // 2 - 200, size[1] // 2 - 80)

# Test for create_scene_clips function
def test_create_scene_clips(dummy_image_path):
    start_time = 0
    duration = 5
    size = (1920, 1080)
    side = "left"

    clips = create_scene_clips(dummy_image_path, dummy_image_path, start_time, duration, size, side, ImageClip)

    assert isinstance(clips, list)
    assert len(clips) == 2
    assert all(isinstance(c, ImageClip) for c in clips)

    char_clip = clips[0]
    text_clip = clips[1]

    assert char_clip.start == start_time
    assert char_clip.duration == duration
    assert char_clip.size[1] == size[1] // 2 # height should be half of scene height
    assert char_clip.pos(0) == get_char_position(side, size)

    assert text_clip.start == start_time
    assert text_clip.duration == duration
    assert text_clip.pos(0) == ("center", 100)
