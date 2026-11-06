import os

import uvicorn

from src.fastapi import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("bin.api:app", host="0.0.0.0", port=port, reload=True)
