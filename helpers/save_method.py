import requests
import asyncio
import json
import datetime
from config import DefaultConfig



async def saveMessage(userId : str , channelID : str , message : str ) -> bool :

    stringUrl =DefaultConfig.BASE_FUNCTION_URL+channelID+"/"+userId+"?operation=add"
    toSend : dict = dict()
    toSend["message"] = message
    toSend["channel"] = channelID
    toSend["id"] = userId
    response = requests.post(stringUrl , json=json.dumps(toSend))
    
    if response.status_code == 200 : 
        return True
    else :
        return False

async def getMessageById(userId : str ,  channelID : str ) -> list :

    stringUrl =DefaultConfig.BASE_FUNCTION_URL+channelID+"/"+userId+"?operation=get"
    response =  requests.post(url = stringUrl ,json="{''}")
    
    if response.status_code == 200 :
        jsonRes = response.json()
        if len(jsonRes["messages"]) > 0 :
            return jsonRes["messages"]
        else : 
            return None
    
    else :
        return None 

async def updateMessage(userId : str ,  channelID : str , messages : list ) -> bool :

    stringUrl =DefaultConfig.BASE_FUNCTION_URL+channelID+"/"+userId+"?operation=update"
    response = requests.post(stringUrl , json=json.dumps(messages))
    
    if response.status_code == 200 : 
        return True
    else :
        return False