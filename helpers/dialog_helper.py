# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import StatePropertyAccessor, TurnContext , MessageFactory , CardFactory
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus 
from config import DefaultConfig
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    HeroCard,
    CardAction,
    CardImage
    
)

class DialogHelper:
    @staticmethod
    async def run_dialog(
        dialog: Dialog, turn_context: TurnContext, accessor: StatePropertyAccessor
    ):
        dialog_set = DialogSet(accessor)
        dialog_set.add(dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        
        if turn_context.activity.text == "/fine" :
            await dialog_context.cancel_all_dialogs()
        
        elif turn_context.activity.text == "/start" : 
            await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(HeroCard(
                text=DefaultConfig.WELCOME_MESSAGE
            ))))

        else :
            results = await dialog_context.continue_dialog()
            if results.status == DialogTurnStatus.Empty:
                await dialog_context.begin_dialog(dialog.id)
