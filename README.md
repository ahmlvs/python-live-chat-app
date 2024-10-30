# python-live-chat-app

Uses Flask Sockets to create a live chat room application.

1. create virtual env

```
python3 -m venv env
source env/bin/activate
```

and add .env file in root folger with SECRET_KEY

2. install libraries

```
pip install Flask
pip install flask-socketio
pip install python-dotenv
```

3. start server

```
python3 main.py
```

4. open 2 browser windows (1 in incognito mode)

```
http://127.0.0.1:5000/
```
