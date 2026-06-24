import styles from "./ChatMessage.module.css";

function fmt(s) {
  return `${Math.floor(s/60).toString().padStart(2,"0")}:${Math.floor(s%60).toString().padStart(2,"0")}`;
}

export function ChatMessage({ speaker, text, start, end }) {
  const isDoctor = speaker === "Doctor";
  return (
    <div className={`${styles.row} ${isDoctor ? styles.rowDoctor : styles.rowPatient}`}>
      <div className={`${styles.avatar} ${isDoctor ? styles.avatarDoctor : styles.avatarPatient}`}>
        {isDoctor ? "Dr" : "Pt"}
      </div>
      <div className={`${styles.bubble} ${isDoctor ? styles.bubbleDoctor : styles.bubblePatient}`}>
        <span className={styles.speaker}>{speaker}</span>
        <p className={styles.text}>{text}</p>
        <span className={styles.timestamp}>{fmt(start)} – {fmt(end)}</span>
      </div>
    </div>
  );
}