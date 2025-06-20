import os

def enforce_extension(path, allowed):
    ext = os.path.splitext(path)[1].lower()
    if ext not in allowed:
        raise ValueError(f"❌ Invalid extension '{ext}'. Allowed: {allowed}")
    return path
