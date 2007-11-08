import dymaxion
import os, tempfile, subprocess
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw as IDraw
from PIL.ImageStat import Stat as IStat

sources = (('world.topo.bathy.200407.3x21600x21600.A1.v', 'world.topo.bathy.200407.3x21600x21600.B1.v', 'world.topo.bathy.200407.3x21600x21600.C1.v', 'world.topo.bathy.200407.3x21600x21600.D1.v'),
           ('world.topo.bathy.200407.3x21600x21600.A2.v', 'world.topo.bathy.200407.3x21600x21600.B2.v', 'world.topo.bathy.200407.3x21600x21600.C2.v', 'world.topo.bathy.200407.3x21600x21600.D2.v'))

def source(lat, lon):
    if lat > 0:
        row = 0
    else:
        row = 1

    if lon < -90:
        col = 0
    elif lon < 0:
        col = 1
    elif lon < 90:
        col = 2
    else:
        col = 3

    image = sources[row][col]
    
    x = 240 * ((lon + 360) % 90)
    y = 240 * ((90 - lat) % 90) # 90 -> 0, 0 -> 90, -90 -> 180
    
    return image, x, y
    
tmp = tempfile.mkstemp('.png', 'dymax-')[1]

for lat in range(90, -90, -1):
    for lon in range(-180, 180, 1):
        src_img, src_x, src_y = source(lat, lon)
        
        # vips im_extract_area {source} {dest} {left} {top} {width} {height}
        proc = subprocess.Popen(('/opt/local/bin/vips', 'im_extract_area', src_img, tmp, str(src_x), str(src_y), '240', '240'))
        proc.wait()
        
        bit = Image.open(tmp)
        r, g, b = map(int, IStat(bit).mean)
        del bit

        print '%(lat)d, %(lon)d: #%(r)02x%(g)02x%(b)02x (%(r)d, %(g)d, %(b)d)' % locals()

os.remove(tmp)
