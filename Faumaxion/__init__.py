import threading, math, time, StringIO, urllib
import icosahedron
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

UP = 'triangle points up'
DOWN = 'triangle points down'
SIDE = 256 # known native size of a triangular tile

class TilePaster(threading.Thread):
    """ Thread for the pasting of tiles.
    """
    def __init__(self, img, srcPath, affineData, lock, verbose=False):
        """ srcPath is for srcImage(), affineData is for PIL.Image.transform()
        """
        self.img = img
        self.srcPath = srcPath
        self.affineData = affineData
        self.lock = lock
        self.verbose = verbose
        threading.Thread.__init__(self)

    def run(self):
        # just the image acquisition happens outside the lock
        src = srcImage(self.srcPath, self.verbose)

        if self.lock.acquire():
            src = src.transform(self.img.size, Image.AFFINE, self.affineData)
            self.img.paste(src, (0, 0), src)
            self.lock.release()

        return
        
def srcImage(srcPath, verbose):
    """ Return a tile image for a source path list.
    """
    url = 'http://faumaxion.modestmaps.com/' + '/'.join(srcPath) + '.png'
    img = Image.open(StringIO.StringIO(urllib.urlopen(url).read()))
    
    if verbose:
        print 'Downloaded', url

    return img

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

def apply_face(img, srcPath, face, point, corners=None, paste=False, verbose=False):
    """ Paste a face onto an image.
    
        Return a list of pasted faces and affine transformations.
    
        Arguments:
            img is a PIL.Image instance.
            srcPath is a list, e.g. ('01', 'i', 'j').
            face is an icosahedron.Face.
            point is UP or DOWN.
            corners is an optional list of three (x, y) pairs of projected triangle corners.
            paste is a boolean flag for doing the actual pasting, or now
    """
    if corners is None:
        corners = map(face.project_vertex, face.vertices())
    
    if not face_in_image(corners, img):
        return []

    # face coords
    (f1x, f1y), (f2x, f2y), (f3x, f3y) = corners
    
    # magnification factor of current face image.
    magnify = math.hypot(f2x - f3x, f2y - f3y) / SIDE
    
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
    
            applied = []
            
            for p, corners in subcorners:
                if p == 'k':
                    applied += apply_face(img, srcPath + [p], face, {UP:DOWN, DOWN:UP}[point], corners, paste, verbose)
                else:
                    applied += apply_face(img, srcPath + [p], face, point, corners, paste, verbose)

            return applied
                    
        except IOError:
            # uh oh: most likely a nested source image failed
            # to load, go on to the current zoom level, below.
            pass

    if verbose:
        print 'Applying %s at %d%% magnification' % ('/'.join(srcPath), magnify*100)
    
    if point == UP:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (SIDE/2, SIDE - SIDE * math.sin(math.pi/3)), (SIDE, SIDE), (0, SIDE)
    elif point == DOWN:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (SIDE/2, SIDE * math.sin(math.pi/3)), (0, 0), (SIDE, 0)
    else:
        raise Exception('Unknown point')
    
    # transform the source tile into place
    t = transform.deriveTransformation(f1x, f1y, i1x, i1y, f2x, f2y, i2x, i2y, f3x, f3y, i3x, i3y)

    if paste:
        src = srcImage(srcPath).transform(img.size, Image.AFFINE, t.data())
        img.paste(src, (0, 0), src)
    
    return [(srcPath, t.data())]

class Map:

    def __init__(self, dimensions, center, side, join=icosahedron.LAND):
        self.width, self.height = dimensions
        self.latitude, self.longitude = center
        self.side = side
        self.join = join
        
    def draw(self, verbose=False):
        """ Draw map out to a PIL.Image and return it.
        """
        # image and filename
        img = Image.new('RGB', (self.width, self.height), 0x00)
        
        if verbose:
            print 'Laying out faces...'

        face = icosahedron.vertex2face(icosahedron.latlon2vertex(self.latitude, self.longitude))
        
        face.orient_north(self.latitude, self.longitude)
        face.center_on(self.latitude, self.longitude)
        
        face.scale(self.side)
        face.translate(img.size[0]/2, img.size[1]/2)
        
        faces = face.arrange_neighbors(self.join)
        
        if verbose:
            print 'Drawing faces...'
        
        applied = []
        
        for f, face in icosahedron.faces.items():
            if face in faces:
                applied += apply_face(img, ['%02d' % f], face, UP, verbose=verbose)
                
        lock = threading.Lock()
        
        pasters = [TilePaster(img, srcPath, affineData, lock, verbose) for (srcPath, affineData) in applied]
        
        for paster in pasters:
            paster.start()
    
        while True:
            time.sleep(.25)
            remaining = sum(map(int, [paster.isAlive() for paster in pasters]))
            if remaining == 0:
                break
        
        if verbose:
            print 'Drawing lines...'

        draw = ImageDraw(img)
        
        for face in faces:
            for edge in face.edges():
                x1, y1 = face.project_vertex(edge.vertexA)
                x2, y2 = face.project_vertex(edge.vertexB)
                
                if edge.kind == icosahedron.LAND:
                    draw.line((x1, y1, x2, y2), fill=(0x00, 0xCC, 0x00, 0x80))
                elif edge.kind == icosahedron.WATER:
                    draw.line((x1, y1, x2, y2), fill=(0x00, 0x66, 0xFF, 0x80))

        return img
