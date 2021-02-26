import sys
import traceback
from datetime import datetime
from http import HTTPStatus
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes
from config import DefaultConfig
from dialogs.mainDialog import MainDialog
from bots.askToMyBot import AskToMyBot

CONFIG = DefaultConfig()

# Creazione Bot Adapter.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Cattura errori
async def on_error(context: TurnContext, error: Exception):

    print(f"\n [on_turn_error]: { error }", file=sys.stderr)
    traceback.print_exc()

    # Invio messaggio di errore 
    await context.send_activity("Ops ... c'è stato quale problema, riprova tra poco")
    # Invio traccia errori se il channel è l'emulatore
    
    if context.activity.channel_id == "emulator":
        
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )

        
        await context.send_activity(trace_activity)

    #Elimino lo stato
    await CONVERSATION_STATE.delete(context)



# Bind per cattura eventi errori 
ADAPTER.on_turn_error = on_error

MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)


main_Dialog = MainDialog()
BOT = AskToMyBot(CONVERSATION_STATE , main_Dialog)


#Messaggi in entrata su /api/messages.
async def messages(req: Request) -> Response:

    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)

#Funzione di avvio bot
def init_func(argv):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.router.add_post("/api/messages", messages)
    return APP

if __name__ == "__main__":
    APP = init_func(None)
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
