from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from helpers.image_search import Image_Search
from helpers.face_cognitive import FaceCognitive
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions , TextPrompt , AttachmentPrompt , ConfirmPrompt
from botbuilder.dialogs.choices import Choice,ListStyle
from botbuilder.core import (
    MessageFactory, 
    CardFactory
)
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
class DeveloperModeDialog(ComponentDialog):

    def __init__(self, dialog_id : str ):
        super(DeveloperModeDialog , self ).__init__(
            dialog_id
        )
        self.cognitive = FaceCognitive()
        self.search = Image_Search
        
        self.add_dialog(AttachmentPrompt(AttachmentPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__+"MainDev"))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog( TextPrompt(TextPrompt.__name__) )
        self.add_dialog( ConfirmPrompt(ConfirmPrompt.__name__))

        # Main Dialog Developer 
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"DeveloperMain",
                [ self.choice_step , self.execute_step , self.mainLoop_step ]
            )
        )
        
        #Dialog per creare il Group
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"CreateGroup" ,
                [ self.nameGroupPrompt ,  self.saveGroupPrompt ]
            )
        )
        
        #Dialog per creare Person
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"CreatePerson" ,[
                 self.namePersonPrompt , 
                 self.personGroupPrompt , 
                 self.savePersonPrompt  ,
                 self.savePersonData
                 
                 ]
            )
        )
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"PhotoLoop",
                [self.beginLoop_step , self.choiceUploadPhoto , self.choicePhotoLoop , self.eval_choicePhotoLoop ]
            )
        )   
        #Dialog per loop Upload foto
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"UploadPhoto" ,
                [ self.imageUploadStep , self.elabUploadStep ]
            )
        )

        #Dialog per loop Ricerca Web 
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"SearchPhoto" ,
                [ self.imageSearchStep , self.showSearchStep , self.analyzeSearchStep ]
            )
        )
        #Dialog per eliminare group
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"ResetGroup" ,
                [ self.choiceGroup_step , self.resetGroup_step ]
            )
        )
        #Dialog per eliminare person
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"ResetPerson" ,
                [self.choiceGroup_step , self.choicePerson_step , self.resetPerson_step ]
            )
        )
        #Dialog per effettuare Train
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__+"Train",
                [self.choiceGroup_step , self.executeTrain_step]
            )
        )
        
        self.initial_dialog_id = WaterfallDialog.__name__+"DeveloperMain"

    
    async def choice_step(self, step_context : WaterfallStepContext ):
        return await step_context.prompt(
            ChoicePrompt.__name__+"MainDev",
            PromptOptions(
                prompt=MessageFactory.text("Seleziona un'azione"),
                retry_prompt=MessageFactory.text("Effettua una scelta valida, riprova"),
                choices=[
                    Choice(value="Crea Person Group"),
                    Choice(value="Aggiungi Person a Person Group"),
                    Choice(value="Reset Group"),
                    Choice(value="Reset Person"),
                    Choice(value="Effettua Training"),
                    Choice(value="Fine")
                ],
                style=ListStyle.hero_card
            )
        )
    
    async def execute_step(self, step_context: WaterfallStepContext ):
        
        result = step_context.result.value
        await step_context.context.send_activity(MessageFactory.text(result))
        

        if result == "Crea Person Group" : 
            
            return await step_context.begin_dialog(WaterfallDialog.__name__+"CreateGroup")

        elif result == "Aggiungi Person a Person Group" : 
            
            return await step_context.begin_dialog(WaterfallDialog.__name__+"CreatePerson")

        elif result == "Reset Group" :
            return await step_context.begin_dialog(WaterfallDialog.__name__+"ResetGroup")
        elif result == "Reset Person" :
            return await step_context.begin_dialog(WaterfallDialog.__name__+"ResetPerson")
        elif result == "Effettua Training" :
            return await step_context.begin_dialog(WaterfallDialog.__name__+"Train")
        elif result == "Fine" : 
            return await step_context.end_dialog()
        
        else : 
            return await step_context.replace_dialog( WaterfallDialog.__name__+"DeveloperMain")

    async def mainLoop_step(self, step_context: WaterfallStepContext ):
        # Ciclo per main prompt
        return await step_context.replace_dialog( WaterfallDialog.__name__+"DeveloperMain")

    async def nameGroupPrompt(self , step_context : WaterfallStepContext) :

        return await step_context.prompt(
            TextPrompt.__name__ ,
            PromptOptions(
                prompt=MessageFactory.text("Inserisci il nome del Person Group da creare"),
                retry_prompt=MessageFactory.text("Prova a reinserire un valore corretto")
            )
        )
    
    async def saveGroupPrompt(self , step_context : WaterfallStepContext ) : 

        result : str = step_context.result
        
        resp = await self.cognitive.createPersonGroup(str(result))

        if resp is not None :    
            await step_context.context.send_activity(f"Ok creato {resp}")
            return await step_context.end_dialog()
        
        else : 
            
            await step_context.context.send_activity("Qualche problema durante la creazione riprova")
            return await step_context.replace_dialog(WaterfallDialog.__name__+"CreateGroup")
        
    async def imageUploadStep( self , step_context : WaterfallStepContext ) :
        
        images = []

        if step_context.options is not None :
            #input array di Urls
            images = step_context.options
        
        step_context.values["images"] = images
        
        prompt_image = PromptOptions(
            prompt=MessageFactory.text(
                "Inserisci la foto da caricare"
                ),
            retry_prompt=MessageFactory.text(
                "Carica una foto corretta oppure /fine"
                ),
        )
        return await step_context.prompt( AttachmentPrompt.__name__ , prompt_image )
    
    async def elabUploadStep(self ,step_context : WaterfallStepContext ) :
        images : list = step_context.values["images"]
        image = step_context.result[0]
        images.append(image.content_url)

        return await step_context.end_dialog(images) 

    async def imageSearchStep(self , step_context : WaterfallStepContext ) : 
        
        images = []

        if step_context.options is not None :
            #input array di Urls
            images = step_context.options
        
        step_context.values["images"] = images

        return await step_context.prompt( TextPrompt.__name__ , PromptOptions(
            prompt=MessageFactory.text("Inserisci il nome del personaggio da ricercare sul web")
        ) )

    async def showSearchStep( self , step_context : WaterfallStepContext ) :

        to_search = step_context.result
        await step_context.context.send_activity("Seleziona un immagine")
        list_search : list = self.search.searchImage(to_search)
        
        if len(list_search) == 0 :
            await step_context.context.send_activity("Mi dispiace nessuna corrispondenza prova ad usare altre parole")
            return step_context.replace_dialog( WaterfallDialog.__name__+"WebSearch" )
        
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
        
        """
        #Mostro risultati ricerca
        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel
        
        for url in list_search :
            reply.attachments.append( self.generateHeroCardPhoto( url , list_search.index(url)+1 ))
        
        
        await step_context.context.send_activity(reply)
        #carico risulati ricerca nel contesto
        """
        
        step_context.values["searchImages"] = list_search


        return await step_context.prompt(
            ChoicePrompt.__name__ ,
            PromptOptions(
                retry_prompt=MessageFactory.text("Inserisci una scelta valida"),
                choices= DeveloperModeDialog.get_options(len(list_search)),
                style=ListStyle.hero_card
            ),
             
        )

    async def analyzeSearchStep( self , step_context :WaterfallStepContext ) : 
        #ottengo risultato da passo precedente e lo  estraggo dalla lista
        choice = step_context.result.value
        images : list = step_context.values["searchImages"]
        imagesContext : list = step_context.values["images"]

        imagesContext.append(images[int(choice)-2])
        #termino dialogo con il risultato selezionato 
        
        return await step_context.end_dialog(imagesContext)

    async def namePersonPrompt(self , step_context : WaterfallStepContext) :

        return await step_context.prompt(
            TextPrompt.__name__ ,
            PromptOptions(
                prompt=MessageFactory.text("Inserisci il nome della persona da inserire"),
                retry_prompt=MessageFactory.text("Prova a reinserire un valore corretto")
            )
        )

    async def personGroupPrompt(self, step_context : WaterfallStepContext): 
        result = step_context.result
        step_context.values["personName"] = result
        groups : list = await self.cognitive.getGroupPerson()
        
        
        if groups is None :
            await step_context.context.send_activity("Sembra non ci sia nessun gruppo creane prima uno")
            return await step_context.end_dialog()
        else :

            return await step_context.prompt(ChoicePrompt.__name__ , PromptOptions(
                prompt=MessageFactory.text("Seleziona il group dove inserire la person"),
                retry_prompt=MessageFactory.text("La selezione non è valida riprova"),
                choices=DeveloperModeDialog.getGroupListChoice( groups ),
                style=ListStyle.hero_card
            ))
    
    async def savePersonPrompt(self , step_context : WaterfallStepContext ) : 

        groupId = step_context.result.value
        personName = step_context.values["personName"]
        person_id = await self.cognitive.createPerson(personGroupName=groupId , personName=personName)
        #Non è stato possibile creare la person 
        if person_id is None : 
            await step_context.context.send_activity("Qualcosa è andato storto prova a reinserire i dati")
            return await step_context.replace_dialog(WaterfallDialog.__name__+"CreatePerson")
        
        else : 
            step_context.values["groupId"] = groupId
            step_context.values["personId"]= person_id
            return await step_context.begin_dialog( WaterfallDialog.__name__+"PhotoLoop" )
    
    async def beginLoop_step(self, step_context : WaterfallStepContext ) :
        
        step_context.values["images"] = step_context.options
        

        return await step_context.prompt(
                ChoicePrompt.__name__ , PromptOptions(
                    prompt=MessageFactory.text("Come vuoi caricare le foto"),
                    retry_prompt=MessageFactory.text("Seleziona un opzione valida"),
                    choices=[
                        Choice(value = "Web") ,
                        Choice(value="Upload")
                    ],
                    style=ListStyle.hero_card
                )
            )

    async def choiceUploadPhoto(self , step_context : WaterfallStepContext ) : 
        
        result = step_context.result.value

        if result == "Web":
            
            return await step_context.begin_dialog(
                WaterfallDialog.__name__+"SearchPhoto" , 
                step_context.values["images"] )
        else :
            return await step_context.begin_dialog(
                WaterfallDialog.__name__+"UploadPhoto" , 
                step_context.values["images"] )

    async def choicePhotoLoop(self, step_context : WaterfallStepContext) : 

        images = step_context.result
        step_context.values["images"] = images

        return await step_context.prompt(
            ConfirmPrompt.__name__ , PromptOptions(
                prompt=MessageFactory.text("Vuoi caricare altre foto ?")
            )
        )
    
    async def eval_choicePhotoLoop(self, step_context : WaterfallStepContext) :
        
        result = step_context.result
        images = step_context.values["images"]

        if result : 
            return await step_context.replace_dialog(WaterfallDialog.__name__+"PhotoLoop" , images)
        else : 
            return await step_context.end_dialog(images)
    
    async def savePersonData(self , step_context : WaterfallStepContext) :
        #Carico array di url da dialog precedente
        images : list = step_context.result
        
        personId = step_context.values["personId"]
        groupId = step_context.values["groupId"] 
        if len(images) == 0 :
            await step_context.context.send_activity("Qualche problema nel caricamento delle foto riprova")
            await step_context.reprompt_dialog()
            return await step_context.replace_dialog(WaterfallDialog.__name__+"PhotoLoop" , images)
        else : 
            
            personId = await self.cognitive.addFaceToPerson(groupId,personId,images)
            if personId == None :
                await step_context.context.send_activity("Qualche problema nel caricamento delle foto riprova")
                await step_context.reprompt_dialog()
                return await step_context.replace_dialog(WaterfallDialog.__name__+"PhotoLoop" , images)
            
            else :    
                await step_context.context.send_activity("Ok salvato")
                return await step_context.end_dialog()

    async def choiceGroup_step(self, step_context : WaterfallStepContext ):
        
        groups : list = await self.cognitive.getGroupPerson()

        if groups is None :
            
            await step_context.context.send_activity("Sembra non ci sia nessun gruppo creane prima uno")
            return await step_context.end_dialog()
        
        else :
        
            return await step_context.prompt(ChoicePrompt.__name__ , PromptOptions(
                    prompt=MessageFactory.text("Seleziona il group da eliminare"),
                    retry_prompt=MessageFactory.text("La selezione non è valida riprova"),
                    choices=DeveloperModeDialog.getGroupListChoice( groups ),
                    style=ListStyle.hero_card
                ))
    
    async def resetGroup_step(self, step_context : WaterfallStepContext ):
        
        groupId = step_context.result.value

        if groupId == "Torna indietro" :
            return await step_context.end_dialog()

        result = await self.cognitive.deleteGroup(groupId)
        
        if result : 
            await step_context.context.send_activity("Eliminato con successo")
            return await step_context.end_dialog()
        else : 
            await step_context.context.send_activity("Non eliminato riprova")
            return await step_context.end_dialog()
    
    async def choicePerson_step(self, step_context : WaterfallStepContext ):
        
        result = step_context.result.value
        step_context.values["personGroupId"] = result

        persons : list = await self.cognitive.getPerson(result)
        step_context.values["listPerson"] = persons
        
        if persons is None :
            
            await step_context.context.send_activity("Sembra non ci sia nessuna persona nel gruppo creane prima una")
            return await step_context.end_dialog()
        
        else :
        
            return await step_context.prompt(ChoicePrompt.__name__ , PromptOptions(
                    prompt=MessageFactory.text("Seleziona la person da eliminare"),
                    retry_prompt=MessageFactory.text("La selezione non è valida riprova"),
                    choices=DeveloperModeDialog.getPersonListChoice( persons ),
                    style=ListStyle.hero_card
                ))

    async def resetPerson_step(self, step_context : WaterfallStepContext ):
            
            personName = step_context.result.value

            groupId = step_context.values["personGroupId"]

            persons = step_context.values["listPerson"]
            
            personId = None
            
            if personName == "Torna indietro" :
                return await step_context.end_dialog()
            
            for person  in persons : 
                
                if person.name == personName : 
                    personId = person.person_id
                    break
            
            result = await self.cognitive.deletePerson(personId , groupId)

            if result : 
                await step_context.context.send_activity("Eliminato con successo")
                return await step_context.end_dialog()
            else : 
                await step_context.context.send_activity("Non eliminato riprova")
                return await step_context.end_dialog()
    
    async def executeTrain_step(self , step_context : WaterfallStepContext ) : 

        
        groupId = step_context.result.value

        if groupId == "Torna indietro" :
            return await step_context.end_dialog()

        result = await self.cognitive.trainPersonGroup(groupId)
        
        if result : 
            await step_context.context.send_activity("Train eseguito con successo")
            return await step_context.end_dialog()
        else : 
            await step_context.context.send_activity("Errore riprova")
            return await step_context.end_dialog()

    @staticmethod
    def get_options( numChoice : int ):
        
        options = []
        
        for i in range( numChoice) :
            choice = Choice(value=str(i+1))
            options.append(choice)

        return options  

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

    @staticmethod
    def getPersonListChoice( personList : list ) :
        
        choice = list()

        if len(personList) != 0 : 
        
            personLs : Person = None
            i=0
            for a in range(len(personList)) : 
                personLs = personList[i]
                ch = Choice(value=personLs.name)
                choice.append(ch)
                i=i+1
        
        choice.append(Choice(value="Torna indietro"))
        return choice
    
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
