import os

# Read DeepSeek API configuration from environment
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

def has_deepseek_key() -> bool:
    return bool(DEEPSEEK_API_KEY)
