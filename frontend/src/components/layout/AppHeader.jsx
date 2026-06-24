/**
 * components/Layout/AppHeader.jsx
 * --------------------------------
 * Top bar: product name, speaker legend, optional clear button.
 */

import styles from "./AppHeader.module.css";

export function AppHeader({ hasConversation, onClear }) {
  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.title}>MedTranscribe</span>
        <span className={styles.subtitle}>Clinical conversation transcript</span>
      </div>

      <div className={styles.right}>
        <div className={styles.legend}>
          <span className={`${styles.legendItem} ${styles.legendDoctor}`}>
            <span className={styles.legendDot} /> Doctor
          </span>
          <span className={`${styles.legendItem} ${styles.legendPatient}`}>
            <span className={styles.legendDot} /> Patient
          </span>
        </div>

        {hasConversation && (
          <button className={styles.clearBtn} onClick={onClear} title="Clear transcript">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14H6L5 6"/>
              <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
            </svg>
          </button>
        )}
      </div>
    </header>
  );
}