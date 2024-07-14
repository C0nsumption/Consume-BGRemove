from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import aiofiles
import io
import os
import numpy as np
import bg_remover
import asyncio
import json
from functools import lru_cache

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessingParams(BaseModel):
    tolerance: int = 30
    blur_radius: float = 2.0
    mode: str = "simple"
    refine: bool = False
    color: str

# In-memory cache for processed images
image_cache = {}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    async with aiofiles.open("temp_image.png", 'wb') as out_file:
        await out_file.write(contents)
    image = Image.open(io.BytesIO(contents))
    # Perform initial processing
    initial_result = bg_remover.remove_background(image, 255, 255, 255)  # Default white background
    initial_result.save("initial_processed.png")
    return {"status": "Image uploaded and initially processed"}

@lru_cache(maxsize=100)
def process_image_cached(params_str):
    params = json.loads(params_str)
    image = Image.open("temp_image.png")
    r, g, b = map(int, params['color'].split(','))
    result = bg_remover.remove_background(
        image, r, g, b, 
        tolerance=params['tolerance'],
        blur_radius=params['blur_radius'],
        mode=params['mode'],
        refine=params['refine']
    )
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            params = json.loads(data)
            
            # Process image with new parameters
            params_str = json.dumps(params, sort_keys=True)
            result = process_image_cached(params_str)
            
            # Send low-res preview
            preview = result.copy()
            preview.thumbnail((150, 150))  # Reduce size more aggressively
            preview_bytes = io.BytesIO()
            preview.save(preview_bytes, format='PNG')
            await websocket.send_bytes(preview_bytes.getvalue())
            
            # Send full-res image
            full_res_bytes = io.BytesIO()
            result.save(full_res_bytes, format='PNG')
            await websocket.send_bytes(full_res_bytes.getvalue())
    except WebSocketDisconnect:
        print("WebSocket disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
