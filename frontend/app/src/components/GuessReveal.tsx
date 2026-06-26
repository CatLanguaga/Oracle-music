import type { GuessOut } from '../types';

interface Props {
  guess: GuessOut;
  onConfirm: (correct: boolean) => void;
  busy?: boolean;
}

export function GuessReveal({ guess, onConfirm, busy }: Props) {
  const { track, prob, questions_asked, top_k } = guess;
  const pct = Math.round(prob * 100);

  return (
    <section className="scene">
      <div className="frame">
        <div className="eyebrow">
          Tras <b style={{ color: 'var(--color-ink)' }}>{questions_asked}</b> preguntas
          <span className="dot" /> certeza {pct}%
        </div>

        <h1 className="title" style={{ fontSize: 42, marginBottom: 8 }}>
          Creo conocer
          <br />
          <em>tu canción.</em>
        </h1>

        <div className="track">
          <div className="cover" aria-hidden="true">
            {track.album_art_url ? (
              <img src={track.album_art_url} alt="" />
            ) : (
              <svg
                viewBox="0 0 160 160"
                width="100%"
                height="100%"
                style={{ background: 'var(--color-ink)', color: 'var(--color-paper)' }}
              >
                <circle cx="80" cy="80" r="42" fill="none" stroke="currentColor" strokeWidth="1" />
                <circle cx="80" cy="80" r="4" fill="currentColor" />
              </svg>
            )}
          </div>

          <div>
            <h2>{track.title}</h2>
            <p className="artist">{track.artist}</p>
            <p className="album">
              {[track.album, track.release_year].filter(Boolean).join(' · ')}
            </p>

            <div className="answers" style={{ marginTop: 24 }}>
              <button
                className="btn primary"
                onClick={() => onConfirm(true)}
                disabled={busy}
              >
                <span>Es esa</span>
                <span className="key">↵</span>
              </button>
              <button
                className="btn"
                onClick={() => onConfirm(false)}
                disabled={busy}
              >
                <span>No es esa</span>
                <span className="key">esc</span>
              </button>
            </div>
          </div>
        </div>

        {top_k.length > 1 && (
          <div className="topk" aria-label="Otras candidatas">
            <h4>Otras sospechas del oráculo</h4>
            <ol>
              {top_k.slice(1, 4).map(([t, p]) => (
                <li key={t.track_id}>
                  <span>
                    <b>{t.title}</b>{' '}
                    <span style={{ color: 'var(--color-muted)', fontStyle: 'italic' }}>
                      · {t.artist}
                    </span>
                  </span>
                  <span className="p">{(p * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </section>
  );
}
