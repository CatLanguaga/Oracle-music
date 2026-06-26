import { useState } from 'react';
import { api } from '../api';

interface Props {
  token: string;
  onDone: () => void;
}

export function SuggestionForm({ token, onDone }: Props) {
  const [title, setTitle] = useState('');
  const [artist, setArtist] = useState('');
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !artist.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      await api.suggest(token, title.trim(), artist.trim());
      setSent(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <>
        <p className="lede">Gracias. Tu canción ahora vive en el grimorio.</p>
        <button className="btn primary" onClick={onDone} style={{ marginTop: 8 }}>
          <span>Otra partida</span>
          <span className="key">↵</span>
        </button>
      </>
    );
  }

  return (
    <form className="suggest" onSubmit={submit}>
      <div className="field">
        <label htmlFor="s-title">Título</label>
        <input
          id="s-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Send My Love"
          autoFocus
        />
      </div>
      <div className="field">
        <label htmlFor="s-artist">Artista</label>
        <input
          id="s-artist"
          type="text"
          value={artist}
          onChange={(e) => setArtist(e.target.value)}
          placeholder="Adele"
        />
      </div>
      {error && (
        <p style={{ color: 'var(--color-accent)', fontSize: 13, marginBottom: 12 }}>{error}</p>
      )}
      <div style={{ display: 'flex', gap: 10, marginTop: 8, flexWrap: 'wrap' }}>
        <button className="btn primary" type="submit" disabled={busy || !title.trim() || !artist.trim()}>
          <span>{busy ? 'Enviando…' : 'Enviar al grimorio'}</span>
          <span className="key">↵</span>
        </button>
        <button className="btn ghost" type="button" onClick={onDone} disabled={busy}>
          <span>Saltar</span>
          <span className="key">esc</span>
        </button>
      </div>
    </form>
  );
}
