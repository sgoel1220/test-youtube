import pytest
from unittest.mock import MagicMock, patch, ANY
import numpy as np
from video_editor import VideoEditor
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

# Simple mock classes for MoviePy objects
class MockClip:
    def __init__(self, *args, **kwargs):
        self.start = 0
        self.duration = 0
        self.size = (100, 100) # Default size
        self.end = self.start + self.duration

    def set_start(self, start):
        self.start = start
        self.end = self.start + self.duration
        return self

    def set_duration(self, duration):
        self.duration = duration
        self.end = self.start + self.duration
        return self

    def resize(self, *args, **kwargs):
        return self

    def set_position(self, *args, **kwargs):
        return self

    def set_audio(self, audio_clip):
        self.audio = audio_clip
        return self

    def write_videofile(self, *args, **kwargs):
        pass

class MockImageClip:
    pass

class MockAudioFileClip(MockClip):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = 10 # Default duration for audio mock

class MockCompositeVideoClip(MockClip):
    def __init__(self, clips, size=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clips = clips
        self.size = size
        # Calculate duration based on sub-clips if available
        if clips and all(hasattr(c, 'end') for c in clips):
            self.duration = max(c.end for c in clips)
        else:
            self.duration = 0

# Mock video_utils functions
@pytest.fixture(autouse=True)
def mock_video_utils():
    with patch('video_editor.create_background_clip') as mock_create_background_clip, \
         patch('video_editor.get_char_position') as mock_get_char_position, \
         patch('video_editor.create_scene_clips') as mock_create_scene_clips:

        mock_create_background_clip.return_value = MockImageClip()
        mock_get_char_position.return_value = (0, 0)
        mock_create_scene_clips.return_value = [MockImageClip(), MockImageClip()]

        yield mock_create_background_clip, mock_get_char_position, mock_create_scene_clips

@pytest.fixture
def sample_config():
    return {
        "canvas_size": [1280, 720],
        "fps": 30,
        "background": "path/to/background.png",
        "music": "path/to/music.mp3",
        "characters": [] # Not directly used in VideoEditor, but good for completeness
    }

@pytest.fixture
def sample_processed_characters():
    return [
        {
            "image": np.zeros((100, 100, 4), dtype=np.uint8), # Mock image as numpy array
            "text_image": np.zeros((50, 200, 4), dtype=np.uint8), # Mock text image
            "start_time": 0,
            "duration": 5,
            "side": "left",
            "rotate": True
        },
        {
            "image": np.zeros((100, 100, 4), dtype=np.uint8),
            "text_image": np.zeros((50, 200, 4), dtype=np.uint8),
            "start_time": 2,
            "duration": 4,
            "side": "right",
            "rotate": False
        }
    ]

class TestVideoEditor:
    def test_init(self, sample_config):
        editor = VideoEditor(sample_config, ImageClip_factory=MockImageClip, AudioFileClip_factory=MockAudioFileClip, CompositeVideoClip_factory=MockCompositeVideoClip)
        assert editor.config == sample_config
        assert editor.canvas_size == (1280, 720)
        assert editor.fps == 30
        assert editor.ImageClip_factory == MockImageClip
        assert editor.AudioFileClip_factory == MockAudioFileClip
        assert editor.CompositeVideoClip_factory == MockCompositeVideoClip

    def test_build_video_basic(self, sample_config, sample_processed_characters, mock_video_utils):
        mock_create_background_clip, mock_get_char_position, mock_create_scene_clips = mock_video_utils

        editor = VideoEditor(sample_config, ImageClip_factory=MockImageClip, AudioFileClip_factory=MockAudioFileClip, CompositeVideoClip_factory=MockCompositeVideoClip)
        video = editor.build_video(sample_processed_characters)

        # Verify create_background_clip is called
        mock_create_background_clip.assert_called_once_with(
            sample_config["background"],
            max(c["start_time"] + c["duration"] for c in sample_processed_characters),
            editor.canvas_size,
            editor.ImageClip_factory,
            editor.ColorClip_factory
        )

        # Verify create_scene_clips is called for each character
        assert mock_create_scene_clips.call_count == len(sample_processed_characters)
        for char_config in sample_processed_characters:
            mock_create_scene_clips.assert_any_call(
                ANY, # Use ANY for numpy array comparison
                ANY, # Use ANY for numpy array comparison
                char_config["start_time"],
                char_config["duration"],
                editor.canvas_size,
                char_config.get("side", "left"),
                editor.ImageClip_factory
            )

        # Verify CompositeVideoClip is called
        assert isinstance(video, MockCompositeVideoClip)
        assert len(video.clips) == 1 + len(sample_processed_characters) * 2 # Background + (char + text) for each character
        assert video.size == editor.canvas_size

        # Verify audio is set if music path is provided
        assert hasattr(video, 'audio')
        assert isinstance(video.audio, MockAudioFileClip)

    def test_build_video_no_music(self, sample_config, sample_processed_characters, mock_video_utils):
        mock_create_background_clip, mock_get_char_position, mock_create_scene_clips = mock_video_utils
        config_no_music = sample_config.copy()
        del config_no_music["music"]

        editor = VideoEditor(config_no_music, ImageClip_factory=MockImageClip, AudioFileClip_factory=MockAudioFileClip, CompositeVideoClip_factory=MockCompositeVideoClip)
        video = editor.build_video(sample_processed_characters)

        # Verify audio is NOT set if no music path is provided
        assert not hasattr(video, 'audio')

    def test_build_video_empty_characters(self, sample_config, mock_video_utils):
        mock_create_background_clip, mock_get_char_position, mock_create_scene_clips = mock_video_utils

        editor = VideoEditor(sample_config, ImageClip_factory=MockImageClip, AudioFileClip_factory=MockAudioFileClip, CompositeVideoClip_factory=MockCompositeVideoClip)
        video = editor.build_video([])

        # Verify background clip is still created with duration 0
        mock_create_background_clip.assert_called_once_with(
            sample_config["background"],
            0, # Max duration should be 0 for empty characters
            editor.canvas_size,
            editor.ImageClip_factory,
            editor.ColorClip_factory
        )
        # CompositeVideoClip should still be called, but with only the background
        assert isinstance(video, MockCompositeVideoClip)
        assert len(video.clips) == 1 # Only background clip
        assert video.size == editor.canvas_size
        assert video.duration == 0 # Duration should be 0 for empty characters