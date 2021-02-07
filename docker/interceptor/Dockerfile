# setting Python as the base image.
FROM python:3.8

# setting the container working directory.
WORKDIR WAPT-Dataset-Collector/code

# copy the dependencies file to the wd.
COPY docker/interceptor/dependencies .

# installing dependencies. (dependencies will always be contained in the same dir of Dockerfile)
RUN pip3 install -r dependencies

# copy the content of src directory to the container working directory.
COPY src .

# run Python code.
ENTRYPOINT ["python3", "Interceptor.py"]
