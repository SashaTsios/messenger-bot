import json
import random
import requests
from flask import Flask, request
from pymessenger.bot import Bot
import tokenfile

app = Flask(__name__)
ACCESS_TOKEN = tokenfile.ACCESS_TOKEN
VERIFY_TOKEN = tokenfile.VERIFY_TOKEN
QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"

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
                    if message.get("postback").get("payload") == "start_button" or message.get("postback").get("payload") == "help":
                        recipient_id = message["sender"]["id"]
                        response = "Для отримання нового питання - нажми на відповідну кнопку або надрукуй 'Нове питання'.\n\nДалі в тебе такі варіанти: отримати інше питання чи відповісти на це.\nПісля відповіді - дізнаєшся чи вона правильна. Якщо так,то при наявності, з\'явиться пояснення до питання і перейдеш до нового.\nЯкщо ж ні - можеш спробувати знову, подивитись відповідь або перейти до іншого питання.\n\nДля вибору конкретного питання просто введи його порядковий номер. \nПитання з української мови мають номери 1 і далі,  математики - 2591 і далі, історії - 3448, географії - 5276, біології - 6710, фізики - 8090 і хімії - 9083."
                        button_title = {"start_button":"Почати тестування","help":"Нове питання"}
                        buttons = [
                            {
                                "content_type": "text",
                                "title": button_title[message.get("postback").get("payload")],
                                "payload": json.dumps(
                                    {"id": 0, "is_correct": "nothing",}
                                ),
                            },
                        ]
                        
                        action = "typing_on"
                        bot.send_action(recipient_id, action)
                        bot.send_message(recipient_id,message={"text": response, "quick_replies": buttons,})

                if message.get("message"):
                    recipient_id = message["sender"]["id"]
                    if message["message"].get("text") == "Допомога":  # quick reply
                        response = "Для отримання нового питання - нажми на відповідну кнопку або надрукуй 'Нове питання'.\n\nДалі в тебе такі варіанти: отримати інше питання чи відповісти на це.\nПісля відповіді - дізнаєшся чи вона правильна. Якщо так,то при наявності, з\'явиться пояснення до питання і перейдеш до нового.\nЯкщо ж ні - можеш спробувати знову, подивитись відповідь або перейти до іншого питання.\n\nДля вибору конкретного питання просто введи його порядковий номер. \nПитання з української мови мають номери 1 і далі,  математики - 2591 і далі, історії - 3448, географії - 5276, біології - 6710, фізики - 8090 і хімії - 9083."
                        buttons = [
                            {
                                "content_type": "text",
                                "title": "Нове питання",
                                "payload": json.dumps(
                                    {"id": 0, "is_correct": "nothing",}
                                ),
                            },
                        ]
                        action = "typing_on"
                        bot.send_action(recipient_id, action)
                        bot.send_message(
                            recipient_id,
                            message={"text": response, "quick_replies": buttons,},
                        )

                    elif message["message"].get("text") == "Нове питання" or message["message"].get("text") == "Почати тестування":
                        random_question(recipient_id)

                    elif message["message"].get("text") != None and message["message"].get("text").isdigit():  # other text - ECHO
                        id_question(recipient_id, message["message"].get("text"))
                    
                    elif message["message"].get("text") not in (
                        "А",
                        "Б",
                        "В",
                        "Г",
                        "Д",
                        "Bot",
                        "Отримати нове питання",
                        "Нове питання",
                        "Відповісти знову",
                        "Нове питання id",
                        "Пояснення",
                        "Допомога",):
                        response = f'Останнє повідомлення містить: {message["message"].get("text")}'
                        send_message(recipient_id, response)

                payload = (
                    message.get("message", {}).get("quick_reply", {}).get("payload")
                )
                # payload = json.dumps({"id": 1, "is_correct": "True",})
                if payload:
                    print(f"PAYLOAD: {payload}")
                    returned_payload = json.loads(payload)
                    #print(f'PAYLOAD DATA: {returned_payload["is_correct"]}')
                    if returned_payload["is_correct"] == "True":
                        get_all_page = requests.get(
                            f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}'
                        )
                        i_question = json.loads(get_all_page.content)
                        if i_question["explanation"]:
                            response = f'Твоя відповідь вірна. \n{i_question["explanation"]} \nСпробуй відповісти на це питання.'
                        else:
                            response = (f"Твоя відповідь вірна. Спробуй відповісти на це питання.")
                        recipient_id = message["sender"]["id"]
                        send_message(recipient_id, response)
                        random_question(recipient_id)

                    elif returned_payload["is_correct"] == "False":
                        response = f"Твоя відповідь не вірна. Вибери відповісти знову чи отримати нове питання."
                        recipient_id = message["sender"]["id"]
                        send_message(recipient_id, response)
                        payload = {
                            "id": returned_payload["id"],
                            "is_correct": "False_answer_again",
                        }
                        dumps = json.dumps(payload)
                        buttons = [
                            {
                                "content_type": "text",
                                "title": "Відповісти знову",
                                "payload": dumps,
                            },
                            {
                                "content_type": "text",
                                "title": "Нове питання",  # do not need to code this, simply == 'Нове питання' and works
                                "payload": json.dumps(
                                    {
                                        "id": returned_payload["id"],
                                        "is_correct": "False_get_new",
                                    }
                                ),
                            },
                        ]
                        get_all_page = requests.get(
                            f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}'
                        )
                        i_question = json.loads(get_all_page.content)
                        if i_question["explanation"]:
                            buttons.append(
                                {
                                    "content_type": "text",
                                    "title": "Пояснення",  # do not need to code this, simply == 'Нове питання' and works
                                    "payload": json.dumps(
                                        {
                                            "id": returned_payload["id"],
                                            "is_correct": "False_get_explanation",
                                        }
                                    ),
                                }
                            )
                        bot.send_message(
                            recipient_id,
                            message={
                                "text": message["message"].get("text"),
                                "quick_replies": buttons,
                            },
                        )
                    elif returned_payload["is_correct"] == "False_answer_again":
                        print("False, try this q again")
                        print(f'ID: {returned_payload["id"]}')
                        recipient_id = message["sender"]["id"]
                        id_question(recipient_id, returned_payload["id"])

                    elif returned_payload["is_correct"] == "False_get_explanation":
                        print("False, get_explanation")
                        print(f'ID: {returned_payload["id"]}')
                        recipient_id = message["sender"]["id"]
                        get_all_page = requests.get(
                            f'{QUESTIONS_API_ROOT}/{returned_payload["id"]}'
                        )
                        i_question = json.loads(get_all_page.content)
                        send_message(recipient_id, i_question["explanation"])
                        random_question(recipient_id)
        return "Message Processed"


def verify_fb_token(token_sent):
    """Сверяет токен, отправленный фейсбуком, с имеющимся у вас.
    При соответствии позволяет осуществить запрос, в обратном случае выдает ошибку."""
    if token_sent == VERIFY_TOKEN:
        return request.args["hub.challenge"]
    else:
        return "Invalid verification token"


def send_message(recipient_id, response):
    """Отправляет пользователю текстовое сообщение в соответствии с параметром response."""
    bot.send_text_message(recipient_id, response)
    return "Success"


# def get_message_text(messaged_text):
#     """ECHO"""
#     return "TEXT-echo: " + messaged_text


def random_question(recipient_id, random_ukr="random?subject=ukr" ):  # combine w id_question  #&format=raw
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/{random_ukr}")
    action = "typing_on"
    bot.send_action(recipient_id, action)
    i_question = json.loads(get_all_page.content)
    #print(f"I_QUESTION: {i_question}")
    instance_full_question = i_question
    if instance_full_question["image"] != None:
        #print(f'image {instance_full_question["image"]}')
        bot.send_image_url(recipient_id, instance_full_question["image"])
    #print(instance_full_question)
    display = f'{instance_full_question["content"]}\n\n'
    i_id = instance_full_question["id"]
    for choices in instance_full_question["choices"]:
        if len(choices["content"]) == 1:
            display = f"Відображено на рисунку"
        #print(str(int(choices["id"]) + 1) + choices["content"][1:])
        else:
            display += f'{choices["content"]}\n'
    response_sent_text = f" Питання\n{display}"
    #print(f'Total n of answers: {len(instance_full_question["choices"])}')
    buttons = []
    for i in range(len(instance_full_question["choices"])):
        button_example = {
            "content_type": "text",
            "title": instance_full_question["choices"][i]["content"].replace('*', '')[0],
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
            "payload": json.dumps({"id": i_id, "is_correct": "nothing",}),
        },
    )
    if instance_full_question["explanation"]:
        buttons.append(
            {
                "content_type": "text",
                "title": "Пояснення",
                "payload": json.dumps(
                    {"id": i_id, "is_correct": "False_get_explanation",}
                ),
            },
        )
    print(buttons)
    bot.send_message(
        recipient_id, message={"text": response_sent_text, "quick_replies": buttons,},
    )


def id_question(recipient_id, id):
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/{id}")  #?&format=raw
    action = "typing_on"
    bot.send_action(recipient_id, action)
    i_question = json.loads(get_all_page.content)
    #print(f"I_QUESTION: {i_question}")
    instance_full_question = i_question
    if instance_full_question.get("statusCode"):
        response = f"На жаль, питання {id} відсутнє або тимчасово недоступне. Спробуй відповісти на це:\n"
        send_message(recipient_id, response)
        random_question(recipient_id, random_ukr="random?subject=ukr&format=raw")
    else:
        if instance_full_question["image"] != None:
            #print(f'image {instance_full_question["image"]}')
            bot.send_image_url(recipient_id, instance_full_question["image"])
        #print(instance_full_question)
        display = f'{instance_full_question["content"]}\n\n'
        i_id = instance_full_question["id"]
        for choices in instance_full_question["choices"]:
            #print(f'CONTENT LENGHT: {len(choices["content"])}')
            if len(choices["content"]) == 1:
                display = f"Відображено на рисунку"
            #print(str(int(choices["id"]) + 1) + choices["content"][0:])
            else:
                display += f'{choices["content"]}\n'  # {(int(choices["id"]) + 1)}
        response_sent_text = f" Питання\n{display}"
        #print(f'Total n of answers: {len(instance_full_question["choices"])}')
        buttons = []
        for i in range(len(instance_full_question["choices"])):
            button_example = {
                "content_type": "text",
                "title": instance_full_question["choices"][i]["content"].replace('*', '')[0],
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
                "payload": json.dumps({"id": i_id, "is_correct": "nothing",}),
            },
        )
        if instance_full_question["explanation"]:
            buttons.append(
                {
                    "content_type": "text",
                    "title": "Пояснення",
                    "payload": json.dumps(
                        {"id": i_id, "is_correct": "False_get_explanation",}
                    ),
                },
            )
        print(buttons)
        bot.send_message(
            recipient_id, message={"text": response_sent_text, "quick_replies": buttons,},
        )

if __name__ == "__main__":
    app.run(debug=True)
