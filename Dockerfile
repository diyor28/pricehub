FROM python:3.10
WORKDIR /app
COPY prchb .
RUN pip install -r requirements.txt
CMD "bash"
