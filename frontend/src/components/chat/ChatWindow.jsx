/**
 * components/Chat/ChatWindow.jsx
 * --------------------------------
 * Right panel: header bar + scrollable conversation + status states.
 */

import { useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import styles from "./ChatWindow.module.css";

export function ChatWindow({ conversation, processing, error }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation, processing]);

  const isEmpty = conversation.length === 0 && !processing && !error;

  return (
    <div className={styles.panel}>
      {/* Top bar */}
      <div className={styles.topBar}>
        <div className={styles.topBarTitle}>Transcript</div>
        <div className={styles.topBarMeta}>
          {conversation.length > 0
            ? `${conversation.length} turn${conversation.length !== 1 ? "s" : ""} recorded`
            : "No turns yet"}
        </div>
      </div>

      {/* Messages */}
      <main className={styles.messages}>
        {isEmpty && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8"  y1="23" x2="16" y2="23"/>
              </svg>
            </div>
            <p className={styles.emptyTitle}>No transcript yet</p>
            <p className={styles.emptyBody}>
              Press the record button in the sidebar to begin.<br/>
              The first voice heard becomes the Doctor; the second the Patient.
            </p>
          </div>
        )}

        {conversation.map((turn, i) => (
          <ChatMessage key={i} {...turn} />
        ))}

        {processing && (
          <div className={styles.processingRow}>
            <div className={styles.processingPill}>
              <span className={styles.spinner} />
              Analysing audio…
            </div>
          </div>
        )}

        {error && (
          <div className={styles.errorRow}>
            <div className={styles.errorPill}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8"  x2="12"    y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {error}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>
    </div>
  );
}