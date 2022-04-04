#init a base image
FROM python:3

#present working directory 
WORKDIR /mindful
#copy the content into the working dir 
COPY . .
#dependecies of flask install
RUN python3 -m pip install -r requirements.txt

#define the command to start the container
CMD ["python","app.py"]

