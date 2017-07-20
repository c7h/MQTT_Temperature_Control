import asyncio
from hbmqtt.client import MQTTClient

async def publish(broker, topic, message, loop):
    """
    publish one message for testing
    :param broker: hostname of the broker
    :param topic: topic to publish
    :param message: message to publish
    :type message: str
    :param loop: async event loop
    :return: 
    """

    c = MQTTClient(loop=loop)
    await c.connect('mqtt://%s' % broker)
    tasks = [
        asyncio.ensure_future(c.publish(topic=topic, message=message)),
    ]
    await asyncio.wait(tasks)
    await c.disconnect()
