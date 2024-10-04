# """Start
#     Windows: python -m flask run --host=0.0.0.0 --cert=adhoc       мусор
#     Linux: мусор
# """

from flask import Flask, request
import logging, json, requests
from datetime import datetime
import pytz

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

username = "your libre link up email"               # ВСТАВЬТЕ СВОИ ДАННЫЕ
password = "your libre link up password"
port = 5000                                         # ПОРТ

url = "https://api.libreview.ru"                    # API в России
version = "4.2.1"
headers = {
    "product": "llu.android",
    "version": version,
    "accept-encoding": "gzip",
    "cache-control": "no-cache",
    "connection": "Keep-Alive",
    "content-type": "application/json",
}
# Login and acquire JWT token
response = requests.post(
    f"{url}/llu/auth/login",
    headers=headers,
    json={"email": username, "password": password},
)
data = response.json()
jwt_token = data["data"]["authTicket"]["token"]
headers["Authorization"] = f"Bearer {jwt_token}"



@app.route("/", methods=["POST"])
def main():
    logging.info(request.json)

    response1 = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }

    req = request.json
    if req["session"]["new"]:
        response = requests.get(f"{url}/llu/connections", headers=headers)
        connections = response.json()
        print(connections["data"][0]["glucoseMeasurement"])

        curret = connections["data"][0]["glucoseMeasurement"]["Value"]
        arrow = connections["data"][0]["glucoseMeasurement"]["TrendArrow"]
        ishigh = connections["data"][0]["glucoseMeasurement"]["isHigh"]
        islow = connections["data"][0]["glucoseMeasurement"]["isLow"]

        arrow_text = "ошибка"
        status = ""

        if arrow == 3:
            arrow_text = "стабильная"
        elif arrow == 4:
            arrow_text = "диагональная вверх"
        elif arrow == 5:
            arrow_text = "вверх"
        elif arrow == 2:
            arrow_text = "диагональная вниз"
        elif arrow == 1:
            arrow_text = "вниз"

        if ishigh:
            status = "Осторожно, высокий уровень глюкозы, "
        elif islow:
            status = "Осторожно, низкий уровень глюкозы, "

        measurement_time = datetime.strptime(connections["data"][0]["glucoseMeasurement"]["Timestamp"], "%m/%d/%Y %I:%M:%S %p")
        local_tz = pytz.timezone('Europe/Moscow') 
        measurement_time = local_tz.localize(measurement_time)
        now = datetime.now(local_tz)
        minutes_ago = (now - measurement_time).total_seconds() // 60

        at = measurement_time.strftime('%H:%M')
        ago = f"{int(minutes_ago)} минут назад" if minutes_ago < 60 else f"{int(minutes_ago // 60)} часов {int(minutes_ago % 60)} минут назад"

        rs = f"{status}Текущий уровень глюкозы {curret}, был отсканирован в {at}, это {ago}, стрелка {arrow_text}"
        response1["response"]["text"] = rs
        
    else:
        pass
        # response = requests.get(f"{url}/llu/connections", headers=headers)
        # connections = response.json()
        # print(connections["data"][0]["glucoseMeasurement"])

        # curret = connections["data"][0]["glucoseMeasurement"]["Value"]
        # arrow = connections["data"][0]["glucoseMeasurement"]["TrendArrow"]
        # ishigh = connections["data"][0]["glucoseMeasurement"]["isHigh"]
        # islow = connections["data"][0]["glucoseMeasurement"]["isLow"]

        # arrow_text = "ошибка"
        # status = ""

        # if arrow == 3:
        #     arrow_text = "стабильная"
        # elif arrow == 4:
        #     arrow_text = "диагональная вверх"
        # elif arrow == 5:
        #     arrow_text = "вверх"
        # elif arrow == 2:
        #     arrow_text = "диагональная вниз"
        # elif arrow == 1:
        #     arrow_text = "вниз"

        # if ishigh:
        #     status = "Осторожно, высокий уровень глюкозы, "
        # elif islow:
        #     status = "Осторожно, низкий уровень глюкозы, "

        # measurement_time = datetime.strptime(connections["data"][0]["glucoseMeasurement"]["Timestamp"], "%m/%d/%Y %I:%M:%S %p")
        # local_tz = pytz.timezone('Europe/Moscow') 
        # measurement_time = local_tz.localize(measurement_time)
        # now = datetime.now(local_tz)
        # minutes_ago = (now - measurement_time).total_seconds() // 60

        # at = measurement_time.strftime('%H:%M')
        # ago = f"{int(minutes_ago)} минут назад" if minutes_ago < 60 else f"{int(minutes_ago // 60)} часов {int(minutes_ago % 60)} минут назад"

        # rs = f"{status}Текущий уровень глюкозы {curret}, был отсканирован в {at}, это {ago}, стрелка {arrow_text}"
        # response1["response"]["text"] = rs

    return json.dumps(response1)

if __name__ == '__main__':
    app.run(port=port, ssl_context='adhoc', host="0.0.0.0")

