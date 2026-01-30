from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter

app = FastAPI()

def format_transcript(transcript):
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

    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    # 1)  manual subtitles EN
    try:
        transcript = transcript_list.find_transcript(["en"])
        return transcript.fetch()
    except:
        pass

    # 2) auto-gen subtitles EN
    try:
        transcript = transcript_list.find_generated_transcript(["en"])
        return transcript.fetch()
    except:
        pass
    # 3) Manual RU -> translate to EN
    try:
        transcript = transcript_list.find_transcript(["ru"])
        return transcript.translate("en").fetch()
    except:
        pass

    # 4) Auto-generated RU -> translate to EN
    try:
        transcript = transcript_list.find_generated_transcript(["ru"])
        return transcript.translate("en").fetch()
    except:
        pass

    # 5) if no subs – error
    raise NoTranscriptFound("English and Russian transcripts are not available")

@app.get("/transcript")
def transcript(id: str = Query(..., description="YouTube video ID")):
    try:
        fetched = fetch_english_transcript(id)
        formatted = format_transcript(fetched)
        return JSONResponse(content={"text": formatted})

    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts disabled for this video")

    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "service": "yt-transcript API (Hetzner V2)",
        "endpoints": {
            "/transcript?id=VIDEO_ID": "Get formatted English transcript",
        },
    }