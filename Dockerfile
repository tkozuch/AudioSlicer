FROM python:3.6.3

WORKDIR /code
COPY requirements.txt /code/
COPY --from=mwader/static-ffmpeg:4.3.2 /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg:4.3.2 /ffprobe /usr/local/bin/
RUN pip install -r requirements.txt

COPY . /code/
