import requests
from config import DefaultConfig

class Image_Search():
         
    @staticmethod
    def searchImage( searchParam : str ) -> list :

        subscription = DefaultConfig.KEYSEARCH
        search_url = DefaultConfig.ENDPOINT_SEARCH

        headers = {"Ocp-Apim-Subscription-Key" : subscription}

        params  = {"q": searchParam , "license": "all", "imageType": "photo" , "count" : "4" , "setLang" : "it"}
        response = requests.get( search_url , headers=headers , params = params )
        response.raise_for_status()
        search_result = response.json()
        thumbnail_urls = [img["thumbnailUrl"] for img in search_result["value"][:4]]
        
        return thumbnail_urls
