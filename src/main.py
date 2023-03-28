import os
from logger import logger as log
from functools import wraps
from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import db
import mqtt

app = Flask(__name__)
CORS(app)


def check_auth(username, password):
    return username == os.environ["AUTH_USER"] and password == os.environ["AUTH_PASS"]


def login_required(f):
    """ basic auth for api """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return {"message": "Authentication required"}
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/v1/thermostat/temp", methods=("GET",))
@login_required
def getLatestSettedTemperature():
    try:
        log.info("GET /api/v1/thermostat/temp")
        last_setted = db.get_last_setted()
        last_mode = db.get_last_mode()
        last_temp = db.get_last_temp()

        if last_setted is None or last_mode is None:
            log.error("no last_setted or last_mode")
            return {
                "error": True,
                "result": "no last_setted or last_mode"
            }

        log.info("GET /api/v1/thermostat/temp 200")
        return {
            "error": False,
            "result": {
                "temp": last_setted,
                "mode": last_mode,
                "last": last_temp
            }
        }
    except Exception as e:
        log.error("GET /api/v1/thermostat/temp")
        log.error(str(e))
        return {
            "error": True,
            "result": e
        }


@app.route("/api/v1/thermostat/temp", methods=("POST",))
@login_required
def updateSettedTemperature():
    try:
        log.info("POST /api/v1/thermostat/temp")
        body = request.get_json()
        if body is None:
            return {
                "error": True,
                "msg": "no body found"
            }

        petitioner = body["petitioner"] if "petitioner" in body else "grafana"
        temp = body["temp"] if "temp" in body else None
        mode = body["mode"] if "mode" in body else None

        if temp is not None:
            log.info("Publising temp")
            mqtt.publish("thermostat/set/" + petitioner, str(temp))
        if mode is not None:
            log.info("Publising mode")
            mqtt.publish("thermostat/setmode/" + petitioner, str(mode))

        log.info("POST /api/v1/thermostat/temp 200")
        return {
            "error": False,
            "msg": "ok"
        }
    except Exception as e:
        log.error("POST /api/v1/thermostat/temp")
        log.error(str(e))

        return {
            "error": True,
            "msg": str(e)
        }


@app.route("/api/v1/thermostat/temp/<dir>", methods=("POST",))
@login_required
def increaseDecreaseSettedTemperature(dir):
    try:
        log.info("POST /api/v1/thermostat/temp/<dir>")
        body = request.get_json()
        petitioner = body["petitioner"] if body is not None and "petitioner" in body else "grafana"

        last_setted = db.get_last_setted()

        direction = 1 if dir == 'inc' else -1
        temp = last_setted + direction

        if temp is not None:
            log.info("Publising temp")
            mqtt.publish("thermostat/set/" + petitioner, str(temp))

        log.info("POST /api/v1/thermostat/temp/<dir> 200")
        return {
            "error": False,
            "msg": "ok"
        }
    except Exception as e:
        log.error("POST /api/v1/thermostat/temp/<dir>")
        log.error(str(e))

        return {
            "error": True,
            "msg": str(e)
        }


if __name__ == "__main__":
    log.info("Starting server")
    mqtt.init()
    serve(app, host="0.0.0.0", port=3001)
