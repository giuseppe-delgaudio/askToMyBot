from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from dialogs.face_compare_star import FaceCompareStar
from dialogs.show_save_result_dialog import ShowSaveResultDialog
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
from config import DefaultConfig
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    HeroCard,
    CardAction,
    
)

class MainDialog(ComponentDialog):

    def __init__(self ):
        
        super(MainDialog , self).__init__(MainDialog.__name__)
        
        self.add_dialog( FaceAnalysisDialog( "FaceAnalysisDialog" ) )
        self.add_dialog( FaceCompareDialog( "FaceCompareDialog" ) )
        self.add_dialog( ShowSaveResultDialog("ManageResultDialog"))
        self.add_dialog( FaceCompareStar("FaceCompareStarDialog"))
        self.add_dialog( DeveloperModeDialog("DeveloperDialog" ))
        self.add_dialog(ChoicePrompt( "MainPrompt" ))
        self.add_dialog(
            WaterfallDialog(
                "Waterfall_main", [ self.choice_step , self.execute_step , self.loop_main_step ] ,
            ),
        
        )
        self.initial_dialog_id = "Waterfall_main"
    
    async def choice_step(self , step_context: WaterfallStepContext):
        #Avvio developerMode
        input = step_context.context.activity.text
        if input is not None :
            if input == "developerMode" :
                await step_context.end_dialog()
                return await step_context.begin_dialog("DeveloperDialog")
        #Avvio prompt con options
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
        #controllo choice ed avvio dialogo corretto
        result = step_context.result.value
        await step_context.context.send_activity(MessageFactory.text(result))

        if result == "Analizza il tuo volto":
            return await step_context.begin_dialog("FaceAnalysisDialog")
        
        elif result == "Confronta due visi" :
        
            return await step_context.begin_dialog( "FaceCompareDialog" )
        
        elif result == "Confronta volto con le star":

            return await step_context.begin_dialog("FaceCompareStarDialog")

        elif result == "Visualizza e controlla salvataggi" : 
            
            return await step_context.begin_dialog("ManageResultDialog")

        elif result == "Aiuto" :

            await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(HeroCard(
                text=DefaultConfig.WELCOME_MESSAGE
            ))))
            return await step_context.next(result=None)

        else :
            await step_context.context.send_activity( MessageFactory.text("Nessuna delle scelte è corretta riprova") )
            return await step_context.replace_dialog("Waterfall_main") 

    #Loop per ritorno da qualsiasi dialog
    async def loop_main_step(self, step_context : WaterfallStepContext) : 

        return await step_context.replace_dialog("Waterfall_main") 

    @staticmethod
    def get_options():
        options = [
            Choice(value="Analizza il tuo volto",synonyms=["/analisiVolto"]),
            Choice(value="Confronta due visi",synonyms=["/confrontoVisi"]),
            Choice(value="Confronta volto con le star" , synonyms=["/confrontoStar"]),
            Choice(value="Visualizza e controlla salvataggi", synonyms=["/salvataggi"]),
            Choice(value="Aiuto",synonyms=["/aiuto"]),
        ]
        return options

