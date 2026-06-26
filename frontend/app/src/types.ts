export interface TrackOut {
  track_id: string;
  title: string;
  artist: string;
  album: string | null;
  album_art_url: string | null;
  release_year: number | null;
}

export interface QuestionOut {
  attr_idx: number;
  attribute_key: string;
  text: string;
  question_number: number;
  candidates: number;
}

export interface GuessOut {
  track: TrackOut;
  prob: number;
  questions_asked: number;
  top_k: [TrackOut, number][];
}

export interface SessionCreateOut {
  token: string;
  session_id: string;
  n_tracks: number;
  n_attrs: number;
  question: QuestionOut;
}

export interface TurnOut {
  state: 'question' | 'guess';
  question: QuestionOut | null;
  guess: GuessOut | null;
}

export interface ConfirmOut {
  result: 'correct' | 'wrong' | 'gave_up';
}

export interface SuggestOut {
  suggestion_id: string;
  status: string;
}

export type AnswerValue = 1.0 | 0.75 | 0.5 | 0.25 | 0.0;

export const ANSWER_LABELS: { value: AnswerValue; label: string; variant: 'primary' | 'default' | 'ghost' | 'no'; key: string }[] = [
  { value: 1.0,  label: 'Sí, sin duda',     variant: 'primary', key: '1' },
  { value: 0.75, label: 'Probablemente sí', variant: 'default', key: '2' },
  { value: 0.5,  label: 'No lo sé',         variant: 'ghost',   key: '3' },
  { value: 0.25, label: 'Probablemente no', variant: 'default', key: '4' },
  { value: 0.0,  label: 'No',               variant: 'no',      key: '5' },
];
