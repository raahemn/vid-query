from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import NoTranscriptFound
from typing import Optional

def fetch_youtube_transcript(
    video_id: str,
    preferred_languages: list[str] = ["en"]
) -> Optional[str]:
    """
    Fetches the transcript for a given YouTube video ID.
    Returns the full text as a single string, or None if unavailable.
    """
    try:
        # transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)

        try:
            # Try to find a transcript in a preferred language
            transcript_obj = transcripts.find_transcript(preferred_languages)
            print(f"Using transcript in preferred language: {transcript_obj.language_code}")
            transcript = transcript_obj.fetch()

        except NoTranscriptFound:
            print("Preferred language not found. Trying fallback...")

            # Fall back to any available *generated* transcript
            if transcripts._generated_transcripts:
                fallback_obj = list(transcripts._generated_transcripts.values())[0]
                print(f"Using fallback transcript: {fallback_obj.language_code}")
                transcript = fallback_obj.fetch()
            else:
                print("No generated transcripts available.")
                return None

        # Convert the transcript object to text
        if transcript:
            if hasattr(transcript, "snippets"):
                # Custom object with .snippets attribute
                text = " ".join(snippet.text for snippet in transcript.snippets)
            elif isinstance(transcript, list):
                text = " ".join(chunk["text"] for chunk in transcript)
            elif hasattr(transcript, "to_list"):
                text = " ".join(chunk["text"] for chunk in transcript.to_list())
            else:
                raise TypeError("Unsupported transcript format")
            return text

        else:
            print("No transcript found.")
            return None

    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
