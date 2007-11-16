import sys, math, icosahedron, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

UP = 'triangle points up'
DOWN = 'triangle points down'

def decompose(face, planar_points, point, depth=0):
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
        
        # i, l, j, k... (or w, d, a, s)
        decompose(face, ((px1, py1), (px12, py12), (px31, py31)), point, depth - 1)
        decompose(face, ((px12, py12), (px2, py2), (px23, py23)), point, depth - 1)
        decompose(face, ((px31, py31), (px23, py23), (px3, py3)), point, depth - 1)
        decompose(face, ((px23, py23), (px31, py31), (px12, py12)), {UP:DOWN, DOWN:UP}[point], depth - 1)

    else:
        # deriveTransformation(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y, c1x, c1y, c2x, c2y)
        
        dim = 256
        mul = 1
        
        tile = Image.new('RGB', (dim*mul, dim*mul), (0x00, 0x00, 0x00))
        draw = ImageDraw(tile)
        
        if point == UP:
            coords = (dim * math.cos(-math.pi/3), dim + dim * math.sin(-math.pi/3)), (dim, dim), (0, dim)
        elif point == DOWN:
            coords = (dim * math.cos(math.pi/3), dim * math.sin(math.pi/3)), (0, 0), (dim, 0)
            
        draw.polygon([(x*mul, y*mul) for (x, y) in coords], fill=(0xFF, 0xFF, 0xFF))

        if mul > 1:
            tile = tile.resize((dim, dim), Image.ANTIALIAS)
        
        (px1, py1), (px2, py2), (px3, py3) = planar_points
        (cx1, cy1), (cx2, cy2), (cx3, cy3) = coords
        
        # the transform from planar points to image coords
        t = transform.deriveTransformation(px1, py1, cx1, cy1, px2, py2, cx2, cy2, px3, py3, cx3, cy3)
        
        input = Image.open('world.1440x720.jpg')
        
        for tile_y in range(dim):
            print tile_y, '...'
        
            for tile_x in range(dim):
                if tile.getpixel((tile_x, tile_y)) != (0x00, 0x00, 0x00):
                    lat, lon = face.unproject_point(*t.unapply(tile_x, tile_y))

                    input_x, input_y = (lon + 180) * 4, (90 - lat) * 4
                    input_x, input_y = int(input_x) % input.size[0], int(input_y) % input.size[1]
                    
                    # print (tile_x, tile_y), (lat, lon), (input_x, input_y)
                    
                    tile.putpixel((tile_x, tile_y), input.getpixel((input_x, input_y)))
        
        tile.save('tile.png')
        
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

face = icosahedron.faces[20]
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
