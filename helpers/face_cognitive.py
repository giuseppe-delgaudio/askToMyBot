from azure.cognitiveservices.vision.face import FaceClient 
from azure.cognitiveservices.vision.face.models import DetectedFace,FaceAttributeType 
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from config import DefaultConfig
import asyncio

class FaceCognitive():

    def __init__(self) : 
        
        self.face_client = FaceClient( DefaultConfig.ENDPOINT , CognitiveServicesCredentials(DefaultConfig.KEYFACE)  )

    async def faceAnalysis(self , image ) -> DetectedFace :
        
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
        
        if not self.detected_face : 

            return None
        else : 
            
            return self.detected_face[0]

        
