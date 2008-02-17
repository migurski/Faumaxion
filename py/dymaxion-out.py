import dymaxion
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

min_x, min_y, max_x, max_y = 9999, 9999, -9999, -9999

points = []
img = Image.new('L', (800, 400), 0x00)
draw = ImageDraw(img)

for lat in range(-90, 90, 3):
    for lon in range(-180, 180, 3):
        x, y = dymaxion.project(lon, lat)
        x, y = x, -y # upside-down!

        min_x, min_y = min(x, min_x), min(y, min_y)
        max_x, max_y = max(x, max_x), max(y, max_y)

        #print (lat, lon), '->', (x, y)
        points.append((x, y, lat, lon))

print (min_x, min_y), (max_x, max_y)

top, left, bottom, right = 10, 10, img.size[1] - 10, img.size[0] - 10

mx = (right - left) / (max_x - min_x)
my = (bottom - top) / (max_y - min_y)

mx, my = min(mx, my), min(mx, my)

bx = left - mx * min_x
by = top - my * min_y


for (x, y, lat, lon) in points:
    x, y = mx * x + bx, my * y + by
    if lat == 0:
        color = 0xFF
    else:
        color = abs(lat) + 0x80
    draw.rectangle((x-1, y-1, x, y), fill=color)

img.save('out.png')