FROM python:3.11-slim

WORKDIR /app

COPY setup.py README.md ./
COPY ai_logmaster/ ai_logmaster/

RUN pip install --no-cache-dir .

ENV HOME=/root

ENTRYPOINT ["logmaster"]
CMD ["--help"]
