
import os
import av
import numpy as np
from scipy.io import wavfile


def convert_to_wav(audio_bytes: bytes, output_path: str) -> None:
    """
    Write audio_bytes (WebM/Opus from browser) to output_path as
    a 16kHz mono signed-16-bit WAV file.

    Raises RuntimeError if the input has no audio stream or no samples.
    """
    tmp_input = output_path + "_input"
    with open(tmp_input, "wb") as f:
        f.write(audio_bytes)

    try:
        samples = []

        with av.open(tmp_input) as container:
            audio_stream = next(
                (s for s in container.streams if s.type == "audio"), None
            )
            if audio_stream is None:
                raise RuntimeError("No audio stream found in the uploaded file.")

            print(
                f"[converter] codec={audio_stream.codec_context.name}  "
                f"rate={audio_stream.sample_rate}Hz  "
                f"channels={audio_stream.channels}"
            )

            resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)

            for frame in container.decode(audio_stream):
                for resampled in resampler.resample(frame):
                    samples.append(resampled.to_ndarray()[0])

            # Flush the resampler
            for resampled in resampler.resample(None):
                samples.append(resampled.to_ndarray()[0])

        if not samples:
            raise RuntimeError("No audio samples decoded — file may be empty or corrupt.")

        audio_np = np.concatenate(samples).astype(np.int16)
        wavfile.write(output_path, 16000, audio_np)

        duration = len(audio_np) / 16000
        print(f"[converter] wrote {len(audio_np)} samples ({duration:.2f}s) → {output_path}")

    finally:
        if os.path.exists(tmp_input):
            os.remove(tmp_input)