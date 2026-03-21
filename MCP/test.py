# test_youtube.py
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

response = youtube.search().list(
    q="indie game dev",
    part="snippet",
    type="video",
    maxResults=3
).execute()

for item in response["items"]:
    print(item["snippet"]["title"])