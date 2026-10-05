from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> dict:
    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    segments = []

    for item in transcript:
        text = item.text.strip()
        start = float(item.start)
        duration = float(item.duration)
        end = start + duration

        if not text:
            continue

        segments.append(
            {
                "text": text,
                "start": start,
                "duration": duration,
                "end": end
            }
        )

    raw_text = " ".join(
        segment["text"]
        for segment in segments
    )

    return {
        "raw_text": raw_text,
        "segments": segments
    }


def format_time(seconds: float) -> str:
    total_seconds = int(seconds)

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return f"{minutes:02d}:{seconds:02d}"


def build_timestamp_chunks(
    segments: list[dict],
    max_words: int = 350,
    overlap_segments: int = 2
) -> list[dict]:

    chunks = []

    current_segments = []
    current_word_count = 0

    for segment in segments:
        text = segment["text"]
        word_count = len(text.split())

        if current_segments and current_word_count + word_count > max_words:
            chunk_text = " ".join(
                item["text"]
                for item in current_segments
            )

            start_time = current_segments[0]["start"]
            end_time = current_segments[-1]["end"]

            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "chunk_text": chunk_text,
                    "word_count": len(chunk_text.split()),
                    "char_count": len(chunk_text),
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_time_display": format_time(start_time),
                    "end_time_display": format_time(end_time)
                }
            )

            if overlap_segments > 0:
                current_segments = current_segments[-overlap_segments:]
                current_word_count = sum(
                    len(item["text"].split())
                    for item in current_segments
                )
            else:
                current_segments = []
                current_word_count = 0

        current_segments.append(segment)
        current_word_count += word_count

    if current_segments:
        chunk_text = " ".join(
            item["text"]
            for item in current_segments
        )

        start_time = current_segments[0]["start"]
        end_time = current_segments[-1]["end"]

        chunks.append(
            {
                "chunk_index": len(chunks),
                "chunk_text": chunk_text,
                "word_count": len(chunk_text.split()),
                "char_count": len(chunk_text),
                "start_time": start_time,
                "end_time": end_time,
                "start_time_display": format_time(start_time),
                "end_time_display": format_time(end_time)
            }
        )

    return chunks


video_id = "aircAruvnKk"

transcript_result = fetch_transcript(video_id)

segments = transcript_result["segments"]

chunks = build_timestamp_chunks(
    segments=segments,
    max_words=350,
    overlap_segments=2
)

print("TOTAL SEGMENTS:")
print(len(segments))

print("\nTOTAL TIMESTAMP CHUNKS:")
print(len(chunks))

for chunk in chunks[:3]:
    print("\n-------------------------")
    print("CHUNK INDEX:")
    print(chunk["chunk_index"])

    print("\nTIME RANGE:")
    print(chunk["start_time_display"], "-", chunk["end_time_display"])

    print("\nWORD COUNT:")
    print(chunk["word_count"])

    print("\nTEXT PREVIEW:")
    print(chunk["chunk_text"][:1000])