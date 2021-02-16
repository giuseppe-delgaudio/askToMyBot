from azure.cognitiveservices.vision.face import FaceClient 
from azure.cognitiveservices.vision.face.models import DetectedFace,FaceAttributeType,VerifyResult 
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from config import DefaultConfig
import asyncio
from io import BytesIO

class FaceCognitive():

    def __init__(self) : 
        
        self.face_client = FaceClient( DefaultConfig.ENDPOINT , CognitiveServicesCredentials(DefaultConfig.KEYFACE)  )

    async def faceAnalysis(self , image : BytesIO , mode : str = None ) -> DetectedFace :
        
        if mode is None :
        
            self.detected_face = self.face_client.face.detect_with_stream(
                image ,
                return_face_attributes=[
                    FaceAttributeType.age,
                    FaceAttributeType.emotion,
                    FaceAttributeType.gender,
                    FaceAttributeType.makeup,
                    FaceAttributeType.facial_hair,
                    FaceAttributeType.glasses
                ],
                recognition_model="recognition_03"

            )
        else :
            self.detected_face = self.face_client.face.detect_with_stream(
                image ,
                recognition_model="recognition_03"

            )
        
        if not self.detected_face : 

            return None
        else : 
            
            return self.detected_face[0]

    async def faceCompare( self , image1 : BytesIO , image2 : BytesIO ) -> VerifyResult :

        self.face1 : DetectedFace =  await self.faceAnalysis(image1 , "b")
        self.face2 : DetectedFace =  await self.faceAnalysis(image2 , "b")

        if (self.face1 != None ) and (self.face2 != None) : 

            result : VerifyResult = self.face_client.face.verify_face_to_face(self.face1.face_id , self.face2.face_id )

            return result
        else : 
            return None
