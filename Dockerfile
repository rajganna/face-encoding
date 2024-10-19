FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Makefile /code/
COPY requirements.txt /code/
COPY app_loader.py /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./app /code/app

EXPOSE 8001

CMD ["uvicorn", "app_loader:app", "--host", "0.0.0.0", "--port", "8001"]
