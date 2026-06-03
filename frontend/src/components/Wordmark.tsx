interface WordmarkProps {
  size?: number;
}

export function Wordmark({ size = 22 }: WordmarkProps) {
  return (
    <span className="wordmark" style={{ fontSize: size }}>
      <span className="wm-text">Postit</span>
      <span className="wm-corner" />
    </span>
  );
}
