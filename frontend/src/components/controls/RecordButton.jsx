import styles from "./RecordButton.module.css";

function pad(n) { return n.toString().padStart(2, "0"); }
function fmt(s) { return `${pad(Math.floor(s/60))}:${pad(s%60)}`; }

const MicIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
       strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="23"/>
    <line x1="8" y1="23" x2="16" y2="23"/>
  </svg>
);

const StopIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
    <rect x="5" y="5" width="14" height="14" rx="2"/>
  </svg>
);

export function RecordButton({ recording, elapsed, processing, onStart, onStop }) {
  return (
    <div className={styles.wrapper}>
      {recording && (
        <div className={styles.timer}>
          <span className={styles.recDot} />
          {fmt(elapsed)}
        </div>
      )}
      <button
        className={`${styles.btn} ${recording ? styles.btnRecording : ""}`}
        onClick={recording ? onStop : onStart}
        disabled={processing}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? <StopIcon /> : <MicIcon />}
      </button>
      <span className={styles.hint}>
        {processing ? "Processing…" : recording ? "Tap to stop" : "Tap to record"}
      </span>
    </div>
  );
}