#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    #APP_ID = os.environ.get("MicrosoftAppId", "bc48ebee-f228-474b-856d-e1003ddf9be3")
    #APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "VIXj8A6eL-F2OpVa376dBO5.w4oj_8j6f-")
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    ## Parametri Cognitive Viso ##

    ENDPOINT = "https://faceapiaskbot.cognitiveservices.azure.com/"
    KEYFACE = "6957c16224e1465c956287dfbd04f4c7"

    # Parametri SearchApi

    ENDPOINT_SEARCH = "https://api.bing.microsoft.com/v7.0/images/search"
    KEYSEARCH ="f09d64c900704318b5f733a4182d0e44"