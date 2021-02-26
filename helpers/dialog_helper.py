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
        #Aggiungo al set il main Dialog
        dialog_set.add(dialog)
        #Creo contesto dialogo main 
        dialog_context = await dialog_set.create_context(turn_context)
        #Se digitato /fine termino tutti i dialoghi Reset
        if turn_context.activity.text == "/fine" :
            await dialog_context.cancel_all_dialogs()
        # comando /start telegram per messaggio di benvenuto
        elif turn_context.activity.text == "/start" : 
            await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(HeroCard(
                text=DefaultConfig.WELCOME_MESSAGE
            ))))
        #Riprendo dialogo avviato
        else :
            results = await dialog_context.continue_dialog()
            if results.status == DialogTurnStatus.Empty:
                await dialog_context.begin_dialog(dialog.id)
