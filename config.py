#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "7c398f90-ee1c-4ba4-9fc8-9efcb660736e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "FcsSfA2_9qk_-5FywT_a~sd4b7UO-8xmyD")
