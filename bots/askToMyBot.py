from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper


class AskToMyBot(ActivityHandler):
    def __init__(
        self,
        conversation_state : ConversationState,
        user_state: UserState,
        dialog : Dialog,
    ):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
    
    async def on_turn(self, turn_context):
        await super().on_turn(turn_context)

        #salvo stato ogni tuno 
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)
    
    async def on_message_activity(self, turn_context):
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )
