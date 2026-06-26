interface Props {
  size?: 'lg' | 'sm';
  thinking?: boolean;
  withStars?: boolean;
}

export function NyotaGlyph({ size = 'lg', thinking = true, withStars = false }: Props) {
  const cls = ['nyota', size === 'sm' ? 'sm' : '', thinking ? 'thinking' : '']
    .filter(Boolean)
    .join(' ');
  return (
    <svg
      className={cls}
      viewBox="0 0 100 100"
      fill="none"
      stroke="currentColor"
      strokeWidth={size === 'sm' ? 1.4 : 1.2}
      aria-hidden="true"
    >
      <path d="M 22 72 A 28 28 0 0 0 78 72 A 22 22 0 0 1 22 72 Z" />
      <path d="M 28 38 Q 50 18 72 38 Q 50 58 28 38 Z" />
      <circle className="iris" cx="50" cy="38" r="6" fill="currentColor" stroke="none" />
      {withStars && (
        <>
          <line x1="12" y1="20" x2="12" y2="26" />
          <line x1="9" y1="23" x2="15" y2="23" />
          <line x1="88" y1="20" x2="88" y2="26" />
          <line x1="85" y1="23" x2="91" y2="23" />
        </>
      )}
    </svg>
  );
}
