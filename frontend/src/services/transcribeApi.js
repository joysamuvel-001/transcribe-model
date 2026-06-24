
const BASE_URL = "http://localhost:8000";

/**
 * POST a recorded audio Blob to /api/transcribe.
 *
 * @param {Blob} audioBlob  - WebM/Opus blob from MediaRecorder
 * @returns {Promise<{ text: string, conversation: ConversationTurn[] }>}
 *
 * @typedef {{ speaker: string, text: string, start: number, end: number }} ConversationTurn
 */
export async function transcribeAudio(audioBlob) {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");

  const response = await fetch(`${BASE_URL}/api/transcribe`, {
    method: "POST",
    body: form,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `Server error ${response.status}`);
  }

  return data;
}

/**
 * GET /api/health — lightweight server liveness check.
 * @returns {Promise<{ status: string, gpu: boolean, device: string }>}
 */
export async function checkHealth() {
  const response = await fetch(`${BASE_URL}/api/health`);
  if (!response.ok) throw new Error("Server unreachable");
  return response.json();
}