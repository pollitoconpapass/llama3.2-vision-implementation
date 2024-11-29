import io
import os
import base64
import uvicorn
from groq import Groq
from PIL import Image
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile


app = FastAPI()

# === CONFIGURATION ===
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# === LOADING THE MODEL ===
MODEL = "llama-3.2-11b-vision-preview"

# === ENDODING FUNCTION ===
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format=image.format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# === ENDPOINT IMPLEMENTATION ===
@app.post("/ask-llama-3-2-vision")
async def answer_image_question(prompt: str = Form(...), image_file: UploadFile = File(...)):
    contents = await image_file.read()
    image = Image.open(io.BytesIO(contents))
    base64_image = encode_image(image)

    if not prompt:
        return {"error": "Please provide a prompt"}

    if not image:
        return {"error": "Please provide an image"}

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=MODEL,
        )
    except Exception as e:
        return {"error": str(e)}

    if not chat_completion:
        return {"error": "No answer was returned"}

    answer = chat_completion.choices[0].message.content

    if not answer:
        return {"error": "No answer was returned"}

    return {"answer": answer}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)