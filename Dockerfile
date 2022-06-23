FROM python:3.9.5


WORKDIR /app


COPY python-requirements.txt /python-requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /python-requirements.txt


COPY . .