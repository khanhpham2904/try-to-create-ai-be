import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd

from config.settings import settings


@dataclass
class DatasetRow:
    timestamp: Optional[str]
    track: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    ms_played: Optional[str]


class DatasetContextService:
    def __init__(self, csv_path: Optional[str]) -> None:
        if csv_path is None:
            csv_path = settings.DATASET_CSV_PATH
        self.csv_path: Optional[Path] = Path(csv_path) if csv_path else None
        self._loaded: bool = False
        self._df: Optional[pd.DataFrame] = None

    def is_available(self) -> bool:
        return bool(self.csv_path and self.csv_path.exists() and self._loaded and isinstance(self._df, pd.DataFrame))

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # Build normalized columns based on actual CSV structure
        # Timestamp - try multiple possible column names
        timestamp_cols = [c for c in df.columns if c in {"ts", "endtime", "end_time", "timestamp", "time", "date"}]
        if timestamp_cols:
            df["timestamp"] = df[timestamp_cols[0]]
        else:
            df["timestamp"] = None

        # Track name - try multiple possible column names
        track_cols = [c for c in df.columns if c in {"track_name", "trackname", "track", "song", "title"}]
        if track_cols:
            df["track"] = df[track_cols[0]]
        else:
            df["track"] = None

        # Artist name - try multiple possible column names
        artist_cols = [c for c in df.columns if c in {"artist_name", "artistname", "artist", "singer"}]
        if artist_cols:
            df["artist"] = df[artist_cols[0]]
        else:
            df["artist"] = None

        # Album name - try multiple possible column names
        album_cols = [c for c in df.columns if c in {"album_name", "albumname", "album"}]
        if album_cols:
            df["album"] = df[album_cols[0]]
        else:
            df["album"] = None

        # Milliseconds played / duration - try multiple possible column names
        ms_cols = [c for c in df.columns if c in {"ms_played", "msplayed", "duration_ms"}]
        if ms_cols:
            df["ms_played"] = df[ms_cols[0]]
        else:
            df["ms_played"] = None

        # Precompute a lowercase haystack for quick contains checks
        def _join_lower(row) -> str:
            parts = [
                str(row.get("track", "") or ""),
                str(row.get("artist", "") or ""),
                str(row.get("album", "") or ""),
            ]
            return " ".join(parts).strip().lower()

        df["haystack"] = df.apply(_join_lower, axis=1)
        return df[["timestamp", "track", "artist", "album", "ms_played", "haystack"]]

    def load_dataset(self) -> bool:
        if not self.csv_path or not self.csv_path.exists():
            self._loaded = False
            self._df = None
            return False

        # Try reading with robust defaults
        try_encodings = ["utf-8", "utf-8-sig", "cp1252"]
        last_err: Optional[Exception] = None
        for enc in try_encodings:
            try:
                df = pd.read_csv(self.csv_path, encoding=enc, engine="python")
                self._df = self._normalize_columns(df)
                self._loaded = True
                return True
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
        # If all attempts failed
        self._loaded = False
        self._df = None
        return False

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords with improved logic for broader matching"""
        # Remove common stop words that don't help with music search
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those",
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "his", "hers", "ours", "theirs"
        }
        
        words = re.findall(r"[A-Za-z0-9']+", (text or "").lower())
        # Filter out stop words and very short words, but be more inclusive
        return [w for w in words if len(w) > 1 and w not in stop_words]

    def _is_music_related_query(self, query: str) -> bool:
        """Check if query is music-related to determine if we should return sample data"""
        music_keywords = {
            "song", "songs", "music", "track", "tracks", "artist", "artists", "album", "albums",
            "spotify", "listen", "listening", "played", "play", "plays", "favorite", "best", "top",
            "history", "data", "dataset", "records", "entries", "taste", "preference"
        }
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in music_keywords)

    def find_relevant(self, query: str, max_results: int = 12) -> List[DatasetRow]:  # Increased from 6 to 12
        if not self.is_available():
            if not self._loaded:
                self.load_dataset()
            if not self.is_available() or self._df is None:
                return []

        df = self._df
        assert df is not None

        # If it's a music-related query but no specific keywords match, return sample data
        if self._is_music_related_query(query):
            keywords = self._extract_keywords(query)
            if not keywords:
                # Return sample data for music-related queries
                sample_size = min(max_results, len(df))
                sample_df = df.sample(n=sample_size, random_state=42)  # Fixed seed for consistency
                results: List[DatasetRow] = []
                for _, r in sample_df.iterrows():
                    results.append(
                        DatasetRow(
                            timestamp=str(r.get("timestamp") or "") or None,
                            track=str(r.get("track") or "") or None,
                            artist=str(r.get("artist") or "") or None,
                            album=str(r.get("album") or "") or None,
                            ms_played=str(r.get("ms_played") or "") or None,
                        )
                    )
                return results

        # Original keyword matching logic
        keywords = self._extract_keywords(query)
        if not keywords:
            return []

        # Score each row by number of keywords present in haystack
        def score_row(hay: str) -> int:
            if not hay:
                return 0
            return sum(1 for k in keywords if k in hay)

        scores = df["haystack"].apply(score_row)
        mask = scores > 0
        if not mask.any():
            return []

        top = df.loc[mask].assign(_score=scores[mask]).sort_values("_score", ascending=False).head(max_results)
        results: List[DatasetRow] = []
        for _, r in top.iterrows():
            results.append(
                DatasetRow(
                    timestamp=str(r.get("timestamp") or "") or None,
                    track=str(r.get("track") or "") or None,
                    artist=str(r.get("artist") or "") or None,
                    album=str(r.get("album") or "") or None,
                    ms_played=str(r.get("ms_played") or "") or None,
                )
            )
        return results

    def get_relevant_context(self, query: str, char_limit: int = 1500) -> Optional[str]:  # Increased from 1200 to 1500
        matches = self.find_relevant(query)
        if not matches:
            return None

        lines: List[str] = ["Spotify listening history context (top matches):"]
        for r in matches:
            parts: List[str] = []
            if r.timestamp:
                parts.append(str(r.timestamp))
            title = r.track or "Unknown Track"
            artist = r.artist or "Unknown Artist"
            parts.append(f"'{title}' by {artist}")
            if r.album:
                parts.append(f"album: {r.album}")
            if r.ms_played:
                parts.append(f"played_ms: {r.ms_played}")
            lines.append(" - " + " | ".join(parts))

        context = "\n".join(lines)
        if len(context) > char_limit:
            context = context[: char_limit - 3] + "..."
        return context


# Initialize singleton service with settings
_csv_path = settings.DATASET_CSV_PATH if hasattr(settings, "DATASET_CSV_PATH") else None
if _csv_path:
    _csv_path = os.path.expandvars(_csv_path)

dataset_service = DatasetContextService(_csv_path)

# Eager load on startup if enabled
if getattr(settings, "DATASET_ENABLED", True):
    dataset_service.load_dataset()
