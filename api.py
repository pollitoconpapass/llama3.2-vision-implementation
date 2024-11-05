import io
import torch 
import uvicorn
from PIL import Image
from fastapi import FastAPI, File, Form, UploadFile
from transformers import (
    MllamaForConditionalGeneration,
    AutoProcessor,
    GenerationConfig,
)

app = FastAPI()

# === LOADING THE MODEL ===
model_id = "meta-llama/Llama-3.2-11B-Vision" # -> model name
model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
# model.to('cpu')
model.gradient_checkpointing_enable()
processor = AutoProcessor.from_pretrained(model_id)


# === ENDPOINT IMPLEMENTATION ===
@app.post("/ask-llama-3-2-vision")
async def answer_image_question(prompt: str = Form(...), image_file: UploadFile = File(...)):
  contents = await image_file.read()
  image = Image.open(io.BytesIO(contents))
  prompt = f"<|image|><|begin_of_text|>{prompt}" # -> special prompt style

  inputs = processor(image, prompt, return_tensors="pt").to("cpu") # -> assigned to the cpu (change it in case you have GPU machine)
  generation_config = GenerationConfig.from_pretrained(model_id)
  generation_config.gradient_checkpointing = True
  output = model.generate(**inputs, generation_config=generation_config, 
                          max_new_tokens=250)

  return processor.decode(output[0])  # -> final response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)