from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from helpers.image_search import Image_Search
from helpers.face_cognitive import FaceCognitive
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions , TextPrompt , AttachmentPrompt , ConfirmPrompt , PromptValidatorContext
from botbuilder.dialogs.choices import Choice,ListStyle
from botbuilder.core import (
    MessageFactory, 
    CardFactory
)
from helpers.save_method import saveMessage
from azure.cognitiveservices.vision.face.models import PersonGroup , Person
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    HeroCard,
    CardAction,
    AttachmentLayoutTypes,
    CardImage
    
)
from helpers.adaptiveCardHelper import replace
import requests , os , json
from io import BytesIO 

class FaceCompareStar(ComponentDialog):

    def __init__(self, dialog_id : str ):
        super(FaceCompareStar , self ).__init__(
            dialog_id
        )
        #Inizializzo congitive e Bing Image Search
        self.cognitive = FaceCognitive()
        self.search = Image_Search()

        #Main dialog per upload foto e check con group 
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"FaceCompareStar",[
                    self.imageUploadStep,
                    self.choiceGroup_step,
                    self.elabStep,
                    self.saveStep
                ],
            )
        )

        self.add_dialog(  
            AttachmentPrompt( AttachmentPrompt.__name__ , FaceCompareStar.picture_prompt_validator )
        )
        self.add_dialog(
            ChoicePrompt( ChoicePrompt.__name__ )
        )
        self.add_dialog(
            ConfirmPrompt(ConfirmPrompt.__name__ , default_locale="italian" )
        )
        
        
        #dialogo iniziale 
        self.initial_dialog_id = WaterfallDialog.__name__+"FaceCompareStar"  
    
   
    async def imageUploadStep( self , step_context : WaterfallStepContext ) -> DialogTurnResult:
        #Prompt upload image
        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Per ottenere un analisi carica una tua foto"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__ , prompt_image )
  
    async def choiceGroup_step(self, step_context : WaterfallStepContext ):
            
            step_context.values["image"] = step_context.result[0]
            #Recupera lista gruppi 
            groups : list = await self.cognitive.getGroupPerson()

            if groups is None :
                #Nessuna categoria
                await step_context.context.send_activity("Sembra non ci sia nessuna categoria, mi dispiace")
                return await step_context.end_dialog()
            
            else :
                #Prompt choice group
                return await step_context.prompt(ChoicePrompt.__name__ , PromptOptions(
                        prompt=MessageFactory.text("Seleziona la categoria"),
                        retry_prompt=MessageFactory.text("La selezione non è valida riprova"),
                        choices=FaceCompareStar.getGroupListChoice( groups ),
                        style=ListStyle.hero_card
                    ))

    async def elabStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:

        personGroup = step_context.result.value

        if personGroup == "Torna indietro":
            step_context.end_dialog()

        image = step_context.values["image"]
        
        #Trasformo immagine in stream da url
        res : Response = requests.get(image.content_url) 
        
        await step_context.context.send_activity(MessageFactory.text("Ora dovrei elaborare"))
        
        result : list = await self.cognitive.identifyPerson( BytesIO(res.content) , personGroup )


        if result is not None and len(result) == 2 :
            # Viso rilevato ora preparo la scheda da mostrare -> result[0] contiene confidence - result[1] person object target
            confidence = result[0] * 100
            person : Person = result[1]
            starImage = self.search.searchImage(searchParam=person.name)
            text1 = f" Il tuo viso ha una somiglianza del {round(confidence,2)} % con {person.name} Complimenti"
            
            data : dict = dict()

            data["result"] = text1
            data["image_1"] = image.content_url
            data["image_2"] = starImage[0]

            with open( os.path.join(os.getcwd(), "templates/showResultCard.json" ) , "rb") as in_file:
                cardData  = json.load(in_file)

            #sostituisco elementi nel template 
            cardData = await replace(cardData , data)
            #costruisco adaptive card
            await step_context.context.send_activity(MessageFactory.attachment(CardFactory.adaptive_card(cardData)))


        else : 
            #Non ho individuato nessun viso nell immagine caricata
            await step_context.context.send_activity(MessageFactory.text("Sembra che la foto non contenga visi oppure non sono riuscito a trovare una corssipondenza adeguata prova a ricaricare la foto oppure premi /fine per terminare"))
            return await step_context.replace_dialog( WaterfallDialog.__name__+"FaceCompareStar" )
            
            
        step_context.values["textAnalysis"] = text1
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions( prompt=MessageFactory.text("Vuoi salvare il risultato ?"), style=ListStyle.hero_card  )
        )
    
    async def saveStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:

        if step_context.result:
            
            text = step_context.values["textAnalysis"]

            userId = step_context.context.activity.from_property.id
            userChannel = step_context.context.activity.channel_id
            res = await saveMessage(userId , userChannel , text )
            
            if res : 
                await step_context.context.send_activity(MessageFactory.text("Salvato"))
            else: 
                await step_context.context.send_activity(MessageFactory.text("Problemi nel salvataggio"))

        else:
            
            await step_context.context.send_activity(MessageFactory.text("Va bene non salvo"))
            
        
        return await step_context.end_dialog()
    
    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "Ricarica un immagine valida oppure /fine"
            )

           
            return False

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0

    @staticmethod
    def getGroupListChoice( groupList : list ) :
        
        choice = list()

        if len(groupList) != 0 : 
        
            personGroup : PersonGroup = None

            for i in range(len(groupList)) : 
                personGroup = groupList.pop()
                ch = Choice(value=personGroup.person_group_id)
                choice.append(ch)
        
        choice.append(Choice(value="Torna indietro"))
        return choice