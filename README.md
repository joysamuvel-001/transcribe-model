# MedTranscribe 🎙️

AI-powered medical transcription with speaker identification.  
**Stack:** NVIDIA NeMo (Nemotron ASR · TitaNet · Sortformer) · FastAPI · React + Vite

---

## Model Downloads

| Model | Size | When it downloads |
|---|---|---|
| Nemotron ASR (`nvidia/nemotron-speech-streaming-en-0.6b`) | ~600 MB | Immediately when `server.py` starts |
| TitaNet Large (`nvidia/speakerverification_en_titanet_large`) | ~90 MB | On your **first enroll or transcribe** request |
| Sortformer diarization | ~200 MB | On your **first transcribe** request |

Models are cached locally after the first download — subsequent runs are instant.  
**Expect the first run to take 5–10 minutes** depending on your internet speed.

---

## Setup

### Prerequisites
- Python 3.10
- NVIDIA GPU recommended (CUDA 12.1+) — CPU works but is significantly slower
- Node.js 18+

---

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/medtranscribe.git
cd medtranscribe
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

---

### 3. Install Python dependencies

**CPU only:**
```bash
pip install -r requirements.txt
```

**GPU (CUDA 12.1) — recommended:**
```bash
# Install PyTorch with CUDA support first
pip install torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

# Then install the rest
pip install -r requirements.txt
```

---

### 4. Create the enrolled speakers folder

```bash
mkdir enrolled_speakers
```

_(On Mac/Linux you can use `mkdir -p enrolled_speakers`)_

---

### 5. Start the backend

```bash
cd backend
python server.py
```

On first run, Nemotron ASR downloads immediately (~600 MB). Wait for:
```
[asr] Running on GPU: ...        ← or "Running on CPU"
INFO: Uvicorn running on http://0.0.0.0:8000
```

TitaNet and Sortformer will download on your first request (one-time only).

---

### 6. Start the frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## Usage

1. **Enroll speakers** — type a name, click Record Sample, speak for 5–10 sec, click stop. Do this for each person before recording the session.
2. **Record** — click the mic button, speak, click stop. Processing takes a few seconds.
3. **Read results** — enrolled speakers appear by name with a match %; anyone not enrolled shows as *Unknown*.

---

## Project Structure

```
medtranscribe/
├── backend/
│   ├── server.py                 # FastAPI app + pipeline orchestration
│   ├── audio_utils/
│   │   └── converter.py          # WebM/Opus → 16kHz mono WAV (via PyAV)
│   ├── diarization/
│   │   ├── model.py              # Sortformer diarization
│   │   └── speaker.py            # Segment parsing + merging
│   ├── transcription/
│   │   └── asr.py                # Nemotron ASR inference
│   ├── identification/
│   │   ├── titanet.py            # TitaNet embedding extraction
│   │   └── registry.py           # Enrollment store + cosine matching
│   └── enrolled_speakers/        # Speaker embeddings saved here (gitignored)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
├── requirements.txt
└── README.md
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'nemo'`**  
→ Make sure your virtual environment is activated (`venv\Scripts\activate` on Windows).

**`av` / ffmpeg errors on audio conversion**  
→ PyAV bundles its own ffmpeg — do not install system ffmpeg separately, it will conflict.

**Low speaker match scores (below 65%)**  
→ Enroll with a longer sample (8–10 sec). Enrolling the same person 2–3 times improves accuracy — embeddings are averaged automatically.

**CUDA out of memory**  
→ Close other GPU applications. All three models together use ~2–3 GB VRAM.

**First transcribe is very slow**  
→ Normal — TitaNet and Sortformer are downloading in the background. Subsequent runs are fast.