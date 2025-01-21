import cv2
import time
import os
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["video_metadata"]
collection = db["videos"]

# Function to record video
def record_video(camera_id, duration_minutes, save_directory):
    cap = cv2.VideoCapture(0)  # 0 for default camera
    if not cap.isOpened():
        print("Error: Cannot access the camera")
        return

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)

    file_name = f"{camera_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
    file_path = os.path.join(save_directory, file_name)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, frame_rate, 
                          (int(cap.get(3)), int(cap.get(4))))

    print(f"Recording video for {duration_minutes} minutes...")

    while datetime.now() < end_time:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    # Get file size in MB
    file_size = os.path.getsize(file_path) / (1024 * 1024)

    metadata = {
        "camera_id": camera_id,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": file_path,
        "file_size": round(file_size, 2),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Insert metadata into MongoDB
    collection.insert_one(metadata)
    print(f"Video saved and metadata stored: {metadata}")

    return metadata

# Function to fetch video metadata from MongoDB
def fetch_video_metadata(camera_id):
    metadata = collection.find_one({"camera_id": camera_id}, sort=[("created_at", -1)])
    if metadata:
        print(f"Fetched metadata: {metadata}")
        return metadata
    else:
        print("No video metadata found for the given camera ID.")
        return None

# Function to play video
def play_video(file_path):
    if not os.path.exists(file_path):
        print("Error: Video file not found")
        return

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print("Error: Cannot play the video")
        return

    print("Playing video...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video Playback', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit playback
            break

    cap.release()
    cv2.destroyAllWindows()

# Main function
if __name__ == "__main__":
    CAMERA_ID = "laptop_camera_001"
    DURATION_MINUTES = 2  # 2 minutes
    SAVE_DIRECTORY = "videos"

    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)

    # Step 1: Record video
    metadata = record_video(CAMERA_ID, DURATION_MINUTES, SAVE_DIRECTORY)

    # Step 2: Fetch video metadata
    fetched_metadata = fetch_video_metadata(CAMERA_ID)
    if fetched_metadata:
        # Step 3: Play the recorded video
        play_video(fetched_metadata["file_path"])
