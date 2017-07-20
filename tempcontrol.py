"""
Handles temperature controls
"""
import json
import logging
import re

from config import sensor_actuator_map, target_temperature

log = logging.getLogger(__name__)


def handle_temperature(temperature, target_temperature, t=13.2):
    """
    control function to calculate valve setting for a given temperature.
    We assume the outside temperature equals the target temperature so we don't add
    energy to the system to keep the current state. 
    (We assume we don't have losses in the open system)
    :param temperature: current temperature
    :type temperature: float
    :param target_temperature: the target temperature
    :type target_temperature: float
    :param t: tuning parameter
    :type t: float
    :return: valve setting percentage(0-100)
    """
    # TODO: more fancy - using sensor for outside temperature / logarithmic controller or PID
    delta_t = target_temperature - temperature
    if delta_t > 7:
        new_value = 100  # full heat if waaaay too cold
    elif delta_t < 0:
        new_value = 0  # no heating if it's to warm
    else:
        # between max and min delta_t, we finetune the valve linear.
        new_value = int(t * delta_t)
    return min(new_value, 100)  # cutoff at 100


def get_actuators_for_sensor(sensor_name):
    """
    return a tuple of actuator names related to a sensor id.
    Very simple approach: look it up in the memory map stored in the config.
    If no mapping exists, use the sensor id as actuator id
    :param sensor_name: the name of the sensor
    :return: tuple with names of the corresponding actuators
    """

    try:
        return sensor_actuator_map[sensor_name]
    except KeyError:
        result = re.findall(r'(?!\w+-)(\d+)', sensor_name)
        if not result:
            raise ValueError("cannot create actuator name from input: %s" % sensor_name)
        else:
            return ("room-%s" % result.pop(),)


async def handle_temp_topic_message(server, packet):
    """
    Handler for temperature readings channel. 
    Decodes incoming packets and triggers actions for handling
    :param packet: MQTT Packet
    :param server: MQTT Server Object
    """

    # handling the bytearray
    try:
        data = packet.payload.data.decode('utf8')  # .replace("'", '"')
        temp_reading = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        logging.warning("cannot decode temperature reading: %s... ignoring", e)
        return

    log.debug(temp_reading)

    # extract values
    current_temperature = temp_reading.get('value')
    sensor_name = temp_reading.get('sensorID')
    readings_type = temp_reading.get('type')

    log.info('Got message from %(sensorID)s : current %(type)s is %(value)s...' % temp_reading)

    # validate message is complete
    if not (current_temperature and sensor_name and readings_type):
        logging.warning("information missing in message %s... ignoring" % temp_reading)
        return

    # we only care about messages of type temperature
    if not readings_type == "temperature":
        logging.warning("message type not handled yet: %s... ignoring" % readings_type)
        return

    # calculate new valve setting for actuator
    new_valve_setting = handle_temperature(
        temperature=current_temperature,
        target_temperature=target_temperature,
    )

    # get actuator for sensor
    try:
        actuator_names = get_actuators_for_sensor(sensor_name)
    except ValueError as e:
        log.error("error looking up actuator name:", e)
        return

    # publish messages to actuators
    try:
        for actuator in actuator_names:
            log.info("Setting value of actuators %s to %s", actuator, new_valve_setting)
            await server.publish_valve_setting(actuator, new_valve_setting)
    except ValueError as e:
        log.error("cannot send message: %s", e)
