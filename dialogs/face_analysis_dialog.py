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
    CardImage
    
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
from botbuilder.dialogs.choices import Choice , ListStyle
from botbuilder.core import MessageFactory, UserState , CardFactory
from helpers.face_cognitive import FaceCognitive
from azure.cognitiveservices.vision.face.models import * 
from PIL import Image
from io import BytesIO
import requests 
from helpers.save_method import saveMessage

class FaceAnalysisDialog(ComponentDialog):
    def __init__(self, dialog_id: str  ):
        super(FaceAnalysisDialog, self).__init__(
            dialog_id 
        )

        #Inizzializzo CognitiveSev
        self.cognitive = FaceCognitive()

        self.add_dialog(
            WaterfallDialog(
                "Waterfall_FaceAnalysis",[
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
            ConfirmPrompt(ConfirmPrompt.__name__+"00" , default_locale="italian" )
        )
        self.add_dialog(
            ConfirmPrompt(ConfirmPrompt.__name__+"01" , default_locale="italian" )
        )
        
        #dialogo iniziale 
        self.initial_dialog_id = "Waterfall_FaceAnalysis"  
    
    async def imageUploadStep( self , step_context : WaterfallStepContext ) -> DialogTurnResult:

        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Per ottenere un analisi carica una foto"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__ , prompt_image )

    async def imageCheck( self , step_context : WaterfallStepContext ) -> DialogTurnResult:
        #memorizzo l'immagine del turno precedente 
        step_context.values["image"] = step_context.result[0]
        image = step_context.values["image"]
        #print(step_context.context.activity.from_property.id)
        await step_context.context.send_activity(
            MessageFactory.attachment(
                
                CardFactory.hero_card(
                    HeroCard(
                    images = [CardImage(url = image.content_url)]
                    )
                )
            )
        )

        return await step_context.prompt(
            ConfirmPrompt.__name__+"00",
            PromptOptions( prompt=MessageFactory.text("La foto è corretta ?")  , style=ListStyle.hero_card )
        )
    
    async def elabStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:
        ## Risposta affermativa step precedente 
        if step_context.result:
            
            image = step_context.values["image"]
           
            #Trasformo immagine in stream da url
            res : Response = requests.get(image.content_url) 
            
            await step_context.context.send_activity(MessageFactory.text("Ora dovrei elaborare"))
            #result = None
            result : DetectedFace = await self.cognitive.faceAnalysis(BytesIO(res.content))

            # Nessun viso rilevato riporto al caricamento
            if result is None :
                
                await step_context.context.send_activity(MessageFactory.text("Sembra che la foto non contenga visi prova a ricaricare la foto oppure premi /fine per terminare"))
                return await step_context.replace_dialog( "FaceAnalysisDialog" )
            
            # Viso rilevato ora preparo la scheda da mostrare
            else : 
                
                textAnalysis = await FaceAnalysisDialog.textImage(result.face_attributes)

                card = HeroCard(
                    title="Il tuo risultato",
                    images = [
                        CardImage(url = image.content_url)
                    ],
                    text=textAnalysis
                )
                step_context.values["textAnalysis"] = textAnalysis
                await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))
            

        ## Risposta negativa utente ricarico foto
        else :
            
            await step_context.context.send_activity(MessageFactory.text("Ti riporto all upload, premi /fine per terminare"))
            return await step_context.replace_dialog( "FaceAnalysisDialog" )
            
        
        return await step_context.prompt(
            ConfirmPrompt.__name__+"01",
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
    async def textImage( face : FaceAttributes ) -> str :

        res = ""
         
        
        age = face.age
        gender : Gender = face.gender
        makeup : Makeup = face.makeup
        emotions : Emotion = face.emotion
        
        res = res + f" Ciao, la tua età è di {age} \n"
        if face.glasses != GlassesType.no_glasses:
            res = res+"il risultato potrebbe dare un risultato migliore senza occhiali"
        if gender == Gender.male : 
            facial_hair : FacialHair = face.facial_hair
            if age > 20 and (facial_hair.moustache >= 0.5 or facial_hair.beard >= 0.5) :
                if facial_hair.moustache >= 0.5:
                    res = res+"forse staresti meglio senza baffi potrebbe toglierti qualche anno,"
                if facial_hair.beard >= 0.5:
                    res = res+" già che ci sei potresti tagliare via anche la barba"

        else : 

            if makeup.lip_makeup or makeup.eye_makeup:
                res = res+"forse potresti ottenere una valutazione più accurata da struccata,"
        
        if emotions.happiness >= 0.5 :
            res = res+"\n sembri particolarmente felice oggi"
        
        res = res+", garzie e alla prossima\n"
        return res 
