"""
Audio Processing Services

This module provides audio file processing capabilities including:
- Audio transcription using Whisper models
- Audio format preprocessing and conversion
- Audio metadata extraction
- Audio utility functions
"""

from .transcriber import AudioTranscriber, TranscriptionResult, TranscriptionOptions
from .metadata_extractor import AudioMetadataExtractor, AudioMetadata
from .preprocessor import AudioPreprocessor, AudioFormat
from .utils import (
    get_audio_duration,
    normalize_audio,
    split_audio,
    convert_audio_format,
    validate_audio_file,
)

__all__ = [
    # Transcription
    "AudioTranscriber",
    "TranscriptionResult",
    "TranscriptionOptions",
    # Metadata
    "AudioMetadataExtractor",
    "AudioMetadata",
    # Preprocessing
    "AudioPreprocessor",
    "AudioFormat",
    # Utilities
    "get_audio_duration",
    "normalize_audio",
    "split_audio",
    "convert_audio_format",
    "validate_audio_file",
]
