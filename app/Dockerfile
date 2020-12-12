# Use the official image as a parent image.
FROM python:3.8

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /app
#
COPY ./src/ /app/src/





# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 8080
# Run the specified command within the container.
CMD [ "python3", "src/core.py" ]

