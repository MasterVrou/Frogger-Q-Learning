import pygame
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import pickle

#WINDOW
WIN = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Boomer Mutant Frog")

#LOAD IMAGES
FROG_IMAGE = pygame.image.load(os.path.join('textures', 'frog.png'))
FROG_IMAGE = pygame.transform.rotate(FROG_IMAGE, 180)
TRUCK_IMAGE1 = pygame.image.load(os.path.join('textures', 'struck.png'))
TRUCK_IMAGE2 = pygame.image.load(os.path.join('textures', 'struck.png'))
CAR_IMAGE = pygame.image.load(os.path.join('textures', 'car.png'))
CAR_IMAGE1 = pygame.transform.rotate(CAR_IMAGE, 180)
CAR_IMAGE2 = pygame.transform.rotate(CAR_IMAGE, 180)
CAR_IMAGE3 = pygame.transform.rotate(CAR_IMAGE, 180)
FAST_CAR_IMAGE1 = pygame.image.load(os.path.join('textures', 'fast_car.png'))
FAST_CAR_IMAGE2 = pygame.transform.rotate(FAST_CAR_IMAGE1, 180)
FAST_CAR_IMAGE3 = FAST_CAR_IMAGE1
TARGET_IMAGE = pygame.image.load(os.path.join('textures', 'target.png'))

#LENGTH WIDTH
FROG_WIDTH = 60
FROG_HEIGHT = 60

FROG_SPEED = 6

TRUCK_WIDTH = 150
TRUCK_HEIGHT = 60
TRUCK_DANGER_WIDTH = 240

CAR_WIDTH = 114
CAR_HEIGHT = 60
CAR_DANGER_WIDTH = 180

FAST_CAR_WIDTH = 129
FAST_CAR_HEIGHT = 60
FAST_CAR_DANGER_WIDTH = 180

TARGET_WIDTH = 60
TARGET_HEIGHT = 60

#INITIALIZE RECTS
frogRect = pygame.Rect(240, 540, FROG_WIDTH, FROG_HEIGHT)
truckRects = {'truck1': pygame.Rect(0, 420, TRUCK_WIDTH, TRUCK_HEIGHT), 'truck2': pygame.Rect(500, 300, TRUCK_WIDTH, TRUCK_HEIGHT)}
carRects = {'car1': pygame.Rect(100, 480, CAR_WIDTH, CAR_HEIGHT), 'car2': pygame.Rect(430, 360, CAR_WIDTH, CAR_HEIGHT), 'car3': pygame.Rect(100, 240, CAR_WIDTH, CAR_HEIGHT)}
fastCarRects = {'fastcar1': pygame.Rect(100, 180, FAST_CAR_WIDTH, FAST_CAR_HEIGHT), 'fastcar2': pygame.Rect(340, 120, FAST_CAR_WIDTH, FAST_CAR_HEIGHT), 'fastcar3': pygame.Rect(0, 60, FAST_CAR_WIDTH, FAST_CAR_HEIGHT)}
targetRect = pygame.Rect(240, 0, TARGET_WIDTH, TARGET_HEIGHT)

#RANDOM VARIABLES
qTableFile = None
FPS = 50
gameOver = False
gameWon = False
episodes = 10000
steps = 200
up = 0
down = 0
right = 0
left = 0
current = 0

deathPenalty = -20
winReward = 300
stepForwardReward = 10
stepToSidesPenalty = -1
stepBackPenalty = -2


epsilon = 0.9
epsilonDecay = 0.9998

printEvery = 100

qTable = None

learningRate = 0.1
discount = 0.95






#DANGERMAP SCORE INITIALIZATION
dangerMap = {(0,0) : 0}
for j in range(10):
    for i in range(10):
        dangerMap[(i,j)] = 0
        
dangerMap[(4, 0)] = 3
    
        

    

#FUNCTIONS
def drawWindow():
    WIN.fill((0, 0, 0))
    WIN.blit(FROG_IMAGE, (frogRect.x, frogRect.y))
    WIN.blit(TRUCK_IMAGE1, (truckRects['truck1'].x, truckRects['truck1'].y))
    WIN.blit(TRUCK_IMAGE2, (truckRects['truck2'].x, truckRects['truck2'].y))
    WIN.blit(CAR_IMAGE1, (carRects['car1'].x, carRects['car1'].y))
    WIN.blit(CAR_IMAGE2, (carRects['car2'].x, carRects['car2'].y))
    WIN.blit(CAR_IMAGE3, (carRects['car3'].x, carRects['car3'].y))
    WIN.blit(FAST_CAR_IMAGE1, (fastCarRects['fastcar1'].x, fastCarRects['fastcar1'].y))
    WIN.blit(FAST_CAR_IMAGE2, (fastCarRects['fastcar2'].x, fastCarRects['fastcar2'].y))
    WIN.blit(FAST_CAR_IMAGE3, (fastCarRects['fastcar3'].x, fastCarRects['fastcar3'].y))
    WIN.blit(TARGET_IMAGE, (targetRect.x, targetRect.y))
    

     
    pygame.display.update()
  



frogTablePosX = 4
frogTablePosY = 9
firstJumpPosX = frogRect.x
firstJumpPosY = frogRect.y
jumpEnded = True
once = False #pass once for each jump

def frogMovement(dire):
    global frogRect, jumpEnded, firstJumpPosX, firstJumpPosY, frogTablePosX, frogTablePosY, once    
    
    
    if jumpEnded:
        once = False
        firstJumpPosX = frogRect.x
        firstJumpPosY = frogRect.y
    
    if dire == 2:

        if frogRect.x < firstJumpPosX + 60:
            frogRect.x += FROG_SPEED
            jumpEnded = False
            if frogRect.x > 540:
                frogRect.x = 540
                jumpEnded = True    
            
        else:
            jumpEnded = True
                
            if not once:
                frogTablePosX += 1
                once = True

    elif dire == 3:
        if frogRect.x > firstJumpPosX - 60:
            frogRect.x -= FROG_SPEED
            jumpEnded = False
            if frogRect.x < 0:
                frogRect.x = 0
                jumpEnded = True
            
        else:
            jumpEnded = True
                
            if not once:
                frogTablePosX -= 1
                once = True

    elif dire == 4:
        if frogRect.y < firstJumpPosY + 60:
            frogRect.y += FROG_SPEED
            jumpEnded = False
            if frogRect.y > 540:
                frogRect.y = 540
                jumpEnded = True
        else:
            jumpEnded = True
                
            if not once:
                frogTablePosY += 1
                once = True

    elif dire == 1:
        if frogRect.y > firstJumpPosY - 60:
            frogRect.y -= FROG_SPEED
            jumpEnded = False
            if frogRect.y < 0:
                frogRect.y = 0
                jumpEnded = True
        else:
            jumpEnded = True
                
            if not once:
                frogTablePosY -= 1
                once = True

        
    
  
    
def carMovements():
    truckRects['truck1'].x += 2
    truckRects['truck2'].x += 2
    carRects['car1'].x -= 3
    carRects['car2'].x -= 3
    carRects['car3'].x -= 3
    fastCarRects['fastcar1'].x += 4
    fastCarRects['fastcar2'].x -= 4
    fastCarRects['fastcar3'].x += 4
    
    if truckRects['truck1'].x > 600:
        truckRects['truck1'].x = -TRUCK_WIDTH
    if truckRects['truck2'].x > 600:
        truckRects['truck2'].x = -TRUCK_WIDTH
    if carRects['car1'].x < -CAR_WIDTH:
        carRects['car1'].x = 600
    if carRects['car2'].x < -CAR_WIDTH:
        carRects['car2'].x = 600
    if carRects['car3'].x < -CAR_WIDTH:
        carRects['car3'].x = 600
    if fastCarRects['fastcar1'].x > 600:
        fastCarRects['fastcar1'].x = -FAST_CAR_WIDTH
    if fastCarRects['fastcar2'].x < -FAST_CAR_WIDTH:
        fastCarRects['fastcar2'].x = 600
    if fastCarRects['fastcar3'].x > 600:
        fastCarRects['fastcar3'].x = -FAST_CAR_WIDTH

#extension of vehicle danger
def vehicleDangerExt(posInTileMapX, posInTileMapY, danger):
    
    #for second car
    if posInTileMapY == 2:
        posInTileMapX -= 1 
    
    for i in range(10):
        dangerMap[(i, posInTileMapY)] = 0
        
    for i in range(10):
        if i >= posInTileMapX and i <=posInTileMapX + danger:
            dangerMap[(i, posInTileMapY)] = 1
    
    
    
    
                
def vehicleDanger():
    #CARS
    for key, value in carRects.items():
        #danger is the width + 60(kinda) the method is diffrent for the car because it moves the other way
        if value.x >=0 and value.x <=600:
            posInTileMapX = value.x//60-1
            posInTileMapY = value.y//60
            danger = CAR_DANGER_WIDTH//60
            vehicleDangerExt(posInTileMapX, posInTileMapY, danger)
    
    #TRUCKS
    for key, value in truckRects.items():
        if value.x >=0 and value.x <=600:
            posInTileMapX = value.x//60
            posInTileMapY = value.y//60
            danger = TRUCK_DANGER_WIDTH//60
            vehicleDangerExt(posInTileMapX, posInTileMapY, danger)
   
    #FAST CARS
    for key, value in fastCarRects.items():
        #danger is the width + 60(kinda) the method is diffrent for the car because it moves the other way
        posInTileMapX = value.x//60
        posInTileMapY = value.y//60
        danger = FAST_CAR_DANGER_WIDTH//60
        vehicleDangerExt(posInTileMapX, posInTileMapY, danger)
     


        
def checkCollision():
    if frogRect.colliderect(truckRects['truck1']) or frogRect.colliderect(truckRects['truck2']) or frogRect.colliderect(carRects['car1']) or frogRect.colliderect(carRects['car2']) or frogRect.colliderect(carRects['car3']) or frogRect.colliderect(fastCarRects['fastcar1']) or frogRect.colliderect(fastCarRects['fastcar2']) or frogRect.colliderect(fastCarRects['fastcar3']):
        global gameOver
        gameOver = True
    
    if frogRect.colliderect(targetRect):
        global gameWon
        gameWon = True
        
# =============================================================================
# def stateParameters():
#     
#     global frogTablePosX, frogTablePosY, left, right, up, down, current
#     if frogTablePosX > 0:
#         left = dangerMap[(frogTablePosX-1, frogTablePosY)]
#     else:
#         left = 2
#     
#     if frogTablePosX < 9:
#         right = dangerMap[(frogTablePosX+1, frogTablePosY)]
#     else:
#         right = 2
#         
#     if frogTablePosY > 0:
#         up = dangerMap[(frogTablePosX, frogTablePosY-1)]
#     else:
#         up = 2
#     
#     if frogTablePosY < 9:
#         down = dangerMap[(frogTablePosX, frogTablePosY+1)]
#     else:
#         down = 2
#            
#     current = frogTablePosY
# =============================================================================
        
outOfBounds = False
    
 
def main():
    
    global frogTablePosX, frogTablePosY, gameOver, gameWon, jumpEnded, epsilon, epsilonDecay, done, qTable, episodes, outOfBounds
    episodeRewards = []
    
    
    
    if qTableFile is None:
        qTable = {}
    
        for up in range(4):
            for right in range(4):
                for left in range(4):
                    for down in range(4):
                        for current in range(10):
                            qTable[up, right, left, down, current] = [np.random.uniform(-5, 0) for i in range(4)]
                            
    else:
        with open(qTableFile, "rb") as f:
            qTable = pickle.load(f)
    
    
    
    
    for episode in range(episodes):
        print(f"episode: {episode}, epsilon: {epsilon}")
        #if episode % printEvery == 0:
            
            
        episodeReward = 0
        
        #stateParameters()
        jumpEnded = True

        step = 0
        action = 1
        maxQArg = 0
        

        
        while step <= steps:


            #outOfBounds = False
            if outOfBounds:
                jumpEnded = True
            
            
            carMovements()
            vehicleDanger()
            
            
            if jumpEnded:
                
                step += 1
                
                
                
                if frogTablePosX > 0:
                    left = dangerMap[(frogTablePosX-1, frogTablePosY)]
                else:
                    left = 2
                
                if frogTablePosX < 9:
                    right = dangerMap[(frogTablePosX+1, frogTablePosY)]
                else:
                    right = 2
                    
                if frogTablePosY > 0:
                    up = dangerMap[(frogTablePosX, frogTablePosY-1)]
                else:
                    up = 2
                
                if frogTablePosY < 9:
                    down = dangerMap[(frogTablePosX, frogTablePosY+1)]
                else:
                    down = 2
                       
                current = frogTablePosY
                
                
                
                
                currentState = (up, right, left, down, current)
                
                
                
                if np.random.random() > epsilon:
                    maxQArg = np.argmax(qTable[currentState])
                    action = maxQArg + 1
                    
                    #print(action)
                    
                else:
                    action = np.random.randint(1, 5)
                
                

                
                

                if action == 1 and up == 2:
                    outOfBounds = True
                if action == 2 and right == 2:
                    outOfBounds = True
                if action == 3 and left == 2:
                    outOfBounds = True
                if action == 4 and down == 2:
                    outOfBounds = True

                
                
                if not outOfBounds:
                    frogMovement(action)
                    checkCollision()
                
                if gameOver or outOfBounds:
                    reward = deathPenalty
                elif gameWon:
                    reward = winReward
                else:
                    if action == 2 or action == 3:
                        reward = stepToSidesPenalty
                    elif action == 1:
                        reward = stepForwardReward
                    elif action == 4:
                        reward = stepBackPenalty
                        
                        
                #stateParameters()
                #we compasate for this error by making the danger of the cars bigger
                #print ("up ", up, " right ", right, " left ", left, " frogTablePosY ", frogTablePosY, "frogTablePosX", frogTablePosX)
                
                if gameOver:
                    newQ = deathPenalty
                elif gameWon:
                    newQ = winReward
                else:
                    

                    
                    if frogTablePosX > 0:
                        left = dangerMap[(frogTablePosX-1, frogTablePosY)]
                    else:
                        left = 2
                    
                    if frogTablePosX < 9:
                        right = dangerMap[(frogTablePosX+1, frogTablePosY)]
                    else:
                        right = 2
                        
                    if frogTablePosY > 0:
                        up = dangerMap[(frogTablePosX, frogTablePosY-1)]
                    else:
                        up = 2
                    
                    if frogTablePosY < 9:
                        down = dangerMap[(frogTablePosX, frogTablePosY+1)]
                    else:
                        down = 2
                           
                    current = frogTablePosY
                
                
                
                
                
                    nextState = (left, right, up, down, current)
                    maxNextQ = np.max(qTable[nextState])
                    currentQ = qTable[currentState][action-1]
                    
                    newQ = (1-learningRate) * currentQ + learningRate * (reward + discount * maxNextQ)
                      
                    
                qTable[currentState][action-1] = newQ
                
                if reward == winReward or reward == deathPenalty or step == steps:
                    frogRect.x = 240
                    frogRect.y = 540
                    frogTablePosX = 4
                    frogTablePosY = 9
                    gameOver = False
                    gameWon = False
                    jumpEnded = True
                    outOfBounds = False
                    break
                
                    
                
            else:
                frogMovement(action)
                checkCollision()
                    
            #print(frogTablePosX, " ", frogTablePosY)
            
            episodeReward += reward
            drawWindow()
        
            
        episodeRewards.append(episodeReward)
        epsilon *= epsilonDecay
        
    rewardsAverage = np.convolve(episodeRewards, np.ones((printEvery,)) / printEvery, mode="valid")
    plt.plot([i for i in range(len(rewardsAverage))], rewardsAverage)
    plt.ylabel(f"reward {printEvery}ma")
    plt.xlabel("episode #")
    plt.show()
    
    with open(f"qTable-{int(time.time())}.pickle", "wb") as f:
        pickle.dump(qTable, f)
        

if __name__ == "__main__":
    main()
    
    
