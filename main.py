from math import sqrt
import pickle as pk
from PIL import Image
import numpy as np
from scipy import spatial
import pygame
import time
from TextWrap import TextWrap

pygame.init()

GUI_SCALE = 1

data = pk.load(open("MapColorsBlockAdjusted.pkl", "rb"))
dataExpanded = []
dataColors = []
shades = [180, 220, 255]
for i in data:
    for j in range(3):
        dataExpanded.append(
            [
                np.array([i*shades[j]//255 for i in i[0]]),
                i[1],
                j
            ]
        )
        dataColors.append(
            np.array([i*shades[j]//255 for i in i[0]])
        )

humanWeights = [0.25, 0.50, 0.25]
def findClosestIndex(color):
    
    return spatial.KDTree(dataColors).query(color)[1]
    
##def sortKeyW(n):
##    return sqrt(sum([(color[i] - n[0][i])**2 * humanWeights[i] for i in range(3)]))
##def findClosestW(color):
##    return min(dataExpanded, key=sortKeyW)

def test(colors):
    import pygcurse, pygame, time
    pygame.init()
    win = pygcurse.PygcurseWindow(3,len(colors),font=pygame.font.Font(None, 30))
    for i in range(len(colors)):
        color = colors[i]
        win.putchar("`", 0, i, None, findClosestW(color)[0])
        win.putchar(".", 1, i, None, color)
        win.putchar("'", 2, i, None, findClosest(color)[0])
        if findClosest(color)[0] != findClosestW(color)[0]:
            time.sleep(2)
    pygame.quit()

def convert(data):
    import tqdm
    # A map is 128x128
    ret = np.empty((128,128), int)
    t = tqdm.tqdm(total=(128*128), desc="Converting...")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ret[i][j] = findClosestIndex(data[i][j])
            t.update(1)
    t.close()
    return ret
        
def fileconvert(filename):
    data = np.asarray(Image.open(filename).convert("RGB"))
    if data.shape[:2] != (128,128):
        raise Exception(f"File too small/big: {filename} ({data.shape[1]}x{data.shape[0]})")
    return convert(data)

def scale(data):
    return type(data)([i*GUI_SCALE for i in data])

def renderimage(surf, data):
    pxSize = 4*GUI_SCALE
    for i in range(128):
        for j in range(128):
            
            pygame.draw.rect(surf,tuple(
                    [int(i) for i in dataExpanded[data[j][i]][0]]
                ),(i*pxSize, j*pxSize, pxSize, pxSize))

font = pygame.font.SysFont(
    [i for i in ["minecraftia",
          "liberationsans",
          "freesans",
          pygame.font.get_default_font()] if i in pygame.font.get_fonts()][0]
, 16*GUI_SCALE)

def renderblock(surf, data, selected):
    pygame.draw.rect(surf, tuple(
        [int(i) for i in dataExpanded[data[selected[::-1]]][0]]),
        scale((512+64, 80, 128, 128)))
    #print(selected[::-1])
    name = dataExpanded[data[selected[::-1]]][1]
    TextWrap(surf, (name if type(name) == str else ", ".join(name)),
            (255,255,255), (512, 0, 256, 80), font)
##    text = font.render((name if type(name) == str else name[0]),
##                       True, (255,255,255))
##    textRect = text.get_rect()
##    textRect.center = (512+128, 16)
##    surf.blit(text, textRect)

def render(surf, data, selected):
    win.fill((0,0,0))
    renderimage(surf, data)
    if selected != None:
        pygame.draw.rect(surf, tuple(
                [255-int(i) for i in dataExpanded[data[selected[::-1]]][0]]
            ),
            scale((selected[0]*4+1, selected[1]*4+1, 2, 2)))
        renderblock(surf, data, selected)
#out = fileconvert("pixelartShip.png")
out = pk.load(open("out.pkl","rb"))
win = pygame.display.set_mode(((512+256)*GUI_SCALE, 512*GUI_SCALE))
pygame.display.set_caption("ImageCraftifier")
renderimage(win,out)
pygame.display.flip()
selected = (100,100)
showDot = (100,100)
draw = True
running = True
while running:
    for event in pygame.event.get():
        #print(event)
        if event.type == 4:
            if event.pos[0] < 512*GUI_SCALE:
                showDot = tuple([i//(4*GUI_SCALE) for i in event.pos])
                draw = True
            else:
                showDot = selected
        if event.type == 5:
            if event.pos[0] < 512*GUI_SCALE:
                showDot = selected = tuple([i//(4*GUI_SCALE) for i in event.pos])
                draw = True
        if event.type == 12: #Quit
            running = False
    if draw:
        render(win, out, showDot)
        pygame.display.flip()
        draw = False
pygame.quit()
        


