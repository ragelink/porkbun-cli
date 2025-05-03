FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
# Install the package in development mode
RUN pip install -e .

ENTRYPOINT ["python", "-m", "porkbun.cli"]
