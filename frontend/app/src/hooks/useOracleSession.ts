import { useCallback, useState } from 'react';
import { api } from '../api';
import type { QuestionOut, GuessOut, AnswerValue } from '../types';

type Phase =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'question'; q: QuestionOut }
  | { kind: 'guess'; g: GuessOut }
  | { kind: 'result'; correct: boolean; g: GuessOut }
  | { kind: 'error'; msg: string };

export interface OracleSession {
  phase: Phase;
  token: string | null;
  sessionId: string | null;
  nTracks: number;
  start: () => Promise<void>;
  answer: (v: AnswerValue) => Promise<void>;
  giveUp: () => Promise<void>;
  confirm: (correct: boolean, actualId?: string) => Promise<void>;
  reset: () => void;
}

export function useOracleSession(): OracleSession {
  const [phase, setPhase] = useState<Phase>({ kind: 'idle' });
  const [token, setToken] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [nTracks, setNTracks] = useState<number>(0);

  const start = useCallback(async () => {
    setPhase({ kind: 'loading' });
    try {
      const s = await api.createSession();
      setToken(s.token);
      setSessionId(s.session_id);
      setNTracks(s.n_tracks);
      setPhase({ kind: 'question', q: s.question });
    } catch (e) {
      setPhase({ kind: 'error', msg: (e as Error).message });
    }
  }, []);

  const answer = useCallback(
    async (v: AnswerValue) => {
      if (!token || phase.kind !== 'question') return;
      const prev = phase.q;
      setPhase({ kind: 'loading' });
      try {
        const turn = await api.answer(token, prev.attr_idx, v);
        if (turn.state === 'guess' && turn.guess) {
          setPhase({ kind: 'guess', g: turn.guess });
        } else if (turn.state === 'question' && turn.question) {
          setPhase({ kind: 'question', q: turn.question });
        } else {
          setPhase({ kind: 'error', msg: 'unexpected turn payload' });
        }
      } catch (e) {
        setPhase({ kind: 'error', msg: (e as Error).message });
      }
    },
    [token, phase]
  );

  const giveUp = useCallback(async () => {
    if (!token) return;
    setPhase({ kind: 'loading' });
    try {
      const g = await api.giveUp(token);
      setPhase({ kind: 'guess', g });
    } catch (e) {
      setPhase({ kind: 'error', msg: (e as Error).message });
    }
  }, [token]);

  const confirm = useCallback(
    async (correct: boolean, actualId?: string) => {
      if (!token || phase.kind !== 'guess') return;
      const g = phase.g;
      try {
        await api.confirm(token, correct, actualId);
        setPhase({ kind: 'result', correct, g });
      } catch (e) {
        setPhase({ kind: 'error', msg: (e as Error).message });
      }
    },
    [token, phase]
  );

  const reset = useCallback(() => {
    setPhase({ kind: 'idle' });
    setToken(null);
    setSessionId(null);
  }, []);

  return { phase, token, sessionId, nTracks, start, answer, giveUp, confirm, reset };
}
