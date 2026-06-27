"""
correction/medgemma.py
-----------------------
General-purpose medical ASR correction using MedGemma.

Design principles:
  - NO hardcoded medical term lists
  - NO specialty detection keywords
  - MedGemma uses its own medical knowledge to identify and fix any term
    from any specialty — cardiology, oncology, nephrology, psychiatry, etc.
  - Two-stage pipeline:
      Stage 1: Context pass — MedGemma reads the full conversation and
               infers what domain/specialty is being discussed
      Stage 2: Per-turn correction pass — each turn corrected individually
               with the inferred context injected, plus one universal
               1-shot example that teaches the ERROR TYPE not the domain
  - Safety filter rejects hallucinations without blocking valid corrections

Requirements:
    pip install transformers>=4.50.0 accelerate
    huggingface-cli login
    Accept license: huggingface.co/google/medgemma-1.5-4b-it
"""

import os
import re
import difflib
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

MODEL_ID = "google/medgemma-1.5-4b-it"
DEVICE   = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE    = torch.bfloat16 if DEVICE == "cuda" else torch.float32

ENABLE_CORRECTION = os.environ.get("ENABLE_MEDGEMMA_CORRECTION", "true").lower() == "true"

_model     = None
_processor = None

if ENABLE_CORRECTION:
    print(f"[medgemma] Loading {MODEL_ID}...")
    try:
        _processor = AutoProcessor.from_pretrained(MODEL_ID)
        _model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID,
            torch_dtype=DTYPE,
            device_map="auto",
        )
        _model.eval()
        print(f"[medgemma] Ready on {DEVICE}.")
    except Exception as e:
        print(f"[medgemma] FAILED — correction disabled: {e}")
        _model = None


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# Tells MedGemma who it is. Kept short — all task detail goes in user prompt.
# The thinking trigger (from Google's own notebook) activates reasoning mode.
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "SYSTEM INSTRUCTION: think silently if needed. "
    "You are a clinical transcription specialist with complete knowledge of "
    "all medical specialties, drug names, procedures, anatomy, and diagnoses. "
    "You correct ASR errors in doctor-patient conversations. "
    "You never invent clinical content."
)


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1 PROMPT — Context inference
#
# MedGemma reads the full raw conversation and returns a 1-2 sentence
# clinical summary that captures what medical topic is being discussed.
# This summary is then injected into every per-turn correction prompt
# so the model has domain context without us needing to tell it the domain.
# ─────────────────────────────────────────────────────────────────────────────
CONTEXT_PROMPT = """\
Below is a raw ASR transcript of a doctor-patient consultation.
The speech recognition made errors — some medical terms are garbled or phonetically mangled.
Despite the errors, read the full transcript and infer what medical topic is being discussed.

RAW TRANSCRIPT:
{full_text}

In 1-2 sentences, describe the medical context of this consultation
(e.g. what condition is being discussed, what treatment is being considered).
Do not correct the text yet. Just summarize the clinical topic.

CLINICAL CONTEXT:"""


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2 PROMPT — Per-turn correction
#
# One universal 1-shot example that teaches the ERROR TYPE (Indian-accent ASR
# garbling of medical terms), not any specific domain.
# MedGemma applies its full medical knowledge to any term in any specialty.
# ─────────────────────────────────────────────────────────────────────────────
CORRECTION_PROMPT = """\
You are correcting one line of ASR output from a doctor-patient consultation.

CLINICAL CONTEXT OF THIS CONSULTATION:
{context}

ABOUT THE ERRORS:
This speech was recorded from an Indian-English speaker. The ASR system makes
characteristic errors with medical terminology:
- Drug names get split or phonetically mangled
  (e.g. "with form in" → "metformin", "solution mall" → "salbutamol",
   "parasdamal" → "paracetamol", "atorvas tin" → "atorvastatin")
- Medical terms get phonetically substituted
  (e.g. "seismic dysfunction" → "systolic dysfunction",
   "commutator heart failure" → "congestive heart failure",
   "smilely elevated" → "mildly elevated",
   "elevator jugular unuser" → "elevated jugular venous")
- Syllables get compressed or run together
  (e.g. "holo systolic" → "holosystolic", "echocardiog raphy" → "echocardiography")
- Numbers spoken as words
  (e.g. "five hundred" → "500", "two point one" → "2.1")

ONE-SHOT EXAMPLE (shows the correction style, not the domain — apply same logic to any specialty):
INPUT:  "Patient has type two diabetes and bludpressure. I will start with form in five hundred mg twice daily and amlodipin five mg for the bludpressure."
OUTPUT: "Patient has type 2 diabetes and high blood pressure. I will start metformin 500 mg twice daily and amlodipine 5 mg for the blood pressure."

CORRECTION RULES:
1. Use the clinical context above to infer what garbled terms most likely mean.
2. Fix any medical term, drug name, procedure, anatomy, or diagnosis that is
   clearly garbled — from ANY medical specialty.
3. Convert spoken numbers to digits where it improves clarity (500 mg, not "five hundred mg").
4. If a word or phrase is too garbled to confidently reconstruct, leave it UNCHANGED.
5. Do NOT add symptoms, diagnoses, or any content not implied by the input.
6. Do NOT change the meaning of what was said.
7. Return ONLY the corrected line — no explanation, no prefix, no quotes.

INPUT:  "{turn_text}"
OUTPUT: """


# ─────────────────────────────────────────────────────────────────────────────
# Main public function
# ─────────────────────────────────────────────────────────────────────────────
def correct_medical_terms(conversation: list) -> list:
    """
    Two-stage correction:
      Stage 1: Infer clinical context from full raw conversation (1 model call)
      Stage 2: Correct each turn individually using that context (N model calls)

    Falls back to original text per-turn if correction fails safety check.
    """
    if not ENABLE_CORRECTION or _model is None or not conversation:
        return conversation

    # ── Stage 1: Infer context ────────────────────────────────────────────────
    context = _infer_context(conversation)
    print(f"[medgemma] Inferred context: {context}")

    # ── Stage 2: Per-turn correction ─────────────────────────────────────────
    result = []
    for i, turn in enumerate(conversation):
        text = turn.get("text", "")

        # Skip very short turns — not enough signal to correct safely
        if len(text.split()) < 4:
            result.append(turn)
            continue

        corrected = _correct_turn(text, context, turn_index=i + 1)

        if corrected and corrected != text and _is_safe_correction(text, corrected):
            new_turn             = dict(turn)
            new_turn["raw_text"] = text
            new_turn["text"]     = corrected
            result.append(new_turn)
            print(f"[medgemma] Turn {i+1} corrected: '{text[:50]}...' → '{corrected[:50]}...'")
        else:
            if corrected and corrected != text:
                print(f"[medgemma] Turn {i+1} rejected by safety check — keeping original")
            result.append(turn)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Context inference
# ─────────────────────────────────────────────────────────────────────────────
def _infer_context(conversation: list) -> str:
    """
    Ask MedGemma to read the raw transcript and summarize the clinical topic.
    Returns a 1-2 sentence string used to ground subsequent corrections.
    Falls back to a generic context string if the call fails.
    """
    full_text = "\n".join(
        f"{t.get('speaker', 'Speaker')}: {t.get('text', '')}"
        for t in conversation
    )

    # Truncate if very long — context inference only needs the gist
    if len(full_text) > 2000:
        full_text = full_text[:2000] + "..."

    prompt = CONTEXT_PROMPT.format(full_text=full_text)

    messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user",   "content": [{"type": "text", "text": prompt}]},
    ]

    try:
        output = _generate(messages, max_new_tokens=120)
        # Clean up — take only the first 1-2 sentences
        sentences = re.split(r'(?<=[.!?])\s+', output.strip())
        context = " ".join(sentences[:2]).strip()
        if context:
            return context
    except Exception as e:
        print(f"[medgemma] Context inference failed: {e}")

    return "This is a general medical consultation between a doctor and patient."


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Single turn correction
# ─────────────────────────────────────────────────────────────────────────────
def _correct_turn(text: str, context: str, turn_index: int = 0) -> str:
    """
    Correct one ASR turn using the inferred clinical context.
    Returns the corrected string, or the original if generation fails.
    """
    prompt = CORRECTION_PROMPT.format(
        context=context,
        turn_text=text,
    )

    messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user",   "content": [{"type": "text", "text": prompt}]},
    ]

    try:
        output = _generate(messages, max_new_tokens=300)

        # Strip accidental quotes, prefixes, or extra lines the model adds
        output = output.strip()
        output = re.sub(r'^["\'`]+|["\'`]+$', "", output).strip()
        output = re.sub(
            r"^(OUTPUT:|Corrected:|Result:|Answer:)\s*",
            "", output, flags=re.IGNORECASE
        ).strip()

        # Take only the first line if model outputs multiple
        first_line = output.split("\n")[0].strip()
        return first_line if first_line else text

    except Exception as e:
        print(f"[medgemma] Turn {turn_index} generation failed: {e}")
        return text


# ─────────────────────────────────────────────────────────────────────────────
# Shared generation helper
# ─────────────────────────────────────────────────────────────────────────────
def _generate(messages: list, max_new_tokens: int) -> str:
    inputs = _processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(DEVICE)

    with torch.no_grad():
        output_ids = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            repetition_penalty=1.1,
        )

    return _processor.decode(
        output_ids[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Safety filter
# ─────────────────────────────────────────────────────────────────────────────
def _is_safe_correction(original: str, corrected: str) -> bool:
    """
    Reject corrections that look like hallucination or off-task output.

    Checks:
      1. Block known refusal / meta-commentary phrases
      2. Corrected text must not be more than 50% longer (hallucination signal)
      3. Word overlap ratio >= 0.60 (allows multi-word substitutions like
         "solution mall" → "salbutamol", while blocking wholesale rewrites)
    """
    BLOCK_PHRASES = [
        "as an ai", "i cannot", "i can't", "i am not able",
        "medical advice", "please consult", "disclaimer",
        "here is the corrected", "here are the corrections",
        "the corrected text", "output:", "example:", "note:",
        "i have corrected", "i corrected",
    ]

    lower = corrected.lower().strip()

    if any(phrase in lower for phrase in BLOCK_PHRASES):
        return False

    if not corrected.strip():
        return False

    orig_words = original.split()
    corr_words = corrected.split()

    # Block if output grew by more than 50% — strong hallucination signal
    if len(corr_words) > len(orig_words) * 1.5:
        return False

    # Minimum word-level overlap
    ratio = difflib.SequenceMatcher(None, orig_words, corr_words).ratio()
    return ratio >= 0.60