# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(self, id: str = None, imageUrl_1: str = None , imageUrl_2: str = None  ):
        self.id = id
        self.imageUrl_1 = imageUrl_1
        self.imageUrl_2 = imageUrl_2