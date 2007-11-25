import sys, re, math, urllib, StringIO, optparse
import gnomonic, icosahedron, mesh, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

UP = 'triangle points up'
DOWN = 'triangle points down'
DIM = 256 # known native size of a triangular tile

def srcImage(srcPath):
    """ Return a tile image for a source path list.
    """
    url = 'http://faumaxion.modestmaps.com/' + '/'.join(srcPath) + '.png'
    
    print 'Downloading', url, '...'
    return Image.open(StringIO.StringIO(urllib.urlopen(url).read()))

    return Image.open('out/tiles/' + '/'.join(srcPath) + '.png')

def face_in_image(corners, img):
    """ Return true if the triangle defined by 3 (x, y) corners is visible inside the image.
    """
    # face coords
    (f1x, f1y), (f2x, f2y), (f3x, f3y) = corners
    
    # face bounding box
    fxmin, fymin, fxmax, fymax = min(f1x, f2x, f3x), min(f1y, f2y, f3y), max(f1x, f2x, f3x), max(f1y, f2y, f3y)
    
    if fxmin >= 0 and fymin >= 0 and fxmax <= img.size[0] and fymax <= img.size[1]:
        # simple bbox check: face is certainly visible
        return True

    elif fxmax <= 0 or fymax <= 0 or fxmin >= img.size[0] or fymin >= img.size[1]:
        # simple bbox check: face is certainly not visible
        return False
        
    else:
        # face *may* not be visible... perform AABB overlap check
        # see: http://www.harveycartel.org/metanet/tutorials/tutorialA.html#section2
        for side in [((f1x, f1y), (f2x, f2y)), ((f2x, f2y), (f3x, f3y)), ((f3x, f3y), (f1x, f1y))]:
            (s1x, s1y), (s2x, s2y) = side
            s3x, s3y = icosahedron.derive_third_point(s1x, s1y, s2x, s2y)
            
            # twist it around so the chosen side is vertical
            t = transform.deriveTransformation(s1x, s1y, 0, 0, s2x, s2y, 0, 2, s3x, s3y, 1, 1)
            
            # no longer needed
            del s1x, s1y, s2x, s2y, s3x, s3y
            
            # transformed triangle coords
            ft1x, ft1y = t.apply(f1x, f1y)
            ft2x, ft2y = t.apply(f2x, f2y)
            ft3x, ft3y = t.apply(f3x, f3y)
            
            # transformed image coords
            it1x, it1y = t.apply(0, 0)
            it2x, it2y = t.apply(0, img.size[1])
            it3x, it3y = t.apply(img.size[0], 0)
            it4x, it4y = t.apply(img.size[0], img.size[1])
            
            # bounding boxen
            fxmin, fymin, fxmax, fymax = min(ft1x, ft2x, ft3x), min(ft1y, ft2y, ft3y), max(ft1x, ft2x, ft3x), max(ft1y, ft2y, ft3y)
            ixmin, iymin, ixmax, iymax = min(it1x, it2x, it3x, it4x), min(it1y, it2y, it3y, it4y), max(it1x, it2x, it3x, it4x), max(it1y, it2y, it3y, it4y)
            
            if fxmax <= ixmin or fxmin >= ixmax or fymax <= iymin or fymin >= iymax:
                return False
            
        return True

def apply_face(img, srcPath, face, point, corners=None):
    """ Paste a face onto an image.
    
        Arguments:
            img is a PIL.Image instance.
            srcPath is a list, e.g. ('01', 'i', 'j').
            face is an icosahedron.Face.
            point is UP or DOWN.
            corners is an optional list of three (x, y) pairs of projected triangle corners.
    """
    if corners is None:
        corners = map(face.project_vertex, face.vertices())
    
    if not face_in_image(corners, img):
        return

    # face coords
    (f1x, f1y), (f2x, f2y), (f3x, f3y) = corners
    
    # magnification factor of current face image.
    magnify = math.hypot(f2x - f3x, f2y - f3y) / DIM
    
    if magnify > 1.4:
        try:
            # split each side in half
            f12x, f12y = .5 * (f1x + f2x), .5 * (f1y + f2y)
            f23x, f23y = .5 * (f2x + f3x), .5 * (f2y + f3y)
            f31x, f31y = .5 * (f3x + f1x), .5 * (f3y + f1y)
            
            subcorners = [('i', ((f1x, f1y), (f12x, f12y), (f31x, f31y))),
                          ('l', ((f12x, f12y), (f2x, f2y), (f23x, f23y))),
                          ('j', ((f31x, f31y), (f23x, f23y), (f3x, f3y))),
                          ('k', ((f23x, f23y), (f31x, f31y), (f12x, f12y)))]
    
            for p, corners in subcorners:
                if p == 'k':
                    apply_face(img, srcPath + [p], face, {UP:DOWN, DOWN:UP}[point], corners)
                else:
                    apply_face(img, srcPath + [p], face, point, corners)

            return
                    
        except IOError:
            # uh oh: most likely a nested source image failed
            # to load, go on to the current zoom level, below.
            pass

    print 'Rendering %s at %d%% magnification' % ('/'.join(srcPath), magnify*100)
    
    if point == UP:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (DIM/2, DIM - DIM * math.sin(math.pi/3)), (DIM, DIM), (0, DIM)
    elif point == DOWN:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (DIM/2, DIM * math.sin(math.pi/3)), (0, 0), (DIM, 0)
    else:
        raise Exception('Unknown point')
    
    # transform the source tile into place
    t = transform.deriveTransformation(f1x, f1y, i1x, i1y, f2x, f2y, i2x, i2y, f3x, f3y, i3x, i3y)
    src = srcImage(srcPath).transform(img.size, Image.AFFINE, t.data())
    
    img.paste(src, (0, 0), src)

def parseWidthHeight(option, opt, values, parser):
    if values[0] > 0 and values[1] > 0:
        parser.width = values[0]
        parser.height = values[1]
        
    else:
        raise optparse.OptionValueError('Image dimensions must be positive (got: width %d, height %d)' % values)

def parseSide(option, opt, value, parser):
    if value > 0:
        parser.side = value
        
    else:
        raise optparse.OptionValueError('Triangle side must be positive (got: %d)' % value)

def parseCenter(option, opt, values, parser):
    if -90 <= values[0] and values[0] <= 90 and -180 <= values[1] and values[1] <= 180:
        parser.latitude = values[0]
        parser.longitude = values[1]
        
    elif -90 > values[0] or values[0] > 90:
        raise optparse.OptionValueError('Latitude must be within (-90, 90) (got: %.2f)' % values[0])
    
    elif -180 > values[1] or values[1] > 180:
        raise optparse.OptionValueError('Longitude must be within (-180, 180) (got: %.2f)' % values[1])

parser = optparse.OptionParser(usage="""faumaxion-out.py [options]

Example map centered on San Francisco and Oakland:
    python faumaxion-out.py -o out.png -c 37.8 -122.3 -s 200 -d 800 600
    
All options are required.""")

parser.add_option('-o', '--out', dest='outfile',
                  help='Write to output file')

parser.add_option('-c', '--center', dest='center', nargs=2,
                  help='Center (lat, lon)', type='float',
                  action='callback', callback=parseCenter)

parser.add_option('-d', '--dimensions', dest='dimensions', nargs=2,
                  help='Pixel dimensions (width, height) of resulting image', type='int',
                  action='callback', callback=parseWidthHeight)

parser.add_option('-s', '--triangle-side', dest='side', nargs=1,
                  help='Pixel length of triangle side', type='int',
                  action='callback', callback=parseSide)

if __name__ == '__main__':

    (options, args) = parser.parse_args()
    
    # image and filename
    img = Image.new('RGB', (parser.width, parser.height), 0x00)
    out = options.outfile
    
    print 'Laying out faces...'
    face = icosahedron.vertex2face(icosahedron.latlon2vertex(parser.latitude, parser.longitude))
    
    face.orient_north(parser.latitude, parser.longitude)
    face.center_on(parser.latitude, parser.longitude)
    
    face.scale(parser.side)
    face.translate(img.size[0]/2, img.size[1]/2)
    
    faces = face.arrange_neighbors(icosahedron.LAND)
    
    print 'Drawing faces...'
    for f, face in icosahedron.faces.items():
        if face in faces:
            apply_face(img, ['%02d' % f], face, UP)
    
    print 'Drawing lines...'
    draw = ImageDraw(img)
    
    for face in faces:
        for edge in face.edges():
            x1, y1 = face.project_vertex(edge.vertexA)
            x2, y2 = face.project_vertex(edge.vertexB)
            
            if edge.kind == icosahedron.LAND:
                draw.line((x1, y1, x2, y2), fill=(0x00, 0xCC, 0x00))
            elif edge.kind == icosahedron.WATER:
                draw.line((x1, y1, x2, y2), fill=(0x00, 0x66, 0xFF))
    
    img.save(out)