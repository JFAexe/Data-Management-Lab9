FROM python:3.10.6-slim-buster AS builder
COPY requirements.txt .
RUN pip3 install --user --upgrade -r requirements.txt

FROM python:3.10.6-slim-buster
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local:$PATH
WORKDIR /app_for_db
ADD . /app_for_db
