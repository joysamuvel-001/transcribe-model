import { RecordButton } from "../Controls/RecordButton";
import styles from "./Sidebar.module.css";

export function Sidebar({
  recording, elapsed, processing,
  onStart, onStop, onRetryVoice, onNewSession,
  hasConversation, doctorTurns = 0, patientTurns = 0,
}) {
  const showActions = hasConversation && !recording && !processing;

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.brandIcon}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="20" height="20">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
        </div>
        <div>
          <div className={styles.brandName}>MedTranscribe</div>
          <div className={styles.brandSub}>Clinical voice transcription</div>
        </div>
      </div>

      <div className={styles.divider} />

      <div className={styles.section}>
        <div className={styles.sectionLabel}>Session status</div>
        <div className={styles.statusRow}>
          <span className={`${styles.statusDot} ${recording ? styles.statusDotActive : ""}`} />
          <span className={styles.statusText}>
            {recording ? "Recording in progress" : processing ? "Processing audio…" : "Ready to record"}
          </span>
        </div>
      </div>

      <div className={styles.section}>
        <div className={styles.sectionLabel}>Speakers</div>
        <div className={styles.speakerRow}>
          <span className={styles.speakerDotDoctor} />
          <span className={styles.speakerLabel}>Doctor</span>
          <span className={styles.speakerCount}>{doctorTurns} turns</span>
        </div>
        <div className={styles.speakerRow}>
          <span className={styles.speakerDotPatient} />
          <span className={styles.speakerLabel}>Patient</span>
          <span className={styles.speakerCount}>{patientTurns} turns</span>
        </div>
      </div>

      <div className={styles.divider} />

      <div className={styles.recordSection}>
        <RecordButton
          recording={recording} elapsed={elapsed}
          processing={processing} onStart={onStart} onStop={onStop}
        />
      </div>

      {showActions && (
        <div className={styles.actions}>
          <button className={styles.actionBtn} onClick={onRetryVoice}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
            </svg>
            Retry last recording
          </button>
          <button className={`${styles.actionBtn} ${styles.actionBtnDanger}`} onClick={onNewSession}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14H6L5 6"/>
              <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
            </svg>
            New session
          </button>
        </div>
      )}

      <div className={styles.sidebarFooter}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="12" height="12" style={{flexShrink:0, marginTop:1}}>
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        For clinical documentation only. Not a substitute for professional judgement.
      </div>
    </aside>
  );
}