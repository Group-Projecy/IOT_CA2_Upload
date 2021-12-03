from flask import Flask, render_template, request, redirect, jsonify
import secrets
import base64
from Crypto import Random
from Crypto.Cipher import AES

app = Flask(__name__)

STUDENT_CHOICES = {}
ELECTIVES = [
    "Smart Technology",
    "Artificial Intelligence",
    "Immersive Technologies",
    "Service Oriented Architecture"
]



BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s : s[0:-ord(s[-1:])]

class AESCipher:

    def __init__( self, key ):
        self.key = bytes(key, 'utf-8')

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = "encryptionIntVec".encode('utf-8')
        print(iv)
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] )).decode('utf8')


@app.route("/")
def index():
    return render_template("index.html", electives=ELECTIVES)



@app.route("/login", methods=['GET', 'POST'])
def login():
    email = "pgarfield@gmail.com"
    password = "password"
    content = request.json
    # must add in encryption and decryption in future
    if content['email'] == email and content['password'] == password:
        result = {"Result": "True",
                  "HouseID": "1234567"
                  }
        return result
    else:
        return "False"


# returns the house main room details
@app.route("/house_room/<house_id>", methods=['GET', 'POST'])
# returns the rooms that the house has
def home_rooms(house_id):
    key = secrets.token_bytes(32)
    print(type(key))
    print(key)

    rooms = [{
        "temperature": 10,
        "dateTime": "24:00:15T2021:12:02",
        "room": "Bedroom #1"
    },
        {
            "temperature": 20,
            "dateTime": "24:00:15T2021:12:02",
            "room": "Kitchen #2"
        }]
    if house_id == "1234567":
        return jsonify(rooms)
    else:
        return str(house_id)


@app.route("/oil_level_current/<house_id>", methods=['GET', 'POST'])
# returns the rooms that the house has
def current_levels(house_id):
    # get the most recent recording of the oil
    result = {
        "oil_level": 10,  # percent out a hundred in number
    }
    if house_id == "1234567":
        return jsonify(result)
    else:
        return str(house_id)


# needed for home page
@app.route("/average_temperature_house/<house_id>", methods=['GET'])
def average_temperature(house_id):
    # get the average temperature of the house
    result = {
        "temperature": 30,  # return as int
    }
    if house_id == "1234567":
        return jsonify(result)
    else:
        return str(house_id)


app.run(debug=True)


# get oil usage last 7 days
@app.route("/usage/<house_id>", methods=['GET'])
def usage_last_7(house_id):
    # get the usage last 7 days
    result = [{
        "oilUsed": 100,  # oil used in litres
        "day": "2021:11:02",
    },
        {
            "oilUsed": 7000,  # oil used in litres
            "day": "2021:11:03",
        },
        {
            "oilUsed": 0,  # oil used in litres
            "day": "2021:11:04",
        },
        {
            "oilUsed": 50,  # oil used in litres
            "day": "2021:11:05",
        },
        {
            "oilUsed": 1000,  # oil used in litres
            "day": "2021:11:06",
        },
        {
            "oilUsed": 1000,  # oil used in litres
            "day": "2021:11:07",
        },
        {
            "oilUsed": 1000,  # oil used in litres
            "day": "2021:11:086",
        }]
    if house_id == "1234567":
        return jsonify(result)
    else:
        return str(house_id)


app.run(debug=True)
