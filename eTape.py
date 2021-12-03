from gpiozero import MCP3008
import time
import datetime
import os

resistor = 560  # Value of the series resistor in ohms
eTape = MCP3008(0)  # MCP pin the output is going to

no_volume_resistance = 2093  # Resistance value (in ohms) when no liquid is present NOTE: it changes slightly every time
calibration_resistance = 730  # Resistance value (in ohms) when liquid is at max line.
# calibration_volume = 30  # length of tape
calibration_volume = 500  # amount of water in ml³

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

my_channel = "seans-pi-channel"
pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH")
pnconfig.uuid = '7929c8df-30b8-4473-a865-1a7ed1adef93'
pubnub = PubNub(pnconfig)


def main():
    while True:
        debug_code()
        # ohms_value = resistance
        resistance = read_resistance()
        # water_level = get_water_level(resistance)
        timestamp = get_time_stamp()
        water_volume = get_water_volume(resistance)
        water_level_litres = convert_water_level_litres(water_volume)
        publish(my_channel, {"WaterLevel ": '{0:0.0f} Litres'.format(water_level_litres), "Time ": timestamp})
        time.sleep(1)
        print("\n")


# reads the out from the mcp and converts the the out put to ohms value
def read_resistance():
    reading = eTape.value * 1000  # adc value
    # covert adc value to resistance
    resist = (1023 / reading) - 1
    resist = resistor / resist
    # print('resistance(): %.2f' % resist)  # just print to console for debugging and calibration
    return resist  # ohms value


# gets the level of the water in cm against the cm line on the level not as accurate as volume
def get_water_level(ohms_value):
    if ohms_value > no_volume_resistance or (no_volume_resistance - calibration_resistance) == 0.0:
        # if no max value for resistance is set
        return 0.0
    else:
        water_level_measurement = (no_volume_resistance - ohms_value) / (no_volume_resistance - calibration_resistance)
        cm = 30 * water_level_measurement
        return cm


# converts the resistance out put to the water volume of the water tube
def get_water_volume(ohms_value):
    if ohms_value > no_volume_resistance or (no_volume_resistance - calibration_resistance) == 0.0:
        # if no max value for resistance is set
        return 0.0
    else:
        water_level_scale = (no_volume_resistance - ohms_value) / (no_volume_resistance - calibration_resistance)
        return calibration_volume * water_level_scale  # returns the value in mm³


# This method will convert the water level from ml³ to litres and then scale up it up to represent a real oil tank size
# as our demo is in 500ml tube
# 500 ml³ represents 1000 litres
def convert_water_level_litres(volume):
    return volume * 2


def get_time_stamp():
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return time_str


# this method is used for debugging and calibrating the sensor
# also used for IOT demo of CA2
def debug_code():
    # ohms_value = resistance
    resistance = read_resistance()
    water_volume = get_water_volume(resistance)
    water_level_litres = convert_water_level_litres(water_volume)
    print("====================")
    print('resistance(): %.2f' % resistance)  # just print to console for debugging and calibration
    print('water volume: {0:0.0f} ml³'.format(water_volume))
    print('Water Level Scaled up: {0:0.0f} L'.format(water_level_litres))


# ----------------------------- PubNub Code ---------------------------------------------
def publish(channel, msg):
    pubnub.publish().channel(my_channel).message(msg).pn_async(my_publish_callback)


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel(my_channel).message('Hello world!').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, message):
        # Handle new message stored in message.message
        try:
            print(message.message, ": ", type(message.message))
            msg = message.message
            key = list(msg.keys())
            if key[0] == "event":
                self.handleEvent(msg)
        except Exception as e:
            print("Received: ", message.message)
            print(e)
            pass
    #  handle event = if oil level = < 20% send message

    # def handleEvent(self, msg):
    #     global data
    #     eventData = msg["event"]
    #     key = list(eventData.keys())
    #     print(key)
    #     print(key[0])
    #     if key[0] in sensor_list:
    #         if eventData[key[0]] is True:
    #             print("Setting the alarm")
    #             data["alarm"] = True
    #         elif eventData[key[0]] is False:
    #             print("Turning alarm off")
    #             data["alarm"] = False


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


if __name__ == "__main__":
    main()

#  Ref website that help me with e-tape: https://learn.adafruit.com/smart-measuring-cup?view=all
