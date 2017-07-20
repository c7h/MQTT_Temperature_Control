import os
import logging

# mqtt settings
mqtt_broker = os.environ.get("MQTT_HOST", "localhost")
mqtt_topic_temperature = os.environ.get("MQTT_READINGS", "/readings/temperature")
mqtt_topic_actuators = os.environ.get("MQTT_ACTUATORS", "/actuators/")

# configure logging
logging.basicConfig(filename=os.environ.get("LOGFILE", 'logfile.txt'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

# temperature settings
target_temperature = float(os.environ.get("TARGET_TEMP", 22.0))


# sensor / actuator mapping
# a room can have multiple actuators.
# Therefore we keep a list of sensor for different actuators
# If a sensor is not registered in the system, we assume the actuator has the same id.
sensor_actuator_map = {
    "sensor-2": ("room-1",
                 "room-5",
                 "room-6"),
    "sensor-4": ("room-2",
                 "room-4"),
}
