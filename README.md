# Testing Nemotron Speech-Streaming ASR (0.6B)

## Important: which model you can actually use right now

- `nvidia/nemotron-speech-streaming-en-0.6b` — **English only, publicly downloadable.** This is what the scripts below use.
- `nvidia/nemotron-3.5-asr-streaming-0.6b` — the multilingual 40-language version (includes Hindi). As of now this is **restricted to NVIDIA employees** (internal evaluation, early-access waitlist only). You won't be able to download it with a normal HF token yet.

So this test validates your pipeline using the English model. Once you get multilingual access, you swap one string (the `model_name`) and everything else stays the same.

## 1. Environment (do this on your Windows GPU machine)

NeMo is built for Linux. On native Windows it's a common source of install failures (Cython/C++ build issues, missing CUDA toolchain matches, etc). The reliable path:

1. Install **WSL2** with an Ubuntu distro (`wsl --install -d Ubuntu-22.04` in PowerShell as admin), if you don't have it already.
2. Install the **NVIDIA driver for WSL** on the Windows side (not inside WSL) — see https://docs.nvidia.com/cuda/wsl-user-guide/index.html. Your existing GPU driver may already support this.
3. Open the Ubuntu/WSL terminal for everything below.

## 2. Install dependencies (inside WSL/Ubuntu)

```bash
sudo apt-get update && sudo apt-get install -y libsndfile1 ffmpeg

python3 -m venv asr-env
source asr-env/bin/activate

pip install --upgrade pip
pip install Cython packaging

# Match this to your CUDA version. cu121 works for most recent GPUs/drivers.
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install "nemo_toolkit[asr] @ git+https://github.com/NVIDIA/NeMo.git@main"
pip install soundfile sounddevice huggingface_hub
```

Verify GPU is visible **before** going further — this is the #1 source of "it ran but was weirdly slow / errored later":

```bash
python3 -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

If this prints `False`, stop and fix the WSL/driver setup first — installing NeMo on top of a broken CUDA setup is where most errors come from.

## 3. (Optional) Hugging Face token

Not required for this specific model since it's public, but set it up now since you'll need it later for the multilingual one:

```bash
huggingface-cli login
# paste your token from https://huggingface.co/settings/tokens
```

## 4. Record a test clip and transcribe it

```bash
python3 record_audio.py        # records 5s from your mic -> test_audio.wav
python3 test_asr.py            # loads the model, transcribes test_audio.wav, prints the text
```

First run will download the model checkpoint (~2.5GB), so it'll pause for a bit on `from_pretrained(...)`.

## If something errors

Paste me the exact traceback rather than just "it errored" — NeMo's install/runtime errors are almost always specific (missing system lib, CUDA/torch version mismatch, sample rate mismatch on the wav file), and the fix depends entirely on which one it is.
