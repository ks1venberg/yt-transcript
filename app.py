from fastapi import FastAPI, HTTPException, Query
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import JSONFormatter

app = FastAPI()

@app.get("/transcript")
def transcript(id: str = Query(..., description="YouTube video ID")):
    try:
        transcript = YouTubeTranscriptApi.fetch(id)
        formatter = JSONFormatter()
        json_transcript = formatter.format_transcript(transcript)
        return json_transcript

    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts disabled for this video")

    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))