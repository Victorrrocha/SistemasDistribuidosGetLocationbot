# Use the official image as a parent image.
FROM python3:3.8

WORKDIR /app
#
COPY ./src/ /app/src/

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 8080
# Run the specified command within the container.
CMD [ "python3", "/app/core.py" ]

