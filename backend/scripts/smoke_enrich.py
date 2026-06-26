"""Smoke test: end-to-end enrichment of a single known track."""
from __future__ import annotations

from backend.enrichment import gemini_enricher, lastfm_enricher, spotify_enricher


def main() -> None:
    track = spotify_enricher.fetch_track("7tFiyTwD0nx5a1eklYtX2J")  # Bohemian Rhapsody
    print(f"[spotify] {track['title']} - {track['artist']} ({track['release_year']})")

    lf = lastfm_enricher.enrich_track(track["artist"].split(",")[0], track["title"])
    print(f"[lastfm] listeners={lf['listeners']:,}  tags={len(lf['tags'])}")
    print(f"  top tags: {', '.join(t for t,_ in lf['tags'][:8])}")
    print(f"  tag-mapped attrs ({len(lf['attributes'])}):")
    for k, v in sorted(lf["attributes"].items(), key=lambda x: -x[1])[:10]:
        print(f"    {k:30s} {v:.2f}")

    attrs = gemini_enricher.estimate_attributes(
        title=track["title"],
        artist=track["artist"],
        year=track["release_year"],
        album=track["album"],
        tags=lf["tags"],
        listeners=lf["listeners"],
    )
    print(f"[gemini] {len(attrs)} attrs returned")
    for k, v in sorted(attrs.items(), key=lambda x: -x[1])[:15]:
        print(f"    {k:30s} {v:.2f}")


if __name__ == "__main__":
    main()
