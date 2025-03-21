import time
from azure.iot.device import IoTHubDeviceClient, Message
import adafruit_dht
import board

# Initialize the DHT22 sensor on GPIO4
dht22 = adafruit_dht.DHT22(board.D4)

CONNECTION_STRING = "HostName=MyEdgeIotHub2025.azure-devices.net;DeviceId=Device1;SharedAccessKey=inWMJ8+PKMCHV08HDCddGTeS9RPuUkfvdSInPQtjVWw="
MSG_SND = '{"temperature": %s, "humidity": %s}'

def iothub_client_init():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def iothub_client_telemetry_sample_run():
    client = iothub_client_init()
    print("Sending data to IoT Hub, press Ctrl-C to exit")

    while True:
        try:
            # Retry mechanism for DHT22 readings
            temperature = None
            humidity = None
            for _ in range(5):  # Try up to 5 times
                try:
                    temperature = dht22.temperature
                    humidity = dht22.humidity
                    if temperature is not None and humidity is not None:
                        break  # Exit loop if reading succeeds
                except RuntimeError:
                    print("DHT22 Read Error: Retrying...")
                    time.sleep(2)  # Small delay before retry

            if temperature is None or humidity is None:
                print("Failed to read from DHT22 sensor after multiple attempts.")
                continue  # Skip sending if reading failed

            # Formatting and sending the message
            msg_txt_formatted = MSG_SND % (temperature, humidity)
            message = Message(msg_txt_formatted)
            print("Sending message from edge: {}".format(message))
            client.send_message(message)
            print("Message successfully sent to app")

        except KeyboardInterrupt:
            print("IoTHubClient stopped")
            break

        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(3)  # Delay between readings

if __name__ == '__main__':
    print("Press Ctrl-C to exit")
    iothub_client_telemetry_sample_run()

