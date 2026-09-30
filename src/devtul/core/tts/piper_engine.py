"""
Piper TTS Engine for DevTul.
Adapted from controller-api for local speech synthesis, voice configuration, and model management.
"""

import io
import wave
from pathlib import Path
from typing import Generator, Optional

import piper
from pydantic import BaseModel, Field

from devtul.core.config import APP_DATA


class PiperConfig(BaseModel):
    """Configuration for Piper speech synthesis."""

    model_dir: Path = Field(
        default_factory=lambda: APP_DATA / "models",
        description="Directory where Piper ONNX models and configurations are stored",
    )
    default_model: str = Field(
        default="en_US-lessac-medium",
        description="Default voice model name",
    )
    speaker_id: Optional[int] = Field(None, description="Speaker ID for multi-speaker models")
    length_scale: float = Field(1.0, description="Speaking rate multiplier (<1.0 is faster, >1.0 is slower)")
    noise_scale: float = Field(0.667, description="Phoneme noise level")
    noise_w_scale: float = Field(0.8, description="Phoneme width noise level")
    volume: float = Field(1.0, description="Volume multiplier")


class PiperEngine:
    """
    Wrapper around piper-tts for speech synthesis in DevTul.
    Supports file generation and audio streaming.
    """

    def __init__(self, config: Optional[PiperConfig] = None, model_name: Optional[str] = None):
        self.config = config or PiperConfig()
        if model_name:
            self.config.default_model = model_name

        self.config.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.config.model_dir / f"{self.config.default_model}.onnx"
        self.config_path = self.config.model_dir / f"{self.config.default_model}.onnx.json"
        self._voice: Optional[piper.PiperVoice] = None

    @property
    def voice(self) -> piper.PiperVoice:
        """Lazily load the PiperVoice model."""
        if self._voice is None:
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Piper voice model not found at: {self.model_path}\n"
                    f"Please place '{self.config.default_model}.onnx' and '{self.config.default_model}.onnx.json' in {self.config.model_dir}."
                )
            self._voice = piper.PiperVoice.load(
                str(self.model_path.as_posix()),
                config_path=str(self.config_path.as_posix()),
            )
        return self._voice

    def _get_synthesis_config(self, speaker_id: Optional[int] = None, **kwargs) -> piper.SynthesisConfig:
        return piper.SynthesisConfig(
            speaker_id=speaker_id if speaker_id is not None else self.config.speaker_id,
            length_scale=kwargs.get("length_scale", self.config.length_scale),
            noise_scale=kwargs.get("noise_scale", self.config.noise_scale),
            noise_w_scale=kwargs.get("noise_w_scale", self.config.noise_w_scale),
            normalize_audio=True,
            volume=kwargs.get("volume", self.config.volume),
        )

    def generate_file(
        self,
        text: str,
        output_path: Path,
        speaker_id: Optional[int] = None,
        **kwargs,
    ) -> float:
        """
        Synthesize text directly to a WAV file.
        Returns duration in seconds.
        """
        synth_config = self._get_synthesis_config(speaker_id=speaker_id, **kwargs)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output_path.as_posix()), "wb") as wav_file:
            self.voice.synthesize(text, wav_file, synth_config)
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        return duration

    def stream(
        self,
        text: str,
        speaker_id: Optional[int] = None,
        skip_header: bool = False,
        **kwargs,
    ) -> Generator[bytes, None, None]:
        """
        Generate audio as a stream of raw WAV/PCM bytes.
        """
        synth_config = self._get_synthesis_config(speaker_id=speaker_id, **kwargs)
        if not skip_header:
            sample_rate = self.voice.config.sample_rate
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
            yield buffer.getvalue()

        for chunk in self.voice.synthesize(text, synth_config):
            yield chunk.audio_int16_bytes
