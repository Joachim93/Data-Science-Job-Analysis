FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/

EXPOSE 8501

CMD ["streamlit", "run", "src/webapp.py"]