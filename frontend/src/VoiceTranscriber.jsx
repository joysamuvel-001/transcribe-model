/**
 * VoiceTranscriber.jsx
 * ---------------------
 * Root orchestrator. Full-screen two-column layout:
 *   Left  — Sidebar  (dark, branding + controls)
 *   Right — ChatWindow (light, transcript)
 */

import { useState, useCallback, useRef } from "react";

import { useRecorder }     from "./hooks/useRecorder";
import { transcribeAudio } from "./services/transcribeApi";

import { Sidebar }    from "./components/Sidebar/Sidebar";
import { ChatWindow } from "./components/Chat/ChatWindow";

import "./styles/global.css";

export default function VoiceTranscriber() {
  const [conversation, setConversation] = useState([]);
  const [processing,   setProcessing]   = useState(false);
  const [error,        setError]        = useState(null);
  const prevLengthRef = useRef(0);

  const handleBlob = useCallback(async (blob) => {
    setProcessing(true);
    setError(null);
    try {
      const data = await transcribeAudio(blob);
      if (!data.conversation?.length) {
        setError("No speech detected. Speak clearly and try again.");
      } else {
        setConversation((prev) => {
          prevLengthRef.current = prev.length;
          return [...prev, ...data.conversation];
        });
      }
    } catch (err) {
      setError(err.message || "Could not reach the server. Is it running on port 8000?");
    } finally {
      setProcessing(false);
    }
  }, []);

  const { recording, elapsed, start, stop } = useRecorder(handleBlob);

  const handleStart = async () => {
    setError(null);
    try { await start(); } catch (err) { setError(err.message); }
  };

  const handleRetryVoice = () => {
    setConversation((prev) => prev.slice(0, prevLengthRef.current));
    setError(null);
  };

  const handleNewSession = () => {
    setConversation([]);
    prevLengthRef.current = 0;
    setError(null);
  };

  const doctorTurns  = conversation.filter((t) => t.speaker === "Doctor").length;
  const patientTurns = conversation.filter((t) => t.speaker === "Patient").length;

  return (
    <div className="app-shell">
      <Sidebar
        recording={recording}
        elapsed={elapsed}
        processing={processing}
        onStart={handleStart}
        onStop={stop}
        onRetryVoice={handleRetryVoice}
        onNewSession={handleNewSession}
        hasConversation={conversation.length > 0}
        turnCount={conversation.length}
        doctorTurns={doctorTurns}
        patientTurns={patientTurns}
      />

      <ChatWindow
        conversation={conversation}
        processing={processing}
        error={error}
      />
    </div>
  );
}