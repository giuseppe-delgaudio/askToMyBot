import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "51bd055d-b570-4266-bef7-8920cf7a9708")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "OT~P8yU59xr~L~sado2A_.RFREr3aA155q")
   
    ## Parametri Cognitive Viso ##

    ENDPOINT = "https://faceapiaskbot.cognitiveservices.azure.com/"
    KEYFACE = "6957c16224e1465c956287dfbd04f4c7"

    # Parametri SearchApi

    ENDPOINT_SEARCH = "https://api.bing.microsoft.com/v7.0/images/search"
    KEYSEARCH ="f09d64c900704318b5f733a4182d0e44"


    # Parametri FunctionURL
    
    BASE_FUNCTION_URL = "https://function-db.azurewebsites.net/api/functionDB/"

    # Messaggio di benvenuto

    WELCOME_MESSAGE = """Benvenuto in AskToMyBot \U0001F604 \ncon questo bot potrai ottenere :
    \n\U0001F534 una valutazione del tuo viso con età ed altre informazioni \U0001F466 
    \n\U0001F534 una comparazione tra il tuo viso ed un altro, caricato da te oppure cercato sul web \U0001F468 \U0001F469
    \n\U0001F534 comparare il tuo volto con diversi gruppi di VIP ottenendo il VIP più somigliante \U0001F468 \U0001F31F 
    \n\U0001F534 potrai gestire e visualizzare tutti i risultati salvati \U0001F4BE
    \n\U0001F4CC ricorda nel rispetto della tua privacy nessun tuo dato personale, comprese le immagini, sarà salvato.\n\n
    \U0001F3BA Buon Divertimento \U0001F3BA 
    \n Invia un qualsiasi messaggio per iniziare"""

