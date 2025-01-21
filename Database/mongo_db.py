from pymongo import MongoClient
from datetime import datetime

def get_mongo_connection():
    
    print("[INFO] Connecting to MongoDB server...")
    try:
        client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI if hosted remotely
        print("[SUCCESS] Connected to MongoDB")
        return client
    except Exception as e:
        print(f"[ERROR] Error connecting to MongoDB: {e}")
        raise

def create_database(db_name):
    
    print(f"[INFO] Creating/connecting to database: {db_name}")
    client = get_mongo_connection()
    db = client[db_name]
    print(f"[SUCCESS] Database '{db_name}' created or connected.")
    return db

def insert_video_data(db_name, video_data):
    
    print("[INFO] Executing 'insert_video_data' function")
    collection_name = "video_collection"
    db = create_database(db_name)
    collection = db[collection_name]

    try:
        # Ensure timestamps are stored as datetime objects for efficient querying
        video_data["start_time"] = datetime.strptime(video_data["start_time"], "%Y-%m-%d %H:%M:%S")
        video_data["end_time"] = datetime.strptime(video_data["end_time"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("[ERROR] Invalid datetime format in video_data")
        raise ValueError("Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS'.")

    result = collection.insert_one(video_data)
    print(f"[SUCCESS] Video data inserted with ID: {result.inserted_id}")
    return result.inserted_id

def search_videos_by_time(db_name, start_time, end_time):
    
    print("[INFO] Executing 'search_videos_by_time' function")
    collection_name = "video_collection"
    db = create_database(db_name)
    collection = db[collection_name]

    try:
        # Convert start_time and end_time to datetime objects
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("[ERROR] Invalid datetime format in time range")
        raise ValueError("Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS'.")

    # Query for videos within the specified time range
    query = {
        "start_time": {"$gte": start_dt},
        "end_time": {"$lte": end_dt}
    }

    results = collection.find(query)
    result_list = [
        {
            "_id": str(video["_id"]),
            "start_time": video["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": video["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "description": video.get("description", ""),
            "video": video.get("video", ""),
        }
        for video in results
    ]

    if result_list:
        print(f"[SUCCESS] Found {len(result_list)} video(s) matching the criteria")
    else:
        print("[INFO] No videos found within the specified time range")

    return result_list


video_data={
        "start_time": "2024-12-14 10:00:00",
        "end_time": "2024-12-14 10:30:00",
        "description": "Sample video description",
        "video": "sample_video.mp4"
}
    
database= 'tsbagul21'

insert_video_data(database,video_data)
