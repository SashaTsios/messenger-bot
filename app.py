# -*- coding: utf-8 -*-
import json
import requests
from flask import Flask, request
from pymessenger.bot import Bot
import tokenfile

app = Flask(__name__)
ACCESS_TOKEN = tokenfile.ACCESS_TOKEN
VERIFY_TOKEN = tokenfile.VERIFY_TOKEN
QUESTIONS_API_ROOT = tokenfile.QUESTIONS_API_ROOT

bot = Bot(ACCESS_TOKEN)


@app.route("/", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        token_sent = request.args["hub.verify_token"]
        return verify_fb_token(token_sent)
    else:
        output = request.get_json()
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                if message.get("postback"):
                    messaging_postback(message)
                if message.get("message"):
                    messaging_message(message)
                payload = (
                    message.get("message", {}).get("quick_reply", {}).get("payload")
                )
                if payload:
                    messaging_payload(message, payload)
        return "Message Processed"


def messaging_postback(message):
    if (
        message.get("postback").get("payload") == "start_button"
        or message.get("postback").get("payload") == "help"
    ):
        recipient_id = message["sender"]["id"]
        response = "Для отримання нового питання - нажми на відповідну кнопку або надрукуй *Нове питання*.\n\nДалі в тебе такі варіанти: отримати інше питання чи відповісти на це.\nПісля відповіді - дізнаєшся чи вона правильна. Якщо так,то при наявності, з'явиться пояснення до питання і перейдеш до нового.\nЯкщо ж ні - можеш спробувати знову, подивитись відповідь або перейти до іншого питання.\n\nДля вибору конкретного питання просто введи його порядковий номер. \nПитання з української мови мають номери 1 і далі,  математики - 2591 і далі, історії - 3448, географії - 5276, біології - 6710, фізики - 8090 і хімії - 9083."
        button_title = {
            "start_button": "Почати тестування",
            "help": "Нове питання",
        }
        buttons = [
            {
                "content_type": "text",
                "title": button_title[message.get("postback").get("payload")],
                "payload": json.dumps({"id": 0, "is_correct": "nothing"}),
            },
        ]
        action = "typing_on"
        bot.send_action(recipient_id, action)
        bot.send_message(
            recipient_id, message={"text": response, "quick_replies": buttons},
        )


def messaging_message(message):
    recipient_id = message["sender"]["id"]
    if message["message"].get("text") == "Допомога":  # quick reply
        response = "Для отримання нового питання - нажми на відповідну кнопку або надрукуй *Нове питання*.\n\nДалі в тебе такі варіанти: отримати інше питання чи відповісти на це.\nПісля відповіді - дізнаєшся чи вона правильна. Якщо так,то при наявності, з'явиться пояснення до питання і перейдеш до нового.\nЯкщо ж ні - можеш спробувати знову, подивитись відповідь або перейти до іншого питання.\n\nДля вибору конкретного питання просто введи його порядковий номер. \nПитання з української мови мають номери 1 і далі,  математики - 2591 і далі, історії - 3448, географії - 5276, біології - 6710, фізики - 8090 і хімії - 9083."
        buttons = [
            {
                "content_type": "text",
                "title": "Нове питання",
                "payload": json.dumps({"id": 0, "is_correct": "nothing"}),
            },
        ]
        action = "typing_on"
        bot.send_action(recipient_id, action)
        bot.send_message(
            recipient_id, message={"text": response, "quick_replies": buttons},
        )
    elif (
        message["message"].get("text") == "Нове питання"
        or message["message"].get("text") == "Почати тестування"
    ):
        id_or_random_question(recipient_id)
    elif (
        message["message"].get("text") is not None
        and message["message"].get("text").isdigit()
    ):
        id_or_random_question(recipient_id, int(message["message"].get("text")))
    elif message["message"].get("text") not in (
        "А",
        "Б",
        "В",
        "Г",
        "Д",
        "Нове питання",
        "Відповісти знову",
        "Пояснення",
        "Правильна відповідь",
        "Допомога",
    ):
        response = f'*Використовуй кнопки! Некоректне введення:* {message["message"].get("text")}'
        send_message(recipient_id, response)


def messaging_payload(message, payload):
    #  print(f"PAYLOAD: {payload}")
    returned_payload = json.loads(payload)
    if returned_payload["is_correct"] == "True":
        get_all_page = requests.get(f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}')
        i_question = json.loads(get_all_page.content)
        if i_question["explanation"]:
            response = f'💪 Твоя відповідь *вірна*. \n{i_question["explanation"]} \nСпробуй відповісти на це питання.'
        else:
            response = f"💪 Твоя відповідь *вірна*. Спробуй відповісти на це питання."
        recipient_id = message["sender"]["id"]
        send_message(recipient_id, response)
        id_or_random_question(recipient_id)
    elif returned_payload["is_correct"] == "False":
        response = f"Твоя відповідь *не вірна*. Вибери наступну дію."
        recipient_id = message["sender"]["id"]
        send_message(recipient_id, response)
        payload = {
            "id": returned_payload["id"],
            "is_correct": "False_answer_again",
        }
        dumps = json.dumps(payload)
        get_all_page = requests.get(f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}')
        i_question = json.loads(get_all_page.content)
        if i_question["explanation"]:
            button_title = "Пояснення"
        else:
            button_title = "Правильна відповідь"
        buttons = [
            {"content_type": "text", "title": "Відповісти знову", "payload": dumps},
            {
                "content_type": "text",
                "title": "Нове питання",
                "payload": json.dumps(
                    {"id": returned_payload["id"], "is_correct": "False_get_new"}
                ),
            },
        ]
        buttons.append(
            {
                "content_type": "text",
                "title": button_title,
                "payload": json.dumps(
                    {
                        "id": returned_payload["id"],
                        "is_correct": "False_get_explanation",
                    }
                ),
            }
        )
        bot.send_message(
            recipient_id, message={"text": "*Вибери дію:*", "quick_replies": buttons},
        )
    elif returned_payload["is_correct"] == "False_answer_again":
        # print(f'False_answer_again - ID: {returned_payload["id"]}')
        recipient_id = message["sender"]["id"]
        id_or_random_question(recipient_id, returned_payload["id"])

    elif returned_payload["is_correct"] == "False_get_explanation":
        # print(f'False_get_explanation - ID: {returned_payload["id"]}')
        recipient_id = message["sender"]["id"]
        get_all_page = requests.get(f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}')
        i_question = json.loads(get_all_page.content)
        if i_question.get("explanation"):
            send_message(recipient_id, i_question["explanation"])
        else:
            for choice in i_question["choices"]:
                if choice["is_correct"]:
                    message = f'*Правильний варіант відповіді на питання номер {returned_payload["id"]}:*\n{choice["content"]}'
            send_message(recipient_id, message)
        id_or_random_question(recipient_id)


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args["hub.challenge"]
    else:
        return "Invalid verification token"


def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "Success"


def id_or_random_question(recipient_id, q_id_or_random_q_subject="ukr"):
    if q_id_or_random_q_subject is not None and type(q_id_or_random_q_subject) is int:
        get_all_page = requests.get(
            f"{QUESTIONS_API_ROOT}/{q_id_or_random_q_subject}"
        )  # ?&format=raw
        #  print('IF DIGIT')
    else:
        get_all_page = requests.get(
            f"{QUESTIONS_API_ROOT}/random?subject={q_id_or_random_q_subject}"
        )
        #  print('IF RANDOM')
    #  print(f'GET ALL PAGE: {get_all_page}')
    action = "typing_on"
    bot.send_action(recipient_id, action)
    i_question = json.loads(get_all_page.content)
    #  print(f"I_QUESTION: {i_question}")
    instance_full_question = i_question
    #  print(f"instance_full_question: {instance_full_question}")
    #  print(f'IMAGE here is: {instance_full_question.get("image")}')
    if instance_full_question.get("statusCode"):
        i_id = q_id_or_random_q_subject
        response = f"На жаль, питання {i_id} відсутнє або тимчасово недоступне. Вибери *Нове питання* або введи номер\n"
        buttons = []
        buttons.append(
            {
                "content_type": "text",
                "title": "Нове питання",
                "payload": json.dumps({"id": i_id, "is_correct": "nothing"}),
            },
        )
        bot.send_message(
            recipient_id, message={"text": response, "quick_replies": buttons},
        )
    else:
        if instance_full_question.get("image") is not None:
            print(f'image image{instance_full_question.get("image")}')
            bot.send_image_url(recipient_id, instance_full_question["image"])
        display = f'{instance_full_question["content"]}\n\n'
        i_id = instance_full_question["id"]
        for choices in instance_full_question["choices"]:
            if len(choices["content"]) == 1:
                display = f"Відображено на рисунку"
            else:
                display += f'{choices["content"]}\n'
        response_sent_text = f" *Питання номер {i_id}*\n{display}"
        buttons = []
        for i in range(len(instance_full_question["choices"])):
            button_example = {
                "content_type": "text",
                "title": instance_full_question["choices"][i]["content"].replace(
                    "*", ""
                )[0],
                "payload": json.dumps(
                    {
                        "id": i_id,
                        "is_correct": str(
                            instance_full_question["choices"][i]["is_correct"]
                        ),
                    }
                ),
            }
            buttons.append(button_example)
        buttons.append(
            {
                "content_type": "text",
                "title": "Нове питання",
                "payload": json.dumps({"id": i_id, "is_correct": "nothing"}),
            },
        )
        if i_question["explanation"]:
            button_title = "Пояснення"
        else:
            button_title = "Правильна відповідь"
        buttons.append(
            {
                "content_type": "text",
                "title": button_title,
                "payload": json.dumps(
                    {"id": i_id, "is_correct": "False_get_explanation"}
                ),
            },
        )
        print(buttons)
        bot.send_message(
            recipient_id,
            message={"text": response_sent_text, "quick_replies": buttons},
        )


if __name__ == "__main__":
    app.run(debug=True)
