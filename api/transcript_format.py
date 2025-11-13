from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/transcript_format', methods=['GET'])
def get_transcript():
    video_id = request.args.get('id')
    formatter = JSONFormatter()
    ytt_api = YouTubeTranscriptApi()

    if not video_id:
        return jsonify({"error_no_id": "missing 'id' parameter"}), 400

    try:
	      transcript = ytt_api.fetch(video_id)
	      json_formatted = formatter.format_transcript(transcript)
	      return json_formatted
    except Exception as e:
        return jsonify({"transcript_error": str(e)}), 500
