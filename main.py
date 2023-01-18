from flask import Flask, request, CORS
from waitress import serve
import db
import mqtt

app = Flask(__name__)
CORS(app)


@app.route("/api/v1/thermostat/temp", methods=("GET",))
def getLatestSettedTemperature():
    print("getting temp")
    last_setted = db.get_last_setted()
    last_mode = db.get_last_mode()

    if last_setted is None or last_mode is None:
        return {
            "error": True,
            "result": "no last_setted or last_mode"
        }

    return {
        "error": False,
        "result": {
            "temp": last_setted,
            "mode": last_mode
        }
    }


@app.route("/api/v1/thermostat/temp", methods=("POST",))
def updateSettedTemperature():
    print("Setting temp")
    body = request.get_json()
    if body is None:
        return {
            "error": True,
            "msg": "no body found"
        }

    petitioner = body["petitioner"] if "petitioner" in body else "grafana"
    temp = body["temp"]
    mode = body["mode"]
    mqtt.publish("thermostat/set/" + petitioner + "}", str(temp))
    mqtt.publish("thermostat/setmode/" + petitioner + "}", str(mode))

    return {
        "error": False,
        "msg": "ok"
    }


if __name__ == "__main__":
    mqtt.init()
    print("Starting server")
    serve(app, host="0.0.0.0", port=3001)
