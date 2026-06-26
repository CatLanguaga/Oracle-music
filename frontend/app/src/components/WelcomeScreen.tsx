import { NyotaGlyph } from './NyotaGlyph';

interface Props {
  onStart: () => void;
  busy?: boolean;
  nTracks?: number;
}

export function WelcomeScreen({ onStart, busy, nTracks }: Props) {
  return (
    <section className="scene">
      <div className="frame" style={{ textAlign: 'center' }}>
        <div className="eyebrow">
          Akinator <span className="dot" /> Versión Beta
        </div>
        <NyotaGlyph withStars />
        <h1 className="title">
          Piensa una canción.
          <br />
          <em>Yo la nombraré.</em>
        </h1>
        <p
          className="lede"
          style={{ marginLeft: 'auto', marginRight: 'auto', textAlign: 'center' }}
        >
          Te haré preguntas. Tú responderás con honestidad o duda. En menos de veinticinco
          respuestas, este oráculo dirá tu canción en voz alta.
        </p>
        <button
          className="btn primary"
          onClick={onStart}
          disabled={busy}
          style={{ margin: '8px auto 0', minWidth: 240, justifyContent: 'center' }}
        >
          <span>{busy ? 'Invocando…' : 'Comenzar el rito'}</span>
          <span className="key">↵</span>
        </button>
        {nTracks ? (
          <p className="footnote">de {nTracks.toLocaleString('es')} canciones en el grimorio</p>
        ) : null}
      </div>
    </section>
  );
}
