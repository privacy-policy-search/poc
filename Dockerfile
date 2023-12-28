FROM public.ecr.aws/lambda/python:3.11

# Copy model directory into /var/task
ADD ./model ${LAMBDA_TASK_ROOT}/model/
# Copy data directory
ADD ./data ${LAMBDA_TASK_ROOT}/data/

# Copy `requirements.txt` into /var/task
COPY ./requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN python3 -m pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Copy function code into /var/task
COPY handler.py privacypolicyfinder.py embeddings.npy .env ${LAMBDA_TASK_ROOT}/

# Set the CMD to our handler
CMD ["handler.lambda_handler"]