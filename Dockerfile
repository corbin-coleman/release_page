FROM python:3-alpine

RUN mkdir release_page
WORKDIR release_page
RUN mkdir templates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY templates/ ./templates
COPY get_release.py .

CMD ["python", "get_release.py"]