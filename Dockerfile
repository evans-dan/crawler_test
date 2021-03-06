#base image
FROM ubuntu:20.04
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

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
ENTRYPOINT ["python3", "./crawler_test.py"]
#CMD [ "/usr/bin/python3", "./crawler_test.py" ]
