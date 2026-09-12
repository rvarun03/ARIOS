from urllib.parse import urlparse,parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from schemas.ingestion import IngestionOutput

def extract_video_id(url:str)-> str:

    parsed_url=urlparse(url)

    hostname=parsed_url.hostname

    if hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
        query_params= parse_qs(parsed_url.query)

        video_id = query_params.get("v")

        if video_id:
            return video_id[0]

    if hostname == "youtu.be":
        return parsed_url.path.strip("/")

    raise ValueError("Invalid YouTube URL")

def fetch_transcript(video_url:str)->str:
    """
    Fetch transcript text from YouTube using video_id.
    """

    api=YouTubeTranscriptApi()
    transcript=api.fetch(video_url)

    segments=[]

    for item in transcript:
        text=item.text
        start=float(item.start)
        duration=float(item.duration)
        end=start + duration

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


def ingest_youtube(url:str)->IngestionOutput:
    """
    Main YouTube ingestion function.
    Converts YouTube URL into ARIOS IngestionOutput.
    """

    try:
        video_id = extract_video_id(url)

        transcript_result = fetch_transcript(video_id)

        raw_text = transcript_result["raw_text"]
        segments = transcript_result["segments"]

        if not raw_text:
            raise ValueError("Transcript was fetched but raw text is empty")

        return IngestionOutput(
                source_type="youtube",
                source_url=url,
                title=f"YouTube Video - {video_id}",
                raw_text=raw_text,
                metadata={
                    "video_id": video_id,
                    "transcript_available": True,
                    "segment_count": len(segments),
                    "raw_text_length": len(raw_text),
                    "first_segment": segments[0] if segments else None,
                    "last_segment": segments[-1] if segments else None
                }
            )    

    except Exception as error:
        return IngestionOutput(
            source_type="youtube",
            source_url=url,
            title="YouTube Video",
            raw_text="",
            metadata={
                "transcript_available": False,
                "error": str(error)
            }
        )
    
