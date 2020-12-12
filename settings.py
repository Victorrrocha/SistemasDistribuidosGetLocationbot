import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_API_URL = os.getenv("BASE_API_URL")

TWITTER_CONSUMER_TOKEN_KEY = os.getenv("TWITTER_CONSUMER_TOKEN_KEY")
TWITTER_CONSUMER_TOKEN_SECRET = os.getenv("TWITTER_CONSUMER_TOKEN_SECRET")

TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")