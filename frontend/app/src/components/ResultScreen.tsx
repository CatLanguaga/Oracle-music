import type { GuessOut } from '../types';
import { NyotaGlyph } from './NyotaGlyph';
import { SuggestionForm } from './SuggestionForm';

interface Props {
  guess: GuessOut;
  correct: boolean;
  token: string;
  onRestart: () => void;
}

export function ResultScreen({ guess, correct, token, onRestart }: Props) {
  if (correct) {
    return (
      <section className="scene">
        <div className="frame" style={{ textAlign: 'center' }}>
          <div className="eyebrow" style={{ color: 'var(--color-accent)' }}>
            El oráculo no se equivocó
          </div>
          <NyotaGlyph withStars />
          <h1 className="title">
            <em>{guess.track.title}</em>
          </h1>
          <p className="lede" style={{ marginLeft: 'auto', marginRight: 'auto', textAlign: 'center' }}>
            de {guess.track.artist}. Adivinada en {guess.questions_asked} preguntas.
          </p>

          <div className="stat-row">
            <div className="stat accent">
              <span className="n">{guess.questions_asked}</span>
              <span className="l">Preguntas</span>
            </div>
            <div className="stat">
              <span className="n">{Math.round(guess.prob * 100)}%</span>
              <span className="l">Certeza final</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn primary" onClick={onRestart}>
              <span>Otra canción</span>
              <span className="key">↵</span>
            </button>
          </div>

          <p className="footnote">tu sigilo del día queda en el grimorio</p>
        </div>
      </section>
    );
  }

  return (
    <section className="scene">
      <div className="frame">
        <div className="eyebrow">
          El oráculo erró <span className="dot" /> cuenta tu canción
        </div>
        <h1 className="title">
          No supe
          <br />
          <em>nombrarla.</em>
        </h1>
        <p className="lede">
          Esta vez te escapaste del grimorio. Si me dices qué canción era, la agregaré para
          futuras invocaciones.
        </p>
        <SuggestionForm token={token} onDone={onRestart} />
      </div>
    </section>
  );
}
