from flask import Flask
from Log import MyLog

app_logger = MyLog(name=__name__)
app = Flask(__name__)
app.config.from_object('webapp_config')
for hndlr in app_logger.handlers:
    app.logger.addHandler(hndlr)
app_logger.info(app.secret_key)

from WebApp import views
