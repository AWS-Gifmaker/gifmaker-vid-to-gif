import uuid
import cv2
import numpy as np
import boto3
import imageio
import os

from urllib.parse import unquote_plus
from matplotlib import pyplot as plt
from datetime import datetime

LOCAL_MODE = False

TARGET_BUCKET = 'gifmaker-gifs'

VIDEO_FRAMES_USED = 20

if not LOCAL_MODE:
    s3_client = boto3.client('s3')


def create_gif(source_path: str, target_path: str):
    print(f"START Analyzing new video, path: {source_path}")

    cap = cv2.VideoCapture(source_path)
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vid_fps = int(cap.get(cv2.CAP_PROP_FPS))

    print("Vide stats:")
    print(f"total_frames: {total_frames}")
    print(f"frame_w: {frame_w}")
    print(f"frame_h: {frame_h}")
    print(f"vid_fps: {vid_fps}")
    print(f"DURATION: {total_frames / vid_fps}")

    # used_frames_indices = get_used_frames_indices(total_frames)
    # print(f"Using frames: {used_frames_indices}")

    performance_per_frame = []

    buf = np.empty((VIDEO_FRAMES_USED, frame_h, frame_w, 3), np.dtype('uint8'))
    fc = 0

    while fc < VIDEO_FRAMES_USED:
        ret, img_buffer = cap.read()

        frame_proc_start = datetime.now()
        print(f"Handling frame {fc}, time: {frame_proc_start}")

        # by default cv2 video reads in BGR
        img_buffer = cv2.cvtColor(img_buffer, cv2.COLOR_BGR2RGB)
        # plt.imshow(img_buffer)
        # plt.show()

        buf[fc] = img_buffer

        frame_proc_end = datetime.now()
        proc_delta = (frame_proc_end - frame_proc_start).total_seconds()
        print(f"Frame {fc} handled, total time: {proc_delta} seconds")
        performance_per_frame.append(proc_delta)
        fc += 1

    cap.release()

    imageio.mimsave(target_path, buf[:VIDEO_FRAMES_USED], format='.gif')

    print(
        f"END, frames covered: {VIDEO_FRAMES_USED}/{total_frames}, average time per frame: {sum(performance_per_frame) / len(performance_per_frame)} seconds")
    print(f"Saved GIF in {target_path}")


def lambda_handler(event: dict, context):
    print(f"Handler called, received event: {event}")
    if not LOCAL_MODE:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            print(f"Input info: bucket={bucket}, key={key}")

            tmpkey = key.replace('/', '')
            download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
            upload_path = '/tmp/gif-{}'.format(tmpkey)
            print(f"Downloading gif object to: {download_path}")
            s3_client.download_file(bucket, key, download_path)
            print("Download completed.")

            # assumes short video bucket keys dont include .smth extension
            target_gif_object_key = key.split('/')[-1]
            target_gif_object_key = ".".join(target_gif_object_key.split('.')[:-1]) + ".gif"
            # assumes source videos are under a directory like /raw-videos/object-hash
            # target_gif_object_key = key.split('/')[-1]

            print("Calling gif creator method.")
            create_gif(download_path, upload_path)

            print(f"Saving to target s3 - bucket={TARGET_BUCKET}, object key = {target_gif_object_key}")
            s3_client.upload_file(upload_path, TARGET_BUCKET, target_gif_object_key)

            print(f"Cleaning up tmp files from {download_path}, {upload_path}")
            os.remove(download_path)
            os.remove(upload_path)

    print("Lambda handler closing")


def main():
    key = "vid111.mov"
    # target_gif_name = ".".join(source_obj_name.split('.')[:-1])  # + ".gif"

    target_gif_object_key = key.split('/')[-1]
    target_gif_object_key = ".".join(key.split('.')[:-1]) + ".gif"
    # target_gif_name = "abcd"

    create_gif(key, target_gif_object_key)


if __name__ == "__main__":
    main()
