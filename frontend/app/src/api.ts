import type {
  SessionCreateOut,
  TurnOut,
  GuessOut,
  ConfirmOut,
  SuggestOut,
  AnswerValue,
} from './types';

const BASE = '';

async function req<T>(path: string, method: string, token: string | null, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${method} ${path} → ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  createSession: () => req<SessionCreateOut>('/oracle/session', 'POST', null, {}),
  answer: (token: string, attr_idx: number, answer: AnswerValue) =>
    req<TurnOut>('/oracle/answer', 'POST', token, { attr_idx, answer }),
  giveUp: (token: string) => req<GuessOut>('/oracle/give-up', 'POST', token, {}),
  confirm: (token: string, correct: boolean, actual_track_id?: string) =>
    req<ConfirmOut>('/oracle/confirm', 'POST', token, { correct, actual_track_id: actual_track_id ?? null }),
  suggest: (token: string, title: string, artist: string) =>
    req<SuggestOut>('/oracle/suggest', 'POST', token, { title, artist, spotify_track_id: null }),
};
