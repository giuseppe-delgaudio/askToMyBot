from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from dialogs.face_compare_star import FaceCompareStar
from dialogs.developer_mode_dialog import DeveloperModeDialog
from dialogs.face_compare_dialog import FaceCompareDialog
from dialogs.face_analysis_dialog import FaceAnalysisDialog
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice,ListStyle
from botbuilder.core import (
    MessageFactory, 
    UserState,
    CardFactory
)
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    HeroCard,
    CardAction,
    
)

class MainDialog(ComponentDialog):

    def __init__(self , user_state : UserState):
        
        super(MainDialog , self).__init__(MainDialog.__name__)
        
        self.user_state = user_state.create_property(
            "UserState"
        )
        self.add_dialog( FaceAnalysisDialog( "FaceAnalysisDialog" , self.user_state) )
        self.add_dialog( FaceCompareDialog( "FaceCompareDialog" , self.user_state ) )
        self.add_dialog( FaceCompareStar("FaceCompareStarDialog"))
        self.add_dialog( DeveloperModeDialog("DeveloperDialog" ))
        self.add_dialog(ChoicePrompt( "MainPrompt" ))
        self.add_dialog(
            WaterfallDialog(
                "Waterfall_main", [ self.choice_step , self.execute_step ] ,
            ),
        
        )
        self.initial_dialog_id = "Waterfall_main"
    
    async def choice_step(self , step_context: WaterfallStepContext):

        input = step_context.context.activity.text
        if input is not None :
            if input == "developerMode" :
                await step_context.end_dialog()
                return await step_context.begin_dialog("DeveloperDialog")

        return await step_context.prompt(
            "MainPrompt",
            PromptOptions(
                prompt=MessageFactory.text(
                    "Seleziona un' azione da eseguire"
                ),
                retry_prompt=MessageFactory.text(
                    "Effettua una scelta valida, ripova"
                ),
                choices=self.get_options(),
                style=ListStyle.hero_card
            ),
        )

    async def execute_step( self , step_context : WaterfallStepContext ):

        result = step_context.result.value
        await step_context.context.send_activity(MessageFactory.text(result))

        if result == "Analizza il tuo volto":
            return await step_context.begin_dialog("FaceAnalysisDialog")
        
        elif result == "Confronta due visi" :
        
            return await step_context.begin_dialog( "FaceCompareDialog" )
        
        elif result == "Confronta volto con le star":

            return await step_context.begin_dialog("FaceCompareStarDialog")

        else :
            await step_context.context.send_activity( MessageFactory.text("Nessuna delle scelte è corretta riprova") )
            return await step_context.replace_dialog("Waterfall_main") 

        return await step_context.end_dialog()

    def cardChoice(self) -> Attachment :
        card = HeroCard(
            title="Seleziona l'azione da eseguire",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="Analizza il tuo volto",
                    value="/mioVolto"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Compara due volti",
                    value="/comparaVolti"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Compara volto con le star",
                    value="/comparaStar"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Aiuto",
                    value="/aiuto"
                )
            ],
        )
        return CardFactory.hero_card(card)
    
    
    def get_options(self):
        options = [
            Choice(value="Analizza il tuo volto",synonyms=["/analisiVolto"]),
            Choice(value="Confronta due visi",synonyms=["/confrontoVisi"]),
            Choice(value="Confronta volto con le star" , synonyms=["/confrontoStar"]),
            Choice(value="Aiuto",synonyms=["/aiuto"]),
        ]
        return options

