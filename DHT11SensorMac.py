# imports Adafruit_DHT libary
import Adafruit_DHT
from gpiozero import LED
import time
import datetime
import os
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

DHT_SENSOR = Adafruit_DHT.DHT11  # sensor type
GPIO_PIN = 4  # GPIO pin DHT11 output is going too
led = LED(21)  # GPIO pin feeding power to led

my_channel = "seans-pi-channel"
pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH")
pnconfig.uuid = '2ca147c6-d6e1-4d2c-9c38-a34d6938efd6'
pubnub = PubNub(pnconfig)


# heating_on = False  # heating is off by default

# returns both humidity, temperature
def get_data_reading():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, GPIO_PIN)
    if humidity is not None and temperature is not None:
        return humidity, temperature
    else:
        return 0, 0


def main():
    while True:
        now = datetime.datetime.now()
        # humidity, temperature = get_data_reading()
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, GPIO_PIN)
        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
            publish(my_channel, {"Bedroom 1: "
                                 "temperature ": '{0:0.1f}*C'.format(temperature)+" "+now.strftime("%Y-%m-%d %H:%M:%S")})
            # heating(25, temperature)
            if temperature < 25:
                led.on()
            else:
                led.off()

        else:
            print('Failed Reading - Trying Again')
            # publish(my_channel, {"Failed Reading": "Trying Again"})
        time.sleep(5)


def turn_heating_on():
    led.on()


def turn_heating_off():
    led.off()


# def heating(temperature_set, current_temperature):
#     if heating_on and current_temperature < temperature_set:
#         led.on()
#     else:
#         led.off()


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

    # === Will be if tempature over certain tempt turn led off or turn led on
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
    pubnub.subscribe().channels(my_channel).execute()

# Help Ref:
# https://www.thegeekpub.com/236867/using-the-dht11-temperature-sensor-with-the-raspberry-pi/
