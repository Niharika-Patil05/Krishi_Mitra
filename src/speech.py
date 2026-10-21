"""Speech via Sarvam AI: stt() for the mic recording, tts() to read the answer aloud."""
import base64
import io
import re
import wave

from src import config


def _client():
    from sarvamai import SarvamAI
    key = config.get_secret("SARVAM_API_KEY")
    if not key:
        raise RuntimeError("SARVAM_API_KEY not set")
    return SarvamAI(api_subscription_key=key)


def stt(audio_bytes: bytes, lang_code: str = "unknown") -> str:
    """WAV bytes -> transcript. lang_code e.g. 'mr-IN', or 'unknown' to auto-detect."""
    resp = _client().speech_to_text.transcribe(
        file=("audio.wav", audio_bytes, "audio/wav"),
        model=config.STT_MODEL,
        language_code=lang_code,
        request_options={"timeout_in_seconds": config.SPEECH_TIMEOUT_S},
    )
    return (resp.transcript or "").strip()


def split_text(text: str, limit: int = config.TTS_MAX_CHARS) -> list[str]:
    """Split on sentence ends (. ? ! ।) so each piece fits the TTS character limit."""
    parts, current = [], ""
    for sentence in re.split(r"(?<=[.?!।])\s+", text.strip()):
        while len(sentence) > limit:  # pathological sentence with no punctuation
            parts.append(sentence[:limit])
            sentence = sentence[limit:]
        if current and len(current) + len(sentence) + 1 > limit:
            parts.append(current)
            current = ""
        current = f"{current} {sentence}".strip()
    if current:
        parts.append(current)
    return parts


def _tts_once(text: str, lang_code: str) -> bytes:
    resp = _client().text_to_speech.convert(
        text=text,
        language_code=lang_code,
        model=config.TTS_MODEL,
        speaker=config.TTS_SPEAKER,
        output_audio_codec="wav",
        request_options={"timeout_in_seconds": config.SPEECH_TIMEOUT_S},
    )
    return base64.b64decode(resp.audios[0])  # API returns base64-encoded WAV


def _join_wavs(chunks: list[bytes]) -> bytes:
    """Concatenate WAV files that share the same format into one WAV."""
    out = io.BytesIO()
    with wave.open(out, "wb") as w_out:
        for i, data in enumerate(chunks):
            with wave.open(io.BytesIO(data)) as w_in:
                if i == 0:
                    w_out.setparams(w_in.getparams())
                w_out.writeframes(w_in.readframes(w_in.getnframes()))
    return out.getvalue()


def tts(text: str, lang_code: str = "mr-IN") -> bytes:
    """Text -> WAV bytes. Long text is split, synthesised piece by piece and joined."""
    pieces = split_text(text)
    if not pieces:
        raise ValueError("nothing to speak")
    wavs = [_tts_once(p, lang_code) for p in pieces]
    return wavs[0] if len(wavs) == 1 else _join_wavs(wavs)


if __name__ == "__main__":
    # Round trip: python -m src.speech  ->  writes test.wav, then transcribes it.
    sample = "हळदीची लागवड मे ते जून महिन्यात करावी."
    audio = tts(sample, "mr-IN")
    with open("test.wav", "wb") as f:
        f.write(audio)
    print(f"Wrote test.wav ({len(audio)} bytes)")
    print("Transcript:", stt(audio, "mr-IN"))
