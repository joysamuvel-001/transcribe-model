

import shutil
import tempfile
import uuid

import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from audio_utils.converter import convert_to_wav
from diarization.model import run_diarization
from diarization.speaker import process_diarization
from transcription.asr import transcribe_segments

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="MedTranscribe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Accept a browser-recorded WebM/Opus clip, run speaker diarization,
    then ASR on each turn, and return a structured conversation.

    Response shape:
        {
            "text": "full concatenated transcript",
            "conversation": [
                {"speaker": "Doctor",  "text": "...", "start": 0.0, "end": 3.2},
                {"speaker": "Patient", "text": "...", "start": 3.4, "end": 7.1},
                ...
            ]
        }
    """
    tmp_dir  = tempfile.mkdtemp()
    wav_path = f"{tmp_dir}/{uuid.uuid4()}.wav"

    try:
        audio_bytes = await audio.read()
        print(f"[server] received {len(audio_bytes)} bytes  type={audio.content_type}")

        # 1. Convert browser audio to 16kHz mono WAV
        convert_to_wav(audio_bytes, wav_path)

        # 2. Run Sortformer diarization
        raw_segments = run_diarization(wav_path)

        # 3. Parse, merge, assign Doctor / Patient roles
        labeled_segments = process_diarization(raw_segments)

        # 4. Slice + transcribe each turn
        conversation = transcribe_segments(wav_path, labeled_segments, tmp_dir)

        full_text = " ".join(t["text"] for t in conversation)
        return {"text": full_text, "conversation": conversation}

    except Exception as exc:
        print(f"[server] error: {exc}")
        return JSONResponse(status_code=500, content={"error": str(exc)})

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "gpu":    torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)