FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt
ENV PORT=8080
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--timeout", "600"]
