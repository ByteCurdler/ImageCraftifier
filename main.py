from math import sqrt
import pickle as pk
from PIL import Image
import numpy as np
from scipy import spatial
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

out = fileconvert("pixelartShip.png")
import pygcurse, pygame, time
pygame.init()
win = pygcurse.PygcurseWindow(128,128,font=pygame.font.Font(None, 10))
win.autoupdate = False
for i in range(128):
    for j in range(128):
        win.putchar("·", i, j, None, tuple(
            [int(i) for i in dataExpanded[out[j][i]][0]])
        )
    win.update()
pygcurse.waitforkeypress()
pygame.quit()
        


