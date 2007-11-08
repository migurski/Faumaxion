import dymaxion
import os, tempfile, subprocess
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw as IDraw
from PIL.ImageStat import Stat as IStat

min_x, min_y, max_x, max_y = 9999, 9999, -9999, -9999

points = []
img = Image.new('RGB', (1440, 900), 0x00)
draw = IDraw(img)

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

for lat in range(-90, 90, 1):
    for lon in range(-180, 180, 1):
        x, y = dymaxion.project(lon, lat)
        x, y = x, -y # upside-down!

        min_x, min_y = min(x, min_x), min(y, min_y)
        max_x, max_y = max(x, max_x), max(y, max_y)
        
        src_img, src_x, src_y = source(lat, lon)

        print (lat, lon), '->', (x, y), source(lat, lon)
        
        # vips im_extract_area {source} {dest} {left} {top} {width} {height}
        proc = subprocess.Popen(('/opt/local/bin/vips', 'im_extract_area', src_img, tmp, str(src_x), str(src_y), '50', '50'))
        proc.wait()
        
        bit = Image.open(tmp)
        r, g, b = map(int, IStat(bit).mean)
        del bit
        
        points.append((x, y, lat, lon, (r, g, b)))

os.remove(tmp)

print (min_x, min_y), (max_x, max_y)

top, left, bottom, right = 10, 10, img.size[1] - 10, img.size[0] - 10

mx = (right - left) / (max_x - min_x)
my = (bottom - top) / (max_y - min_y)

mx, my = min(mx, my), min(mx, my)

bx = left - mx * min_x
by = top - my * min_y


for (x, y, lat, lon, color) in points:
    x, y = mx * x + bx, my * y + by
    draw.rectangle((x-1, y-1, x+1, y+1), fill=color)

img.save('out.png')