import json

def handler(request):
    message = {
        "message": "Hey, there! There is a Python script for Vercel platform which transcribes video to text."
    }

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(message)
    }
