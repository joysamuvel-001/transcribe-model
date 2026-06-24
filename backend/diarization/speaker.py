"""
diarization/speaker.py
-----------------------
Wraps NVIDIA Sortformer diarization model.

Responsibilities:
  - Parse raw diarizer output into (start, end, speaker_id) triples
  - Merge jittery same-speaker segments that are close together
  - Drop very short noise segments
  - Assign human-readable roles: first voice -> Doctor, all others -> Patient
"""

import re
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

# Merge same-speaker segments separated by less than this many seconds.
MERGE_GAP_SECONDS = 0.6

# Drop segments shorter than this — usually diarizer noise, not real speech.
MIN_SEGMENT_SECONDS = 0.25

# Role assignment order. First voice heard becomes index 0 (Doctor),
# every subsequent new voice becomes Patient regardless of count.
_ROLES = ["Doctor", "Patient"]

_SEGMENT_RE = re.compile(r"(\d+\.\d+)\s+(\d+\.\d+)\s+(speaker_\d+)")

Segment = Tuple[float, float, str]  # (start, end, label)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_raw_segments(raw_output: list) -> List[Segment]:
    """
    Convert Sortformer's raw string output into sorted (start, end, speaker_id)
    tuples.

    raw_output: list of strings like '0.00 3.20 speaker_0'
    """
    parsed: List[Segment] = []
    for line in raw_output:
        m = _SEGMENT_RE.search(str(line))
        if not m:
            continue
        start, end, speaker = m.groups()
        parsed.append((float(start), float(end), speaker))
    parsed.sort(key=lambda s: s[0])
    return parsed


def merge_segments(
    segments: List[Segment],
    max_gap: float = MERGE_GAP_SECONDS,
    min_duration: float = MIN_SEGMENT_SECONDS,
) -> List[Segment]:
    """
    1. Merge consecutive same-speaker segments whose gap is ≤ max_gap seconds.
    2. Drop any result shorter than min_duration seconds.
    """
    if not segments:
        return []

    merged = [list(segments[0])]
    for start, end, speaker in segments[1:]:
        last = merged[-1]
        if speaker == last[2] and (start - last[1]) <= max_gap:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end, speaker])

    return [
        (seg[0], seg[1], seg[2])
        for seg in merged
        if (seg[1] - seg[0]) >= min_duration
    ]


def assign_roles(segments: List[Segment]) -> List[Segment]:
    """
    Map raw speaker_N labels to clinical roles.

    Rule: first speaker encountered -> "Doctor".
          Every subsequent speaker (however many Sortformer finds) -> "Patient".

    This intentionally collapses phantom 3rd/4th speakers caused by background
    noise or model jitter into "Patient", keeping the output strictly 2-person.
    """
    role_map: dict[str, str] = {}
    idx = 0
    labeled: List[Segment] = []

    for start, end, speaker in segments:
        if speaker not in role_map:
            role_map[speaker] = _ROLES[0] if idx == 0 else _ROLES[1]
            idx += 1
        labeled.append((start, end, role_map[speaker]))

    return labeled


def process_diarization(raw_output: list) -> List[Segment]:
    """
    Full pipeline: parse -> merge -> assign roles.
    Returns a chronologically sorted list of (start, end, role) tuples.
    """
    parsed = parse_raw_segments(raw_output)
    merged = merge_segments(parsed)
    labeled = assign_roles(merged)
    return labeled