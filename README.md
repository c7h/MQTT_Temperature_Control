# Temperature Control System


The temperature control system controls multiple actuators in different rooms based on sensor readings.
It uses readings from the MQTT topic `/readings/temperature` where data gets
processed in the following format:

```json
{
  "sensorID": "sensor-1",
  "type": "temperature",
  "value": 25.3
}
```

It then produces a result on the `/actuators/room-1` topic to control the actuators:

```json
{
  "level": 14
}
```

## Example:

```
 ______               _____          __           __
/_  __/__ __ _  ___  / ___/__  ___  / /________  / /
 / / / -_)  ' \/ _ \/ /__/ _ \/ _ \/ __/ __/ _ \/ /
/_/  \__/_/_/_/ .__/\___/\___/_//_/\__/_/  \___/_/
             /_/

subscribing to topic [/readings/temperature]...
starting event loop
listening for incoming messages...
Got message from sensor-2 : current temperature is 21.0...
Setting value of actuators room-1 to 13
Setting value of actuators room-5 to 13
Setting value of actuators room-6 to 13
Got message from sensor-2 : current temperature is 11.0...
Setting value of actuators room-1 to 100
Setting value of actuators room-5 to 100
Setting value of actuators room-6 to 100
```


## Design Notes:
The Server is designed to handle request async.

# Requirements

- python3.X
- everything in requirements.txt
- MQTT Server

The Server is started via `$ python main.py`.

# Configuration

You can configure the system using environment variables:

- `MQTT_HOST`: mqtt host. default: localhost
- `MQTT_READINGS`: topic for sensor data
- `MQTT_ACTUATORS`: topic for actuator output
- `LOGFILE`: full path of logfile
- `TARGET_TEMP`: Target temperature of the system

Further, you can set up the mapping of different sensors to different actuators.
Assuming every room has one sensor, it can have multiple actuators.
A mapping should define the relation to one sensor to multiple actuators. Of course,
a actuator can be part of multiple sensors as well.

```python
sensor_actuator_map = {
    "sensor-2": ("room-1",
                 "room-5",
                 "room-6"),
    "sensor-4": ("room-2",
                 "room-4"),
}
```

if a sensor has no actuator defined in the mapping, the ID of the sensor is used
to build the actuator name: Following scheme is used:
`5ens0rn4me-991` becomes `room-991`. Always use a hyphen to separate name from ID - it will fail otherwise.


# Temperature control

We use an simple *algorithm* to control the temperature:
If the read temperature is colder than 7 degrees of the target temperature,
we heat with the valves opened 100%. 7 to 0 degrees temperature difference and we open the valve linear.
This simple linear ramp-up might not be perfect, but should work for now.
Since we consider the outside temperature equal to the target temperature,
we stop heating at soon as the sensor tells us that the room has reached the target temperature, we close the valves of the actuators.
Remember this when you are planning to use different sensors for the same actuator!
It might end up in weird situations where actuators are moving a lot.

# Setup

This section describes how to get the system up and running.

## Access to MQTT Broker

Access to an MQTT Broker is needed. The broker is the instance which takes the messages and  For a fast start you can either use a public MQTT broker like [the HiveMQ test system](http://www.mqtt-dashboard.com/) or setup a local docker container on using **mosquitto**:

`$ docker run -it -p 1883:1883 -p 9001:9001 -v mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto`

This is the better choice for developing.

## Installing requirements

1. create a virtual environment
  `$ virtualenv python=$(which python3) venv ; source venv/bin/activate`
2. install requirements
  `$ pip3 install -r requirements`
3. run the server
  `$ python main.py`


