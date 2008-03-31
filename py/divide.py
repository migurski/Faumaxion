import os, os.path, sys, math, Faumaxion, struct
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

UP = 'triangle points up'
DOWN = 'triangle points down'

world = open('world.topo.bathy.200407.v', 'r')

def latlon_rgba(lat, lon):
    """ Get (r, g, b) color at specified (lat, lon) in degrees.
    """
    w, h = 86400, 43200
    
    x, y = (lon + 180) * 240, (90 - lat) * 240
    x, y = int(x) % w, int(y) % h
    
    off = (y * w) + x
    
    world.seek(0x40 + off * 3)
    r, g, b = struct.unpack('BBB', world.read(3))
    
    return r, g, b, 0xFF

def decompose(face, name, planar_points, point, depth=6):
    """ Vertices are expected in clockwise order, with first being the point.
    """
    if point == UP:
        pass
    elif point == DOWN:
        pass
    else:
        raise Exception('Unknown point')
    
    print 'working on', name
    
    dim = 256
    
    # image x, y coordinates of triangle points
    if point == UP:
        coords = (dim/2, dim + dim * math.sin(-math.pi/3)), (dim, dim), (0, dim)
    elif point == DOWN:
        coords = (dim/2, dim * math.sin(math.pi/3)), (0, 0), (dim, 0)

    (px1, py1), (px2, py2), (px3, py3) = planar_points
    (cx1, cy1), (cx2, cy2), (cx3, cy3) = coords
    
    # the transform from planar points to image x, y coords
    t = Faumaxion.transform.deriveTransformation(px1, py1, cx1, cy1, px2, py2, cx2, cy2, px3, py3, cx3, cy3)
    
    if depth:
        # there's further to go; gather up sub-triangles and stitch them together
        px12, py12 = .5 * (px1 + px2), .5 * (py1 + py2)
        px23, py23 = .5 * (px2 + px3), .5 * (py2 + py3)
        px31, py31 = .5 * (px3 + px1), .5 * (py3 + py1)
        
        parts = [('i', ((px1, py1), (px12, py12), (px31, py31))),
                 ('l', ((px12, py12), (px2, py2), (px23, py23))),
                 ('j', ((px31, py31), (px23, py23), (px3, py3))),
                 ('k', ((px23, py23), (px31, py31), (px12, py12)))]
        
        parts.sort()
        
        surtile = Image.new('RGBA', (dim*2, dim*2), (0x00, 0x00, 0x00, 0x00))
        
        # i, l, j, k...
        for p, coords in parts:
            if p == 'k':
                subtile = decompose(face, name + '/' + p, coords, {UP:DOWN, DOWN:UP}[point], depth - 1)
            else:
                subtile = decompose(face, name + '/' + p, coords, point, depth - 1)
                
            if point == UP:
                if p == 'i':
                    x, y = dim/2, int(dim + dim * math.sin(-math.pi/3))
                elif p == 'l':
                    x, y = dim, dim
                elif p == 'j':
                    x, y = 0, dim
                elif p == 'k':
                    x, y = dim/2, int(2*dim + dim * math.sin(-math.pi/3))
            elif point == DOWN:
                if p == 'i':
                    x, y = dim/2, int(-dim * math.sin(-math.pi/3))
                elif p == 'l':
                    x, y = 0, 0
                elif p == 'j':
                    x, y = dim, 0
                elif p == 'k':
                    x, y = dim/2, int(-dim - dim * math.sin(-math.pi/3))

            surtile.paste(subtile, (x, y), subtile)

        colors, mask = surtile.resize((dim, dim), Image.BICUBIC), surtile.resize((dim, dim), Image.LINEAR)

        tile = Image.new('RGBA', (dim, dim), (0x00, 0x00, 0x00, 0x00))
        tile.paste(colors, (0, 0), mask)

        for y in range(dim):
            for x in range(dim):
                alpha = tile.getpixel((x, y))[3]
                if 0x00 < alpha and alpha < 0xFF:
                    lat, lon = face.unproject_point(*t.unapply(x, y))
                    tile.putpixel((x, y), latlon_rgba(lat, lon))
        
    else:
        # this is it, go pixel-by-pixel
        tile = Image.new('RGBA', (dim, dim), (0x00, 0x00, 0x00, 0x00))
        mask = Image.new('L', (dim, dim), 0x00)

        ImageDraw(mask).polygon(coords, fill=0xFF)

        for y in range(dim):
            for x in range(dim):
                if mask.getpixel((x, y)) != 0x00:
                    lat, lon = face.unproject_point(*t.unapply(x, y))
                    tile.putpixel((x, y), latlon_rgba(lat, lon))
    
    filename = name + '.png'
    print 'saving', filename
    
    try:
        tile.save(filename)
    except IOError:
        os.makedirs(os.path.dirname(filename))
        tile.save(filename)

    return tile

if __name__ == '__main__':
    
    for f in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20):
        face = Faumaxion.icosahedron.faces[f]
        latlons = map(Faumaxion.icosahedron.vertex2latlon, face.vertices())
        xys = map(face.project_vertex, face.vertices())
        
        (x1, y1), (x2, y2), (x3, y3) = xys
        decompose(face, 'out/tiles/%02d' % f, xys, UP)
