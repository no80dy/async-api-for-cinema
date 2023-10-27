FROM python:3.11-alpine

WORKDIR /app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt requirements.txt

# install dependencies
RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornH11Worker", "main:app", "--host", "0.0.0.0", "--port", "8000"]
