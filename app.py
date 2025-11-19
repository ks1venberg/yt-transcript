from fastapi import FastAPI, HTTPException, Query
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

    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

    # 1)  manual subtitles EN
    try:
        transcript = transcripts.find_manually_created_transcript(["en"]).fetch()
        return transcript
    except:
        pass

    # 2) auto-gen subtitles EN
    try:
        transcript = transcripts.find_generated_transcript(["en"]).fetch()
        return transcript
    except:
        pass

    # 3) if no subs – error
    raise NoTranscriptFound("No English transcript available")

@app.get("/transcript")
def transcript(id: str = Query(..., description="YouTube video ID")):
    try:
        transcript = fetch_english_transcript(id)
        formatted = format_transcript(transcript)
        return {"text": formatted}

    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts disabled for this video")

    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "service": "yt-transcript API (Railway)",
        "endpoints": {
            "/transcript?id=VIDEO_ID": "Get formatted English transcript",
        },
    }