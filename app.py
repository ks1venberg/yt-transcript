from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = FastAPI()

def format_transcript(transcript):
    logging.info("Formatting transcript")
    formatter = TextFormatter()
    return formatter.format_transcript(transcript)


def fetch_english_transcript(video_id: str):
    """
    Returns EN subtitles
    fallback:
      1) manual subtitles EN
      2) auto-gen subtitles EN
      3) if no subs – error
    """

    logging.info("fetch_english_transcript, video_id=%s", video_id)

    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    # 1)  manual subtitles EN
    try:
        transcript = transcript_list.find_transcript(["en"])
        logging.info("EN transcript fetched, video_id=%s", video_id)
        return transcript.fetch()
    
    except TranscriptsDisabled:
        logging.warning(
            "TranscriptsDisabled for EN, video_id=%s",
            video_id,
        )

    except NoTranscriptFound:
        logging.warning(
            "NoTranscriptFound for EN, video_id=%s",
            video_id,
        )

    # 2) auto-gen subtitles EN
    try:
        transcript = transcript_list.find_generated_transcript(["en"])
        return transcript.fetch()
    
    except NoTranscriptFound:
        logging.warning(
            "No auto-generated EN transcript, video_id=%s",
            video_id,
        )

    # 3) Manual RU -> translate to EN
    try:
        logging.info("Trying manual translate ru-en")
        transcript = transcript_list.find_transcript(["ru"])
        return transcript.translate("en").fetch()
    
    except Exception:
        logging.warning(
            "Manual translate ru-en failed for video_id=%s",
            video_id)

    # 4) Auto-generated RU -> translate to EN
    try:
        logging.info("Trying to translate auto-generated ru")
        transcript = transcript_list.find_generated_transcript(["ru"])
        return transcript.translate("en").fetch()
    
    except Exception:
        logging.warning(
            "Auto-generated ru translate to en failed, video_id=%s",
            video_id,
        )

    # 5) if no subs – error
    logging.error(
        "No English or Russian transcripts available, video_id=%s",
        video_id,
    )
    raise NoTranscriptFound("English and Russian transcripts are not available")

@app.get("/transcript")
def transcript(id: str = Query(..., description="YouTube video ID")):

    logging.info("App has started for video_id=%s", id)

    try:
        fetched = fetch_english_transcript(id)
    
    except NoTranscriptFound as exc:
        logging.warning(
            "NoTranscriptFound for video_id=%s",
            id,
        )

        return {"video_id": id, "transcript": None}
    
    logging.info("Successfully fetched transcript, video_id=%s", id)

    formatted = format_transcript(fetched)
    return JSONResponse(content={"text": formatted})

@app.get("/")
def root():
    return {
        "service": "yt-transcript API (Hetzner V2)",
        "endpoints": {
            "/transcript?id=VIDEO_ID": "Get formatted English transcript",
        },
    }