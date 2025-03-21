from azure.storage.blob import BlobServiceClient
import datetime
import json
import hashlib
from flask import jsonify

# Azure Storage Connection Details
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=edgestockage2025;AccountKey=3xAx10+RhpFRG9y7zcrR33840kWy6a1rGmNdZydOitEtRYXN5uoX4PfntfDwlxQGz6ONDcH2MjIx+AStT/8QOw==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "container"

def get_latest_sensor_data():
    """Fetches the latest sensor data from Azure Blob Storage."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Get today's folder path (e.g., "2025/03/01")
        now = datetime.datetime.now()
        folder_path = f"{now.year}/{now.month:02d}/{now.day:02d}"

        # List blobs in today's folder
        blob_list = list(container_client.list_blobs(name_starts_with=folder_path + "/"))
        
        if not blob_list:
            return jsonify({"error": "No sensor data available"}), 404

        # Sort blobs by last modified date (latest first)
        blob_list.sort(key=lambda blob: blob.last_modified, reverse=True)
        latest_blob = blob_list[0]

        # Download the latest blob content
        blob_client = container_client.get_blob_client(latest_blob.name)
        blob_data = blob_client.download_blob().readall().decode("utf-8")

        # Process JSON data (extract latest reading)
        try:
            lines = blob_data.strip().split('\n')  # Blob may contain multiple JSON objects
            last_data_json = json.loads(lines[-1])  # Take the latest entry

            temperature = last_data_json.get("temperature")
            humidity = last_data_json.get("humidity")

            return jsonify({
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": last_data_json.get("EventProcessedUtcTime"),
                "device_id": last_data_json.get("IoTHub", {}).get("ConnectionDeviceId")
            }), 200

        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format in blob"}), 500

    except Exception as e:
        return jsonify({"error": f"Error retrieving sensor data: {str(e)}"}), 500

