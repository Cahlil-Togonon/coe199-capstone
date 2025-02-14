FROM python:3.9-slim

WORKDIR /coe199-capstone
COPY . .

RUN apt-get update && apt-get install libexpat1 -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "ph_main.py"]

# RUN apk add --no-cache \
#     proj-util \
#     gdal-dev \
#     build-base \
#     libffi-dev \
#     bash \
#     && python3 -m ensurepip \
#     && pip3 install --no-cache --upgrade pip setuptools wheel