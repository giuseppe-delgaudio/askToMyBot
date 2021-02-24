#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "51bd055d-b570-4266-bef7-8920cf7a9708")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "OT~P8yU59xr~L~sado2A_.RFREr3aA155q")
    #APP_ID = os.environ.get("MicrosoftAppId","")
    #APP_PASSWORD = os.environ.get("MicrosoftAppPassword","")
    ## Parametri Cognitive Viso ##

    ENDPOINT = "https://faceapiaskbot.cognitiveservices.azure.com/"
    KEYFACE = "6957c16224e1465c956287dfbd04f4c7"

    # Parametri SearchApi

    ENDPOINT_SEARCH = "https://api.bing.microsoft.com/v7.0/images/search"
    KEYSEARCH ="f09d64c900704318b5f733a4182d0e44"


    # Parametri FunctionURL

    BASE_FUNCTION_URL = "http://localhost:7071/api/functionDB/"