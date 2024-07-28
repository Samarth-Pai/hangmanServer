from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_STR = os.getenv("MONGODB_STR")

app = FastAPI(debug=True)
client = MongoClient(MONGODB_STR)
db = client["hangmanServer"]
matchRoom = db["matchRoom"]
playRoom = db["playRoom"]

class matchRoomModel(BaseModel):
    mode: str
    roomID: str
    matchFound: bool

class playRoomModel(BaseModel):
    mode: str
    word: str   
    roomID: str
    guessedIndices: list
    player1Time: float
    player2Time: float
    player1Turn: bool
    finishedPlaying: bool
    submittedAlpha: str

class timeModel(BaseModel):
    playerNo: int
    timing: float
    
    
@app.post("/createMatchRoom")
def createMatchRoom(roomDetails: matchRoomModel):
    matchRoom.insert_one(roomDetails.model_dump())
    

@app.get("/matchStatus/{roomID}")
def getMatchStatus(roomID: str):
    return matchRoom.find_one({"roomID":roomID})["matchFound"]

@app.get("/findMatchRoom/{mode}")
def findMatchRoom(mode: str):
    status = matchRoom.find_one({"mode":mode,"matchFound":False})
    if status:
        return status["roomID"]
    
@app.put("/declareMatch/{roomID}")
def declareMatch(roomID: str):
    matchRoom.find_one_and_update({"roomID":roomID},{"$set":{"matchFound":True}})

@app.get("/getTiming/{roomID}/{playerNo}")
def getTiming(roomID: str,playerNo: int):
    return playRoom.find_one({"roomID":roomID})[f"player{playerNo}Time"]

@app.post("/shiftToPlay/{roomID}")
def shiftToPlay(playDetails: playRoomModel,roomID: str):
    print(playDetails.model_dump())
    playRoom.insert_one(playDetails.model_dump())
    
@app.get("/getWord/{roomID}")
def getWord(roomID: str):
    return playRoom.find_one({"roomID":roomID})["word"]

@app.get("/getGuessedIndices/{roomID}")
def getGuessedIndices(roomID: str):
    return playRoom.find_one({"roomID":roomID})["guessedIndices"]

@app.put("/updateTiming/{roomID}")
def updateTiming(timings: timeModel,roomID: str):
    timingDict = timings.model_dump()
    timing = timingDict.get("timing")
    playerNo = timingDict.get("playerNo")
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{f"player{playerNo}Time":timing}})

@app.get("/playerOneTurn/{roomID}")
def playerOneTurn(roomID: str):
    return playRoom.find_one({"roomID":roomID})["player1Turn"]      

@app.put("/changePlayerTurn/{roomID}")
def changePlayerTurn(roomID: str):
    player1Turn = playRoom.find_one({"roomID":roomID})["player1Turn"]
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{"player1Turn":not player1Turn}})

@app.get("/getSubmittedAlpha/{roomID}")
def getSubmittedAlpha(roomID: str):
    return playRoom.find_one({"roomID":roomID})["submittedAlpha"]

@app.post("/submitAlpha/{roomID}/{alpha}")
def submitAlpha(roomID: str,alpha: str):
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{"submittedAlpha":alpha}})

@app.put("/flushAlpha/{roomID}")
def flushAlpha(roomID: str):
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{"submittedAlpha":""}})

@app.put("/turnPlayer/{roomID}")
def turnPlayer(roomID: str):
    playerTurn = playRoom.find_one({"roomID":roomID})["player1Turn"]
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{"player1Turn":not playerTurn}})

@app.get("/isPlaying/{roomID}")
def isPlaying(roomID: str):
    return not playRoom.find_one({"roomID":roomID})["finishedPlaying"]

@app.put("/declareFinish/{roomID}")
def declareFinish(roomID: str):
    playRoom.find_one_and_update({"roomID":roomID},{"$set":{"finishedPlaying":True}})