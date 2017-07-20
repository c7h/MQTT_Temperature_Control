"""
this controls the server bootup, async queues and message handling
"""

import asyncio
import logging
import json

from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1

from config import (
    mqtt_broker, mqtt_topic_actuators, mqtt_topic_temperature
)
from tempcontrol import handle_temp_topic_message

log = logging.getLogger(__name__)


class Server(object):
    def __init__(self, loop):
        self.__loop = loop
        self.__client = MQTTClient(
            loop=self.__loop,
            client_id="Challenge",
        )

        # topics to subscribe to
        self.__subscribed_topics = [
            mqtt_topic_temperature,
        ]

    async def setup(self):
        """
        start server tasks in a defined order
        :return: None
        """
        mqtt_url = "mqtt://%s" % mqtt_broker
        await self.__client.connect(mqtt_url)

        # subscribe
        for topic in self.__subscribed_topics:
            log.info("subscribing to topic [%s]..." % topic)
            await self.__client.subscribe([(topic, QOS_1)])

    async def run(self):
        """
        start listening to incoming messages
        :return: 
        """
        log.info("listening for incoming messages...")
        while True:
            await self.handle_incoming_messages()

    async def publish_valve_setting(self, actuator, value):
        """
        publish a new valve setting to the actuator
        :param actuator: actuator name. e.g. room-1
        :type actuator: str
        :param value: new actuator value. allowed 0-100
        :type value: int
        :return: None
        :raise ValueError: if wrong actuator value
        """
        if 0 < value > 100:
            raise ValueError("Actuator needs to be in range between 0 and 100")

        actuator_topic = "%s/%s" % (mqtt_topic_actuators, actuator)
        actuator_message = json.dumps({"level": value}, ensure_ascii=False).encode('utf-8')
        log.debug('message %b ready to send to channel %s', actuator_message, actuator_topic)
        await self.__client.publish(actuator_topic, message=actuator_message)

    async def handle_incoming_messages(self):
        """
        handle readings from subscribed topics and delegate it
        to their assigned callbacks
        :return: None
        """
        message = await self.__client.deliver_message()
        packet = message.publish_packet

        # TODO: improve handling of subtopics etc...
        if packet.variable_header.topic_name.startswith(mqtt_topic_temperature):
            # handle any message specifically from the temperature-reading channel
            await handle_temp_topic_message(self, packet)
        else:
            log.warning("unknown message received... ignoring")

    async def clean(self):
        """
        Clear data before exiting. Close handlers and sockets
        :return: 
        """
        log.info("cleaning up...")
        await self.__client.unsubscribe(self.__subscribed_topics)
        await self.__client.disconnect()


def run():
    """Manages the event loop"""
    loop = asyncio.get_event_loop()
    app = Server(loop=loop)

    # setup server components
    loop.run_until_complete(app.setup())

    # run the loop
    try:
        log.info("starting event loop")
        loop.create_task(app.run())
        loop.run_forever()
    finally:
        loop.run_until_complete(app.clean())
        log.info("Execution interrupted: closing the loop.")

    loop.close()
    log.info("Shut down the loop.")
