FROM public.ecr.aws/lambda/python:3.8

# problem with gui libs for opencv, maybe custom linux base would work? for now use opencv-python-headless
# RUN yum install gcc openssl-devel wget tar -y
# RUN yum install ffmpeg libsm6 libxext6  -y
# RUN yum install libXext libSM libXrender -y

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY vid_to_gif.py   ./
# COPY ./vids ./vids
CMD ["vid_to_gif.lambda_handler"]