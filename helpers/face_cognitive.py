
from azure.cognitiveservices.vision.face import FaceClient 
from azure.cognitiveservices.vision.face.models import DetectedFace,FaceAttributeType,VerifyResult , IdentifyResult , IdentifyCandidate , SimilarFace
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person , TrainingStatus , PersonGroup
from config import DefaultConfig
import asyncio
import time
from io import BytesIO
import requests

class FaceCognitive():

    def __init__(self) : 
        
        self.face_client = FaceClient( DefaultConfig.ENDPOINT , CognitiveServicesCredentials(DefaultConfig.KEYFACE)  )

    async def faceAnalysis(self , image : BytesIO , mode : str = None ) -> DetectedFace :
        
        if mode != "onlyId" :
        
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
            self.detected_face = self.face_client.face.detect_with_stream(image , recognition_model="recognition_03")
    
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
    
    async def createPersonGroup( self , personGroupName : str) :
            
            try :
                group : PersonGroup = self.face_client.person_group.create( person_group_id=personGroupName.lower() , name=personGroupName.lower() , recognition_model="recognition_03" )

            except : 
                return None
            
            return personGroupName.lower()

    async def createPerson( self, personGroupName : str , personName : str ) -> bool: 
        
        try:
            
            pers : Person = self.face_client.person_group_person.create( person_group_id= personGroupName.lower() , name= personName.lower() )

        except Exception as e :
            print(e)
            return None
        
        return pers.person_id
    
    async def addFaceToPerson( self, personGroup : str , personId : str  , image : list ) : 

        try :
            for imageUrl in image :
                res : Response = requests.get(imageUrl)
                self.face_client.person_group_person.add_face_from_stream(person_group_id=personGroup , person_id= personId , image=BytesIO(res.content) , detection_model='detection_03' )
            
            return personId

        except Exception as e : 
            print(e)
            return None

    async def trainPersonGroup( self , personGroup : str ) -> bool :

        result : bool = True 
        self.face_client.person_group.train(person_group_id=personGroup)
        
        while(True) :

            status : TrainingStatus = self.face_client.person_group.get_training_status(person_group_id=personGroup) 

            if ( status.status is TrainingStatusType.succeeded ) : 
                break
            elif ( status.status is TrainingStatusType.failed ) :
                result = False
                break
            time.sleep(2)
        
        return result
    
    async def getGroupPerson( self ) -> list : 

        groupList = self.face_client.person_group.list()
        if len(groupList) > 0 : 
            return groupList
        else : 
            return None  

    async def deleteGroup(self , groupId : str) -> bool : 

        try : 
            self.face_client.person_group.delete(person_group_id=groupId)
        except Exception as e :
            print(e)
            return False

        return True 

    async def getPerson(self , groupId : str ) -> bool :       
        
        personList = self.face_client.person_group_person.list(person_group_id=groupId)

        if len(personList) > 0 : 
            return personList
        else : 
            return None
    
    async def deletePerson(self , personId : str , personGroupId :str) -> bool : 
        
        try :     
            self.face_client.person_group_person.delete(person_group_id=personGroupId , person_id=personId)
        except Exception as e :
            print(e)
            return False

        return True 
     
    async def identifyPerson(self , image : BytesIO , person_group :str  ) -> list : 

        try :    
            toIdentify : DetectedFace = await self.faceAnalysis( image , "onlyId" ) 

            if toIdentify.face_id is not None : 
                #Preparo lista per result 
                result = list()

                #Ricerca nel group della face
                faceIds = list()
                faceIds.append(str(toIdentify.face_id))
                identify : IdentifyResult = self.face_client.face.identify(face_ids=faceIds , person_group_id=person_group ,max_num_of_candidates_returned=1 , confidence_threshold=0.1 )
                #identify : SimilarFace = self.face_client.face.find_similar(face_id=toIdentify.face_id ,max_num_of_candidates_returned=1 )
                if len(identify) > 0 : 
                    #candidate : SimilarFace = identify[0]
                    candidate : IdentifyCandidate = identify[0].candidates[0]
                    #ids = candidate.face_id
                    ids = candidate.person_id
                    result.append(candidate.confidence)
                    person : Person = self.face_client.person_group_person.get(person_group_id=person_group , person_id=ids  )
                    result.append(person)
                    return result
                    
        except Exception as e :
            print(e)
            return None 


