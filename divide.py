import sys, math, icosahedron, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

UP = 'triangle points up'
DOWN = 'triangle points down'

def decompose(face, planar_points, point, depth=1):
    """ Vertices are expected in clockwise order, with first being the point.
    """
    if point == UP:
        pass
    
    elif point == DOWN:
        pass
    
    else:
        raise Exception('Unknown point')
    
    if depth:
        (px1, py1), (px2, py2), (px3, py3) = planar_points
        
        px12, py12 = .5 * (px1 + px2), .5 * (py1 + py2)
        px23, py23 = .5 * (px2 + px3), .5 * (py2 + py3)
        px31, py31 = .5 * (px3 + px1), .5 * (py3 + py1)
        
        decompose(face, ((px1, py1), (px12, py12), (px31, py31)), point, depth - 1)
        decompose(face, ((px12, py12), (px2, py2), (px23, py23)), point, depth - 1)
        decompose(face, ((px31, py31), (px23, py23), (px3, py3)), point, depth - 1)
        decompose(face, ((px23, py23), (px31, py31), (px12, py12)), {UP:DOWN, DOWN:UP}[point], depth - 1)

    else:
        # deriveTransformation(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y, c1x, c1y, c2x, c2y)
        
        geo_locations = [face.unproject_point(x, y) for (x, y) in planar_points]
        
        print planar_points
        print geo_locations
        draw.polygon([(lon * mul, (90 - lat) * mul) for (lat, lon) in geo_locations], outline=0xFF)
        draw.polygon([((lon - 360) * mul, (90 - lat) * mul) for (lat, lon) in geo_locations], outline=0x99)
        draw.polygon([((lon + 360) * mul, (90 - lat) * mul) for (lat, lon) in geo_locations], outline=0x99)

mul = 4

# dim = 256
# mul = 4
# 
# tile = Image.new('L', (dim*mul, dim*mul), 0x00)
# draw = ImageDraw(tile)
# 
# #coords = 0, 0, dim*mul, 0, dim*mul * math.cos(math.pi/3), dim*mul * math.sin(math.pi/3)
# #draw.polygon(coords, fill=0x80)
# #print coords
# 
# coords = (0, dim*mul), (dim*mul, dim*mul), (dim*mul * math.cos(-math.pi/3), dim*mul + dim*mul * math.sin(-math.pi/3))
# decompose(coords)
# 
# tile = tile.resize((dim, dim), Image.ANTIALIAS)
# tile.save('tile.png')

world = Image.new('L', (360 * mul, 180 * mul), 0x00)
draw = ImageDraw(world)

for lat in (0, 90):
    for lon in (0, 90, 180, 270):
        draw.rectangle((lon*mul, lat*mul, (lon + 90) * mul, (lat + 90) * mul), outline=0x66)

for face in icosahedron.faces.values():
    latlons = map(icosahedron.vertex2latlon, face.vertices())
    xys = map(face.project_vertex, face.vertices())
    
    (x1, y1), (x2, y2), (x3, y3) = xys
    # coords = (0, dim), (dim, dim), (dim * math.cos(-math.pi/3), dim + dim * math.sin(-math.pi/3))
    
    #print latlons
    #print xys
    #print coords
    
    decompose(face, xys, UP)

world = world.resize((720, 360), Image.ANTIALIAS)
world.save('world.png')
