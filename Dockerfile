FROM edoburu/python-runner:latest

WORKDIR /app

ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
