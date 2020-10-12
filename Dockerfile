#base image
FROM ubuntu:20.04

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
#RUN pip3 install -r requirements.txt
RUN pip install -r requirements.txt

# put the local src directory to the cwd
COPY crawler_test.py .

# set the port to use
EXPOSE 5000

# run the container
CMD [ "/usr/bin/python3", "./code/crawler_test.py" ]
