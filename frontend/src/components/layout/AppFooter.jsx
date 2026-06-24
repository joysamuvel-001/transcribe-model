import { RecordButton } from "../Controls/RecordButton";
import styles from "./AppFooter.module.css";

const RetryIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
  </svg>
);

const NewSessionIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
    <path d="M3 3v5h5"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

export function AppFooter({ recording, elapsed, processing, onStart, onStop, onRetryVoice, onNewSession, hasConversation }) {
  const showActions = hasConversation && !recording && !processing;

  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <RecordButton recording={recording} elapsed={elapsed} processing={processing} onStart={onStart} onStop={onStop} />
        {showActions && (
          <div className={styles.actions}>
            <button className={styles.actionBtn} onClick={onRetryVoice}>
              <RetryIcon /> Retry last recording
            </button>
            <span className={styles.divider} />
            <button className={`${styles.actionBtn} ${styles.actionBtnDanger}`} onClick={onNewSession}>
              <NewSessionIcon /> New session
            </button>
          </div>
        )}
      </div>
    </footer>
  );
}