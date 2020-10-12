#base image
FROM python:3.8

#some info
LABEL maintainer="evans.dan@gmail.com"
LABEL version="0.1"
LABEL description="Custom Docker image to run the crawler_test.py \
file"

#set the working directory
WORKDIR /code

# set the package requirements for the script
COPY requirements.txt .

# install the requirements with pip
RUN pip3 install -r requirements.txt

# put the local src directory to the cwd
COPY crawler_test.py .

# run the container
CMD [ "python3", "./crawler_test.py" ]
