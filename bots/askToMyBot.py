from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState , MessageFactory , CardFactory
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper
from botbuilder.schema import ChannelAccount , HeroCard
from config import DefaultConfig

class AskToMyBot(ActivityHandler):
    def __init__(
        self,
        conversation_state : ConversationState,
        dialog : Dialog,
    ):
        self.conversation_state = conversation_state
        self.dialog = dialog
    
    async def on_turn(self, turn_context):
        await super().on_turn(turn_context)

        #salvo stato ogni tuno conversazioni
        await self.conversation_state.save_changes(turn_context, False)
    
    async def on_message_activity(self, turn_context):
        
        #Avvio helper per controllo stato dialoghi
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )
    
    #Messaggio help per nuovi utenti (SOLO MICROSOFT)
    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
         await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(HeroCard(
                text=DefaultConfig.WELCOME_MESSAGE
            ))))
