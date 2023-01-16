from flask import Flask

app = Flask(__name__)


@app.route("/api/v1/thermostat/temp", methods=("GET",))
def getLatestSettedTemperature():
    return "Hello, World!"


@app.route("/api/v1/thermostat/temp", methods=("POST",))
def updateSettedTemperature():
    return "Hello, World!"


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=3001)
