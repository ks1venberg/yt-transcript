import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

def get_transcript(request):
    try:
        video_id = request.get("query", {}).get("id")

        if not video_id:
            return {
            "statusCode": 400,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": "missing id parameter"})
            }
    
        transcript = YouTubeTranscriptApi().fetch(video_id)
        json_formatted = JSONFormatter().format_transcript(transcript)
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json"},
            "body": json_formatted
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"transcript_error": str(e)})
        }