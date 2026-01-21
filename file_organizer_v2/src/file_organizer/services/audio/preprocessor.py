"""
Audio Preprocessing Service

Provides audio format conversion, normalization, and preprocessing
capabilities to prepare audio files for transcription and analysis.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union
import logging
import tempfile

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"
    WMA = "wma"
    OPUS = "opus"


@dataclass
class AudioConfig:
    """Audio configuration parameters."""
    sample_rate: int = 16000  # Whisper optimal rate
    channels: int = 1  # Mono
    bit_rate: str = "128k"
    codec: str = "pcm_s16le"  # For WAV


class AudioPreprocessor:
    """
    Audio preprocessing service for format conversion and normalization.

    Handles:
    - Format conversion (mp3, m4a, flac, etc. -> wav)
    - Sample rate conversion (optimal for Whisper: 16kHz)
    - Channel conversion (stereo -> mono)
    - Audio normalization
    - Silence removal
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize the audio preprocessor.

        Args:
            config: Audio configuration (uses defaults if None)
        """
        self.config = config or AudioConfig()
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is available."""
        try:
            import subprocess
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("ffmpeg not found or not working properly")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning(
                "ffmpeg not found. Audio conversion capabilities will be limited. "
                "Install ffmpeg for full functionality."
            )

    def convert_to_wav(
        self,
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
    ) -> Path:
        """
        Convert audio file to WAV format optimized for transcription.

        Args:
            audio_path: Input audio file path
            output_path: Output file path (None = temp file)
            sample_rate: Target sample rate (None = use config default)
            channels: Number of channels (None = use config default)

        Returns:
            Path to the converted WAV file

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If conversion fails
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Determine output path
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = Path(temp_dir) / f"{audio_path.stem}_converted.wav"
        else:
            output_path = Path(output_path)

        # Use config defaults if not specified
        sample_rate = sample_rate or self.config.sample_rate
        channels = channels or self.config.channels

        logger.info(f"Converting {audio_path} to WAV format")

        try:
            import subprocess

            # Build ffmpeg command
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-c:a", self.config.codec,
                "-y",  # Overwrite output file
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")

            logger.info(f"Conversion complete: {output_path}")
            return output_path

        except FileNotFoundError:
            # Fallback to pydub if ffmpeg not available
            return self._convert_with_pydub(
                audio_path, output_path, sample_rate, channels
            )
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise

    def _convert_with_pydub(
        self,
        audio_path: Path,
        output_path: Path,
        sample_rate: int,
        channels: int,
    ) -> Path:
        """Fallback conversion using pydub."""
        try:
            from pydub import AudioSegment

            logger.info("Using pydub for conversion (ffmpeg not available)")

            # Load audio
            audio = AudioSegment.from_file(str(audio_path))

            # Convert to target format
            audio = audio.set_frame_rate(sample_rate)
            audio = audio.set_channels(channels)

            # Export as WAV
            audio.export(
                str(output_path),
                format="wav",
                parameters=["-ar", str(sample_rate)]
            )

            logger.info(f"Conversion complete using pydub: {output_path}")
            return output_path

        except ImportError:
            raise ImportError(
                "Neither ffmpeg nor pydub is available for audio conversion. "
                "Install one of them: apt-get install ffmpeg or pip install pydub"
            )

    def normalize_audio(
        self,
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        target_db: float = -20.0,
    ) -> Path:
        """
        Normalize audio levels.

        Args:
            audio_path: Input audio file path
            output_path: Output file path (None = overwrite input)
            target_db: Target dB level

        Returns:
            Path to normalized audio file
        """
        audio_path = Path(audio_path)
        if output_path is None:
            output_path = audio_path
        else:
            output_path = Path(output_path)

        try:
            from pydub import AudioSegment
            from pydub.effects import normalize

            logger.info(f"Normalizing audio: {audio_path}")

            audio = AudioSegment.from_file(str(audio_path))
            normalized = normalize(audio, headroom=abs(target_db))

            normalized.export(str(output_path), format=output_path.suffix[1:])

            logger.info(f"Normalization complete: {output_path}")
            return output_path

        except ImportError:
            logger.warning("pydub not available, skipping normalization")
            return audio_path

    def remove_silence(
        self,
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        silence_thresh: int = -40,  # dB
        min_silence_len: int = 1000,  # ms
    ) -> Path:
        """
        Remove silence from audio file.

        Args:
            audio_path: Input audio file path
            output_path: Output file path (None = overwrite input)
            silence_thresh: Silence threshold in dB
            min_silence_len: Minimum silence length in ms

        Returns:
            Path to processed audio file
        """
        audio_path = Path(audio_path)
        if output_path is None:
            output_path = audio_path
        else:
            output_path = Path(output_path)

        try:
            from pydub import AudioSegment
            from pydub.silence import detect_nonsilent

            logger.info(f"Removing silence from: {audio_path}")

            audio = AudioSegment.from_file(str(audio_path))

            # Detect non-silent chunks
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh
            )

            # Concatenate non-silent chunks
            if nonsilent_ranges:
                trimmed = AudioSegment.empty()
                for start, end in nonsilent_ranges:
                    trimmed += audio[start:end]

                trimmed.export(str(output_path), format=output_path.suffix[1:])
                logger.info(f"Silence removal complete: {output_path}")
                return output_path
            else:
                logger.warning("No non-silent audio detected")
                return audio_path

        except ImportError:
            logger.warning("pydub not available, skipping silence removal")
            return audio_path

    def preprocess(
        self,
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        convert_to_wav: bool = True,
        normalize: bool = True,
        remove_silence: bool = False,
    ) -> Path:
        """
        Complete preprocessing pipeline.

        Args:
            audio_path: Input audio file path
            output_path: Output file path (None = temp file)
            convert_to_wav: Whether to convert to WAV
            normalize: Whether to normalize audio levels
            remove_silence: Whether to remove silence

        Returns:
            Path to preprocessed audio file
        """
        audio_path = Path(audio_path)
        current_file = audio_path

        logger.info(f"Starting preprocessing pipeline for: {audio_path}")

        # Step 1: Convert to WAV if needed
        if convert_to_wav and audio_path.suffix.lower() != ".wav":
            current_file = self.convert_to_wav(current_file, output_path)

        # Step 2: Normalize
        if normalize:
            current_file = self.normalize_audio(current_file)

        # Step 3: Remove silence
        if remove_silence:
            current_file = self.remove_silence(current_file)

        logger.info(f"Preprocessing complete: {current_file}")
        return current_file

    @staticmethod
    def get_audio_info(audio_path: Union[str, Path]) -> dict:
        """
        Get audio file information.

        Args:
            audio_path: Audio file path

        Returns:
            Dictionary with audio metadata
        """
        audio_path = Path(audio_path)

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(audio_path))

            return {
                "duration_seconds": len(audio) / 1000.0,
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "format": audio_path.suffix[1:],
            }

        except ImportError:
            return {"error": "pydub not available"}

    @staticmethod
    def is_supported_format(audio_path: Union[str, Path]) -> bool:
        """Check if audio format is supported."""
        audio_path = Path(audio_path)
        suffix = audio_path.suffix.lower()[1:]  # Remove the dot

        supported = [fmt.value for fmt in AudioFormat]
        return suffix in supported
