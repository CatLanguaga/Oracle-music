import { useOracleSession } from './hooks/useOracleSession';
import { WelcomeScreen } from './components/WelcomeScreen';
import { QuestionCard } from './components/QuestionCard';
import { GuessReveal } from './components/GuessReveal';
import { ResultScreen } from './components/ResultScreen';

function App() {
  const s = useOracleSession();

  return (
    <>
      <nav className="nav">
        <div className="nav-title">
          Nyota <em>·</em> Oráculo Musical
        </div>
      </nav>
      <main className="stage">
        {s.phase.kind === 'idle' && (
          <WelcomeScreen onStart={s.start} nTracks={s.nTracks} />
        )}
        {s.phase.kind === 'loading' && (
          <section className="scene">
            <div className="frame" style={{ textAlign: 'center' }}>
              <p className="lede" style={{ margin: 0 }}>El oráculo medita…</p>
            </div>
          </section>
        )}
        {s.phase.kind === 'question' && (
          <QuestionCard
            question={s.phase.q}
            onAnswer={s.answer}
            onGiveUp={s.giveUp}
          />
        )}
        {s.phase.kind === 'guess' && (
          <GuessReveal guess={s.phase.g} onConfirm={s.confirm} />
        )}
        {s.phase.kind === 'result' && s.token && (
          <ResultScreen
            guess={s.phase.g}
            correct={s.phase.correct}
            token={s.token}
            onRestart={() => {
              s.reset();
              s.start();
            }}
          />
        )}
        {s.phase.kind === 'error' && (
          <section className="scene">
            <div className="frame">
              <div className="eyebrow" style={{ color: 'var(--color-accent)' }}>Error</div>
              <p className="lede">{s.phase.msg}</p>
              <button className="btn primary" onClick={s.reset}>
                <span>Reintentar</span>
                <span className="key">↵</span>
              </button>
            </div>
          </section>
        )}
      </main>
    </>
  );
}

export default App;
