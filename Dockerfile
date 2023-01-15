FROM python:3.10-slim

ADD main.py .
ADD .env .

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
