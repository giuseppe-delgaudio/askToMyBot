from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import UserProfile

class FaceAnalysisDialog(ComponentDialog):
    def __init__(self, dialog_id: str , user_state : UserState):
        super(FaceAnalysisDialog, self).__init__(
            dialog_id 
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,[
                    self.imageUploadStep,
                    self.imageCheck,
                    self.elabStep,
                    self.saveStep
                ],
            )
        )

        self.add_dialog(  
            AttachmentPrompt(AttachmentPrompt.__name__ , FaceAnalysisDialog.picture_prompt_validator)
        )
        self.add_dialog(
            ConfirmPrompt(ConfirmPrompt.__name__+"00")
        )
        self.add_dialog(
            ConfirmPrompt(ConfirmPrompt.__name__+"01")
        )
        
        #dialogo iniziale 
        self.initial_dialog_id = WaterfallDialog.__name__   
    
    async def imageUploadStep( self , step_context : WaterfallStepContext ) -> DialogTurnResult:

        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Per ottenere un analisi carica una tua foto"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__ , prompt_image )

    async def imageCheck( self , step_context : WaterfallStepContext ) -> DialogTurnResult:
        #memorizzo l'immagine del turno precedente 
        step_context.values["image"] = step_context.result[0]

        await step_context.context.send_activity(
            MessageFactory.attachment(
                step_context.values["image"]
            )
        )

        return await step_context.prompt(
            ConfirmPrompt.__name__+"00",
            PromptOptions( prompt=MessageFactory.text("La foto è corretta ?") )
        )
    
    async def elabStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:

        if step_context.result:
            
            await step_context.context.send_activity(MessageFactory.text("Ora dovrei elaborare"))

        else:
            
            await step_context.context.send_activity(MessageFactory.text("Ti riporto all upload, premi /fine per terminare"))
            return await step_context.replace_dialog( FaceAnalysisDialog.__name__ )
            
        
        return await step_context.prompt(
            ConfirmPrompt.__name__+"01",
            PromptOptions( prompt=MessageFactory.text("Vuoi salvare il risultato ?") )
        )
    
    async def saveStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:

        if step_context.result:
            
            await step_context.context.send_activity(MessageFactory.text("Ora dovrei salvare"))

        else:
            
            await step_context.context.send_activity(MessageFactory.text("Va bene non salvo"))
            
        
        return await step_context.end_dialog()
    
    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "No attachments received. Proceeding without a profile picture..."
            )

            # We can return true from a validator function even if recognized.succeeded is false.
            return True

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0
