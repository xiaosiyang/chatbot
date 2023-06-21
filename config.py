#!/usr/bin/env python3


import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 80
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
