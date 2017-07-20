import unittest
import asyncio

from server import Server
from basetest import publish

from config import mqtt_broker, mqtt_topic_temperature


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # async preparations - create a new event loop for every test
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()


class RunServerTestCase(BaseTestCase):
    def test_server_setup(self):

        s = Server(self.loop)
        async def testee():
            return await s.setup()

        self.loop.run_until_complete(testee())
        self.assertFalse(self.loop.is_running())


class HandleMessageTestCase(BaseTestCase):
    def setUp(self):
        super(HandleMessageTestCase, self).setUp()
        self.server = Server(loop=self.loop)
        self.loop.run_until_complete(self.server.setup())

    def test_handle_unknown_message(self):
        async def testee():
            await self.server.handle_incoming_messages()
            await publish(broker=mqtt_broker,
                          message="unknown",
                          topic='/readings',
                          loop=self.loop)
        self.loop.run_until_complete(testee())


if __name__ == '__main__':
    unittest.main()
