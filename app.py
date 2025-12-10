from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY not set. Add it to .env")

@app.route("/", methods=["GET"])
def index():
    default_city = request.args.get("city", "")
    return render_template("index.html", default_city=default_city)

@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        try:
            return jsonify({"error": resp.json().get("message", "Failed to fetch weather")}), resp.status_code
        except Exception:
            return jsonify({"error": "Failed to fetch weather"}), 500

    data = resp.json()
    result = {
        "city": f"{data.get('name')}, {data.get('sys', {}).get('country')}",
        "temperature_c": data.get("main", {}).get("temp"),
        "feels_like_c": data.get("main", {}).get("feels_like"),
        "humidity": data.get("main", {}).get("humidity"),
        "description": data.get("weather", [{}])[0].get("description"),
        "icon": data.get("weather", [{}])[0].get("icon"),
        "wind_speed": data.get("wind", {}).get("speed"),
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
