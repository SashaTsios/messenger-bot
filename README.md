## Messenger bot for zno simulator

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
QUESTIONS_API_ROOT = #посилання на url чи json, де знаходяться питання 
де ACCESS_TOKEN замінюємо на свій із https://developers.facebook.com/apps/YOUR_APP_ID/messenger/settings/ в Access Tokens,
VERIFY_TOKEN - генеруємо самі, використовуємо в п4. Не забудь змінити YOUR_APP_ID на свій!
4. На сторінці https://developers.facebook.com/apps/YOUR_APP_ID/messenger/settings/ в Webhooks добавити/виправити (при необхідності): Callback URL - <ssl_url>``` - посилання з логу Ngrok, Verify Token - із tokenfile.py