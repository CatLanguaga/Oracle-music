import { useEffect } from 'react';
import { NyotaGlyph } from './NyotaGlyph';
import { ANSWER_LABELS, type AnswerValue, type QuestionOut } from '../types';

interface Props {
  question: QuestionOut;
  maxQuestions?: number;
  onAnswer: (v: AnswerValue) => void;
  onGiveUp: () => void;
  busy?: boolean;
}

const KEY_MAP: Record<string, AnswerValue> = {
  '1': 1.0,
  '2': 0.75,
  '3': 0.5,
  '4': 0.25,
  '5': 0.0,
};

export function QuestionCard({ question, maxQuestions = 25, onAnswer, onGiveUp, busy }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (busy) return;
      const v = KEY_MAP[e.key];
      if (v !== undefined) onAnswer(v);
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onAnswer, busy]);

  const pct = Math.min(100, Math.round((question.question_number / maxQuestions) * 100));

  return (
    <section className="scene">
      <div className="frame">
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 28, marginBottom: 8 }}>
          <NyotaGlyph size="sm" />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="eyebrow">
              Pregunta <b style={{ color: 'var(--color-ink)' }}>
                {String(question.question_number).padStart(2, '0')}
              </b>
              <span className="dot" />
              {question.candidates} candidatos
            </div>
            <p className="question-text">«{question.text}»</p>
          </div>
        </div>

        <div className="answers">
          {ANSWER_LABELS.map((a, i) => {
            const classes = ['btn'];
            if (a.variant === 'primary') classes.push('primary');
            if (a.variant === 'ghost') classes.push('ghost');
            if (a.variant === 'no') classes.push('no');
            const full = i === 0 || i === 2 || i === 4;
            if (full) classes.push('full');
            return (
              <button
                key={a.key}
                className={classes.join(' ')}
                onClick={() => onAnswer(a.value)}
                disabled={busy}
              >
                <span>{a.label}</span>
                <span className="key">{a.key}</span>
              </button>
            );
          })}
        </div>

        <div className="progress" aria-hidden="true">
          <span style={{ width: `${pct}%` }} />
        </div>
        <div className="meta">
          <span>
            <b>{question.question_number}</b> / {maxQuestions}
          </span>
          <span>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (!busy) onGiveUp();
              }}
              style={{ color: 'var(--color-muted)', textDecoration: 'underline dotted' }}
            >
              Rendirse
            </a>
          </span>
        </div>
      </div>
    </section>
  );
}
