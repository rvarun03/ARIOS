from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from schemas.ingestion import IngestionOutput


def extract_video_id(url:str) -> str:
    """"
       Extract the video id from the youtube url 
    """
    parsed_url= urlparse(url)

    if parsed_url.hostname in [
        "www.youtube.com",
        "youtube.com"
    ]:
        return parse_qs(parsed_url.query)["v"][0]
    
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    
    raise ValueError("Invalid YouTube URL")

def fetch_transcript(video_id:str) -> str:

    """"
        From the video id fetch the transcript
    """
    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)
    
    print(type(transcript))
    print(type(transcript[0]))
    print(transcript[0])

    raw_text = " ".join(
        item.text
        for item in transcript
    )
    return raw_text

def ingest_youtube(url:str) -> IngestionOutput:
    try:
        video_id= extract_video_id(url)
        raw_text= fetch_transcript(video_id)

        return IngestionOutput(
            source_type="youtube",
            source_url=url,
            title=None,
            raw_text=raw_text,
            metadata={
                "video_id": video_id,
                "length": len(raw_text)
            }
        )
    
    except Exception as e:
        return IngestionOutput(
            source_type="youtube",
            source_url=url,
            title=None,
            raw_text="",
            metadata={
                "error": str(e)
            }
        )