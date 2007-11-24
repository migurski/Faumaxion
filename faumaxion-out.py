import sys, gzip, re, random, math, cPickle, operator
import gnomonic, icosahedron, mesh, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

print 'Laying out faces...'
lat, lon = map(float, sys.argv[-2:])
face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))

face.orient_north(lat, lon)
face.center_on(lat, lon)

face.scale(150)
face.translate(300, 300)

faces = face.arrange_neighbors()

points = []
img = Image.new('RGB', (600, 600), 0x00)
draw = ImageDraw(img)

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

print 'Drawing points...'
for (x, y, lat, lon, color) in points:
    draw.rectangle((x-3, y-3, x, y), fill=color)

print 'Drawing lines...'
for face in faces:
    for edge in face.edges():
        x1, y1 = face.project_vertex(edge.vertexA)
        x2, y2 = face.project_vertex(edge.vertexB)
        
        if edge.kind == icosahedron.LAND:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0xCC, 0x00))
        elif edge.kind == icosahedron.WATER:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0x66, 0xFF))

img.save('out.png')