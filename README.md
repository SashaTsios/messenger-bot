## Messenger bot - for training and testing

### Install requirements:
```
pip install -r requirements.txt
```

### Запуск локального середовища:
1. Запустити локальний веб-сервер ```python app.py```.
2. Активувати за допомогою [Ngrok](https://ngrok.com/) ```./ngrok http <Port>``` тунель між локальним веб-вервером і зовнішнім сайтом з підтримкою SSL.
3. Створіть в директорії із app.py новий файл tokenfile.py, який має містити 3 змінні.
Приклад:
ACCESS_TOKEN = "EAABrZB7EkKR0iTxwU5kPUZANpLS3ZAGFcgzvkd7mn67lajaxZAtW6"
VERIFY_TOKEN = "MeSSenGERTEST1NGT0KEN"
QUESTIONS_API_ROOT = #посилання на url чи json, де знаходяться питання - список з таких елементів:
{"id": 1, "content": "Текст вашого запитання", "image": null | "https://cdn.freebiesbug.com/wp-content/uploads/2012/12/github-psd-icon.jpg", "explanation": "" | "*ТЕМА: Література XX ст.* *Михайло Коцюбинський**. Пояснення. \n\n*Відповідь – А.*", "choices": [{"id": 0, "content": "*А*: перший варіант відповіді", "is_correct": false}, {"id": 1, "content": "*Б*: другий варіант відповіді", "is_correct": false},]}
в "choices" - до 5 елементів.
де ACCESS_TOKEN замінюємо на свій із https://developers.facebook.com/apps/YOUR_APP_ID/messenger/settings/ в Access Tokens,
VERIFY_TOKEN - генеруємо самі, використовуємо в п4. Не забудь змінити YOUR_APP_ID на свій!
4. На сторінці https://developers.facebook.com/apps/YOUR_APP_ID/messenger/settings/ в Webhooks добавити/виправити (при необхідності): Callback URL - <ssl_url>``` - посилання з логу Ngrok, Verify Token - із tokenfile.py