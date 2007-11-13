import sys, gzip, re, random, math, cPickle, operator
import gnomonic, icosahedron, mesh
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

print 'Laying out faces...'
lat, lon = map(float, sys.argv[-2:])
face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))

seen = []
remain = [(None, face, [])]

while len(remain):
    # do a breadth-first traversal of all faces, adjoining them into a single map

    remain.sort()
    kind, face, chain = remain.pop(0)
    
    if face in seen:
        continue
    else:
        seen.append(face)

    if len(chain):
        chain[-1].adjoin(face)
    
    chain = chain[:] + [face]
    
    for neighbor in face.neighbors():
        edge = face.shared(neighbor)
        remain.append((2*edge.kind + len(chain), neighbor, chain))

points = []
img = Image.new('RGB', (600, 600), 0x00)
draw = ImageDraw(img)

re_intersections = re.compile(r'^(-?\d*[05]), (-?\d*[05]): #\w{6} \((\d+), (\d+), (\d+)\)')
re_intersections = re.compile(r'^(-?\d*[02468]), (-?\d*[02468]): #\w{6} \((\d+), (\d+), (\d+)\)')
re_intersections = re.compile(r'^(-?\d*[\d]), (-?\d*[\d]): #\w{6} \((\d+), (\d+), (\d+)\)')

print 'Loading colors...'
colors = cPickle.load(gzip.open('world.topo.bathy-colors.pickle.gz'))

print 'Projecting points...'
for lat in range(-90, 90, 3):
    for lon in range(-180, 180, 3):
        try:
            r, g, b = colors[lat, lon]
        except KeyError:
            continue

        face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))
        x, y = face.project_latlon(lat, lon)
        
        points.append((x, y, lat, lon, (r, g, b)))

min_x = min([x for (x, y, lat, lon, color) in points])
min_y = min([y for (x, y, lat, lon, color) in points])
max_x = max([x for (x, y, lat, lon, color) in points])
max_y = max([y for (x, y, lat, lon, color) in points])

print (min_x, min_y), (max_x, max_y)

top, left, bottom, right = 10, 10, img.size[1] - 10, img.size[0] - 10

mx = (right - left) / (max_x - min_x)
my = (bottom - top) / (max_y - min_y)

mx, my = min(mx, my), min(mx, my)

bx = left - mx * min_x
by = top - my * min_y

print 'Drawing points...'
for (x, y, lat, lon, color) in points:
    x, y = mx * x + bx, my * y + by
    draw.rectangle((x-3, y-3, x, y), fill=color)

img.save('out.png')