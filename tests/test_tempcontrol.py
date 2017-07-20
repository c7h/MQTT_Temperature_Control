import unittest
import asyncio

from tempcontrol import (
    handle_temperature, get_actuators_for_sensor, handle_temp_topic_message)


class TemperatureTestCase(unittest.TestCase):
    def test_valve_settings_01(self):
        """if it's too hot, we close the valves"""
        result = handle_temperature(
            temperature=25.8,
            target_temperature=24
        )
        self.assertEqual(result, 0)

    def test_value_settings_02(self):
        """if we are way too cold, we heat up 100%"""
        result = handle_temperature(
            target_temperature=30,
            temperature=20,
        )
        self.assertEqual(result, 100.0)

    def test_valve_settings_boundaries_01(self):
        # if we are more then 7 degrees too cold, we should still heat 100%
        result = handle_temperature(22.99999, 30)
        self.assertEqual(result, 100.0)

    def test_valve_settings_boundaries_02(self):
        # if we are too hot, or perfect in temperature, we should stop heating
        result = handle_temperature(30, 30)
        self.assertEqual(result, 0.0)

    def test_valve_between_boundaries(self):
        # we should be in an average heating range if we are 4 degrees too cold
        valve_range = range(45, 55)
        result = handle_temperature(26, 30)
        self.assertIn(int(result), valve_range)


class ActuatorsManagingTestCase(unittest.TestCase):

    def test_get_actuator_01(self):
        res = get_actuators_for_sensor("sensor-2")
        self.assertTupleEqual(res, ('room-1', 'room-5', 'room-6'))

    def test_get_malformed_actuator(self):
        # we cannot create an actuator name from this sensor name:
        with self.assertRaises(ValueError):
            get_actuators_for_sensor('foosensor-XXX')

    def test_get_unknown_actuator(self):
        res = get_actuators_for_sensor("sensor-99")
        self.assertTupleEqual(res, ("room-99",))


if __name__ == '__main__':
    unittest.main()


# Mocking needed components
sent_message = tuple()


class MockServer(object):
    async def publish_valve_setting(self, actuator, value):
        """
        async mock method used to mock server class for this test case
        """
        # FIXME: this is very ugly and need to go away
        global sent_message
        sent_message = actuator, value


class MockPayload(object):
    data = bytearray(b'{\n  "sensorID": "sensor-2",\n  "type": "temperature",\n  "value": 22.3\n}')


class MockPacket(object):
    payload = MockPayload()


class TestMessageCallbackTestCase(unittest.TestCase):
    def setUp(self):
        self.server = MockServer()
        self.packet = MockPacket()
        self.loop = asyncio.get_event_loop()

    def test_handle_01(self):
        async def testee():
            await handle_temp_topic_message(self.server, self.packet)
        self.loop.run_until_complete(testee())
        self.assertEqual(sent_message[1], 0)
