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
from helpers.save_method import saveMessage
from helpers.adaptiveCardHelper import replace
from botbuilder.dialogs.choices import Choice , ListStyle
from botbuilder.core import MessageFactory, UserState , CardFactory
from helpers.face_cognitive import FaceCognitive
from helpers.image_search import Image_Search
from data_models import UserProfile
from azure.cognitiveservices.vision.face.models import * 
from PIL import Image
import os , json
from io import BytesIO
import requests 

class FaceCompareDialog(ComponentDialog):
    def __init__(self, dialog_id: str , user_state : UserState):
        super(FaceCompareDialog, self).__init__(
            dialog_id 
        )
        
        #Inizzializzo CognitiveSev
        self.cognitive = FaceCognitive()
        self.search = Image_Search()

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"Compare",[
                    self.image_1_Upload_step,
                    self.image_1_Check_step,
                    self.image_2_choice_step,
                    self.image_2_evaluateChoice_step,
                    self.elabStep,
                    self.saveStep
                ],
            )
        )

        self.add_dialog( AttachmentPrompt(AttachmentPrompt.__name__+"Compare" , FaceCompareDialog.picture_prompt_validator) )
        self.add_dialog( ConfirmPrompt(ConfirmPrompt.__name__+"Compare") )
        self.add_dialog( ChoicePrompt( ChoicePrompt.__name__+"Compare" ) )
        self.add_dialog( ConfirmPrompt(ConfirmPrompt.__name__+"Save" , default_locale="italian"))

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"2upload",[
                    self.image_2_upload_step,
                    self.image_2_check_step,
                    self.image_2_closeDialog_step 
                ],
            )
        )
                
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"Search",[
                    self.search_step,
                    self.showSearch_step,
                    self.analyzeSearchStep 
                ],
            )
        )
        #Prompt per ricerca personaggio 
        self.add_dialog( TextPrompt(TextPrompt.__name__+"Search") )
        #Prompt per scelta foto con custom validator
        self.add_dialog( ChoicePrompt(ChoicePrompt.__name__+"ChoiceSearch" ) )

       
        
        #dialogo iniziale 
        self.initial_dialog_id = WaterfallDialog.__name__+"Compare"  
    
    async def image_1_Upload_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult:

        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Per ottenere un analisi carica la prima foto"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__+"Compare" , prompt_image )

    async def image_1_Check_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult:
        #memorizzo l'immagine del turno precedente 
        step_context.values["image1"] = step_context.result[0]
        image = step_context.values["image1"]
        
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
            ConfirmPrompt.__name__+"Compare",
            PromptOptions( prompt=MessageFactory.text("La foto è corretta ?")  , style=ListStyle.hero_card )
        )
    
    async def image_2_choice_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult:
        if step_context.result:
            
            choicePrompt = PromptOptions(
                prompt=MessageFactory.text(
                    "Seleziona un' azione da eseguire"
                ),
                retry_prompt=MessageFactory.text(
                    "Effettua una scelta valida, ripova oppure /fine"
                ),
                choices= [
                    Choice(value="Cerca sul web", synonyms=["web"]),
                    Choice( value="Carica immagine" , synonyms=["immagine","locale"])

                ],
                style=ListStyle.hero_card
            )


            return await step_context.prompt( ChoicePrompt.__name__+"Compare" , options=choicePrompt )
        

        else :
            
            await step_context.context.send_activity(MessageFactory.text("Ti riporto all upload, premi /fine per terminare"))
            return await step_context.replace_dialog( WaterfallDialog.__name__+"Compare" )
    
    #step per valutazione scelta
    async def image_2_evaluateChoice_step ( self , step_context : WaterfallStepContext ) : 

        result = step_context.result.value

        if result == "Cerca sul web" or result == "web" : 
            
            return await step_context.begin_dialog(WaterfallDialog.__name__+"Search")
        else :
            
            return await step_context.begin_dialog(WaterfallDialog.__name__+"2upload")

    # step per elaborazini immagini
    async def elabStep(self,step_context: WaterfallStepContext ) -> DialogTurnResult:
    ## Risposta affermativa step precedente 
        
        image1 = step_context.values["image1"]
        image2 = step_context.result
        
        #Trasformo immagine in stream da url
        res1 : Response = requests.get(image1.content_url) 
        res2 : Response = requests.get(image2)
        await step_context.context.send_activity(MessageFactory.text("Ora dovrei elaborare"))
        
        result : VerifyResult  = await self.cognitive.faceCompare( BytesIO(res1.content) , BytesIO(res2.content) )

        # Nessun viso rilevato riporto al caricamento
        if result is None :
            
            await step_context.context.send_activity(MessageFactory.text("Sembra che la foto non contenga visi prova a ricaricare la foto oppure premi /fine per terminare"))
            return await step_context.replace_dialog( WaterfallDialog.__name__+"Compare" )
        
        # Viso rilevato ora preparo la scheda da mostrare
        else : 
            
            confidence = result.confidence * 100
            text = None
            if confidence >=80 :
                text= "Wow siete praticamente uguali "
            elif confidence >=60 : 
                text= "Si nota una certa somiglianza ma non siete proprio gemelli"
            elif confidence >= 30 :
                text = "Potrebbe esserci una certa somiglianza, ma è molto lieve"
            else : 
                text= "Non ho individuato nessuna somiglianza"

            text1 = f"Il tuo grado di somiglianza è {round(confidence,2)}% {text}"
            
            data : dict = dict()

            data["result"] = text1
            data["image_1"] = image1.content_url
            data["image_2"] = image2

            with open( os.path.join(os.getcwd(), "templates/showResultCard.json" ) , "rb") as in_file:
                cardData  = json.load(in_file)

            #sostituisco elementi nel template 
            cardData = await replace(cardData , data)
            
            await step_context.context.send_activity(MessageFactory.attachment(CardFactory.adaptive_card(cardData)))

            """
            card = HeroCard(
                title="Il tuo risultato",
                images = [
                    CardImage(url =image1.content_url),
                    CardImage(url=image2)
                ],
                text=text1 
            )
            
            await step_context.context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))

            """
            step_context.values["textAnalysis"] = text1
            return await step_context.prompt(
            ConfirmPrompt.__name__+"Save",
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

    async def image_2_upload_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult : 
        
        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Carica la seconda foto"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__+"Compare" , prompt_image )

    async def image_2_check_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult :
        #memorizzo l'immagine del turno precedente 
        step_context.values["image2Upl"] = step_context.result[0]
        image = step_context.values["image2Upl"]
        
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
            ConfirmPrompt.__name__+"Compare",
            PromptOptions( prompt=MessageFactory.text("La foto è corretta ?")  , style=ListStyle.hero_card )
        )
    
    async def image_2_closeDialog_step( self , step_context : WaterfallStepContext ) -> DialogTurnResult :
        
        if step_context.result:
            step_context.values["image2Upl"]
            return await step_context.end_dialog(step_context.values["image2Upl"].content_url)
        

        else :
            
            await step_context.context.send_activity(MessageFactory.text("Ti riporto all upload, premi /fine per terminare"))
            return await step_context.replace_dialog( WaterfallDialog.__name__+"2upload" )

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

    
    async def search_step(self , step_context : WaterfallStepContext ) -> DialogTurnResult :

        return await step_context.prompt(
            TextPrompt.__name__+"Search",
            PromptOptions(prompt=MessageFactory.text("Inserisci il nome del personaggio da ricercare sul web"))
        )
    
    async def showSearch_step( self , step_context ) -> DialogTurnResult :

        to_search = step_context.result
        await step_context.context.send_activity("Seleziona un immagine")
        list_search : list = self.search.searchImage(to_search)
        
        if len(list_search) == 0 :
            await step_context.context.send_activity("Mi dispiace nessuna corrispondenza prova ad usare altre parole")
            return step_context.replace_dialog( WaterfallDialog.__name__+"Search" )
        '''
        #Mostro risultati ricerca
        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel
        
        for url in list_search :
            reply.attachments.append( self.generateHeroCardPhoto( url , list_search.index(url)+1 ))
        
        
        await step_context.context.send_activity(reply)
        '''

        #preparo risultati  immagini 
        data : dict = dict()
        i = 0
        for url in list_search :
            index = f"img_{i+1}"
            data[index] = url 
            i+=1
        data["nameCard"] = "Seleziona una scelta"

        with open( os.path.join(os.getcwd(), "templates/showImageCard.json" ) , "rb") as in_file:
            cardData  = json.load(in_file)

        #sostituisco elementi nel template 
        cardData = await replace(cardData , data)
        
        #carico risulati ricerca nel contesto
        step_context.values["searchImages"] = list_search
        
        await step_context.context.send_activity(MessageFactory.attachment(CardFactory.adaptive_card(cardData)))

        return await step_context.prompt(
            ChoicePrompt.__name__+"ChoiceSearch",
            PromptOptions(
                retry_prompt=MessageFactory.text("Inserisci una scelta valida"),
                choices= FaceCompareDialog.get_options(len(list_search)),
                style=ListStyle.hero_card
            ),
             
        )

    async def analyzeSearchStep( self , step_context ) -> DialogTurnResult : 
        #ottengo risultato da passo precedente e lo  estraggo dalla lista
        choice = step_context.result.value
        images : list = step_context.values["searchImages"]

        
        #termino dialogo con il risultato selezionato 
        
        return await step_context.end_dialog(images[int(choice)-1])


    @staticmethod
    def generateHeroCardPhoto( url_send , choice ) -> Attachment :
        
        card = HeroCard(
            title="Immagine "+str(choice),
            images=[
                CardImage(
                    url=url_send
                )
            ]
        )
        return CardFactory.hero_card(card)

    @staticmethod
    def get_options( numChoice : int ):
        
        options = []
        
        for i in range( numChoice) :
            choice = Choice(value=str(i+1))
            options.append(choice)

        return options  