from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    HeroCard,
    CardAction,
    CardImage,
    AttachmentLayoutTypes
    
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
from helpers.save_method import getMessageById , updateMessage
from botbuilder.dialogs.choices import Choice , ListStyle
from botbuilder.core import MessageFactory, UserState , CardFactory
from helpers.face_cognitive import FaceCognitive
from helpers.image_search import Image_Search
from data_models import UserProfile
from azure.cognitiveservices.vision.face.models import * 
from PIL import Image
from io import BytesIO
import requests 

class ShowSaveResultDialog(ComponentDialog):
    def __init__(self, dialog_id: str ):
        super(ShowSaveResultDialog, self).__init__(
            dialog_id 
        )

        self.add_dialog( ConfirmPrompt(ConfirmPrompt.__name__ ))
        self.add_dialog( ChoicePrompt( ChoicePrompt.__name__ ))

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"SaveMain", 
                [
                    self.showSaveResult_step,
                    self.confirmDelete_step,
                    self.endSave_step
                ]

            )
        )

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"DeleteLoop",
                [
                    self.beginLoopDelete_step,
                    self.delete_step,
                    self.evaluate_loop_step
            
                ]
            
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__+"SaveMain"
    
    
    async def showSaveResult_step(self,step_context : WaterfallStepContext ) :
        
        userId = step_context.context.activity.from_property.id
        userChannel = step_context.context.activity.channel_id
        messageList : list = await getMessageById(userId=userId ,channelID=userChannel)

        if messageList is None :

            await step_context.context.send_activity("Mi dispiace non hai salvato nessun risultato")
            return await step_context.end_dialog()
        
        else : 

            #Mostro risultati ricerca
            card = HeroCard(
                title="I tuoi risultati",
                text=ShowSaveResultDialog.generateText(messageList)
            )

            await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))
            step_context.values["messages"] = messageList
            return await step_context.prompt(ConfirmPrompt.__name__ , PromptOptions(
                prompt=MessageFactory.text("Vuoi eliminare qualche risultato ?"),
                retry_prompt=MessageFactory.text("Inserisci un risultato valido")
            ))
    
    async def confirmDelete_step(self,step_context : WaterfallStepContext ) :

        if step_context.result :

            return await step_context.begin_dialog(WaterfallDialog.__name__+"DeleteLoop" , options=step_context.values["messages"] )
            
        else :
            
            await step_context.context.send_activity("Va bene torno al menu")
            return await step_context.end_dialog()
  
    async def beginLoopDelete_step(self,step_context : WaterfallStepContext ) :
        
        messageList = step_context.options
        step_context.values["messages"] = messageList 
        choices = []
        
        for i in range(len(messageList)) : 
            choice = Choice(
                value=str(i+1) 
            )
            choices.append(choice)
        
        choices.append(Choice(value="Tutto" ))

        return await step_context.prompt(ChoicePrompt.__name__ , PromptOptions(
            prompt=MessageFactory.text("Quale messaggio vuoi eliminare"),
            choices=choices,
            style=ListStyle.hero_card
        ))
    
    async def delete_step(self,step_context : WaterfallStepContext ) :

        toDelete = step_context.result.value
        messageList : list = step_context.values["messages"]

        if toDelete == "Tutto" :

            messageList.clear()
            return await step_context.end_dialog(result=messageList)

        else : 

            del messageList[int(toDelete)-1]
            step_context.values["messages"] = messageList
            return await step_context.prompt(ConfirmPrompt.__name__ , PromptOptions(
                prompt=MessageFactory.text("Vuoi eliminare altri risultati ?"),
                retry_prompt=MessageFactory.text("Inserisci un risultato valido")
            ))

    async def evaluate_loop_step( self , step_context : WaterfallStepContext ) : 

        if step_context.result :

            return await step_context.replace_dialog(WaterfallDialog.__name__+"DeleteLoop" , options=step_context.values["messages"] )
            
        else :
            
            return await step_context.end_dialog(result = step_context.values["messages"])

    async def endSave_step( self , step_context : WaterfallStepContext ) : 

        messageList : list = step_context.result
        userId = step_context.context.activity.from_property.id
        userChannel = step_context.context.activity.channel_id
        res =  await updateMessage(userId=userId , channelID=userChannel , messages=messageList )
        if res : 
            await step_context.context.send_activity("Eliminato/i correttamnete")
        else : 
            await step_context.context.send_activity("Problemi durante l' eliminazione riprova")

        return await step_context.end_dialog()

    
    @staticmethod
    def generateText( messages : list  ) -> str :
        i = 0
        text = ""
        for message in messages :
            msg =message["message"]
            date= message["date"]
            text+=f"{i+1}:\n{msg}\nin data {date}\n\n"
            i+=1
        return text
