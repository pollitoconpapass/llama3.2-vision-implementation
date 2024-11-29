FROM python:3.12-slim

WORKDIR /app

COPY . . 

RUN pip install -r requirements.txt && \
    pip install --upgrade accelerate scipy transformers 

ENV GROQ_API_KEY=${GROQ_API_KEY}

EXPOSE 4040

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "4040"]