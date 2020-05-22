from math import sqrt, ceil
import pickle as pk
from PIL import Image
import numpy as np
from scipy import spatial
import pygame
import time
from TextWrap import TextWrap
import sys

try:
    import better_exceptions as be
    sys.excepthook = be.excepthook
except ImportError:
    pass
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
    cache = {}
    print("Converting image...")
    step = 512 / data.shape[0]
    win = pygame.display.set_mode((512,32))
    pygame.display.set_caption("Converting...")
    # A map is 128x128
    ret = np.empty(data.shape[:2], int)
    w = 0
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if tuple(data[i][j]) in cache:
                ret[i][j] = cache[tuple(data[i][j])]
            else:
                tmp = findClosestIndex(data[i][j])
                ret[i][j] = tmp
                cache[tuple(data[i][j])] = tmp
        w += step
        pygame.draw.rect(win,(0,255,0),(0,0,round(w),32))
        pygame.display.flip()
    return ret
        
def fileconvert(filename):
    data = np.asarray(Image.open(filename).convert("RGB"))
##    if data.shape[:2] != (128,128):
##        raise Exception(f"File too small/big: {filename} ({data.shape[1]}x{data.shape[0]})")
    return convert(data)

def scale(data):
    return type(data)([i*GUI_SCALE for i in data])

def renderimage(surf, data, pos):
    pxSize = 4*GUI_SCALE
    for i in range(128):
        for j in range(128):
            x, y = i+pos[0], j+pos[1]
            if x < data.shape[1] and y < data.shape[0]:
                color = tuple([int(k) for k in dataExpanded[data[y][x]][0]])
            else:
                color = ((0,0,0) if (x+y)%2 == 0 else (127,127,127))
            pygame.draw.rect(surf,color,(i*pxSize, j*pxSize, pxSize, pxSize))

font = pygame.font.SysFont(
    [i for i in ["minecraftia",
          "liberationsans",
          "freesans",
          pygame.font.get_default_font()] if i in pygame.font.get_fonts()][0]
, 16*GUI_SCALE)

def renderblock(surf, data, selected, pos):
    if selected[0]+pos[0] >= data.shape[1] or selected[1]+pos[1] >= data.shape[0]:
        return
    dataBlock = dataExpanded[data[selected[1]+pos[1],selected[0]+pos[0]]]
    color = tuple([int(i) for i in dataBlock[0]])
    pygame.draw.rect(surf, tuple([255-i for i in color]),
        scale((512+64, 80, 128, 128)))
    pygame.draw.rect(surf, color, scale((512+65, 81, 126, 126)))
    #print(selected[::-1])
    name = dataBlock[1]
    TextWrap(surf, (name if type(name) == str else ", ".join(name)),
            (255,255,255), scale((512, 0, 256, 80)), font)
    TextWrap(surf, "rgb(" + ", ".join([str(i) for i in color]) + ")",
            (255,255,255), scale((512, 224, 256, 80)), font)
    slope = dataBlock[2]
    pygame.draw.line(surf, (255,255,255), *scale(
        ((512+64, 256+(slope*64)), (512+192, 384-(slope*64)))
    ), 10*GUI_SCALE)
    TextWrap(surf, f"x:{selected[0]+1+pos[0]}, z:{selected[1]+1+pos[1]}",
            (255,255,255), scale((512, 384, 256, 80)), font)

def render(surf, data, selected, pos):
    win.fill((0,0,0))
    renderimage(surf, data, pos)
    if selected != None:
        if selected[0]+pos[0] < data.shape[1] and selected[1]+pos[1] < data.shape[0]:
            pygame.draw.rect(surf, tuple(
                    [255-int(i) for i in dataExpanded[data[selected[1]+pos[1],selected[0]+pos[0]]][0]]
                ),
                scale((selected[0]*4+1, selected[1]*4+1, 2, 2))
            )
        renderblock(surf, data, selected, pos)



### MAIN ###
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} file")
    sys.exit(1)

torange = lambda n, low, high: min(high, max(low, n))

out = fileconvert(sys.argv[1])
win = pygame.display.set_mode(((512+256)*GUI_SCALE, 512*GUI_SCALE))
pygame.display.set_caption("ImageCraftifier")
renderimage(win,out,(0,0))
pygame.display.flip()
selected = None
showDot = None
draw = True
running = True
pos = [0,0]
while running:
    for event in pygame.event.get():
        #print(event)
        if event.type == 1: #Gain/lose focus
            if event.gain == 0 and event.state == 1:
                showDot = selected
        if event.type == 4: #Move mouse
            if event.pos[0] < 512*GUI_SCALE:
                showDot = tuple([i//(4*GUI_SCALE) for i in event.pos])
                if event.buttons[0]:
                    direction = [-i for i in event.rel]
                    for i in range(2):
                        pos[i] += direction[i] / (4*GUI_SCALE)
                        pos[i] = torange(pos[i], 0, max(out.shape[1-i]-128,0))
                draw = True
            else:
                showDot = selected
        if event.type == 5: #Press mouse button
            if event.pos[0] < 512*GUI_SCALE:
                if event.button == 1:
                    showDot = selected = tuple([i//(4*GUI_SCALE) for i in event.pos])
                    draw = True
                #  4
                # 6 7
                #  5
                if event.button in range(4, 8):
                    direction = [(0, -1), (0, 1), (-1, 0), (1, 0)][event.button - 4]
                    for i in range(2):
                        pos[i] += direction[i] * 16
                        pos[i] = torange(pos[i], 0, max(ceil(out.shape[1-i]/16-8)*16,0))
                    draw = True
            
        if event.type == 12: #Quit
            running = False
    if draw:
        render(win, out, showDot, [round(i) for i in pos])
        pygame.display.flip()
        draw = False
pygame.quit()
        


