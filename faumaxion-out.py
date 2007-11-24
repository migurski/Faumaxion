import sys, gzip, re, random, math, cPickle, operator
import gnomonic, icosahedron, mesh, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

print 'Laying out faces...'
lat, lon = map(float, sys.argv[1:3])
face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))

face.orient_north(lat, lon)
face.center_on(lat, lon)

face.scale(int(sys.argv[3]))
face.translate(300, 300)

faces = face.arrange_neighbors()

points = []
img = Image.new('RGB', (600, 600), 0x00)

UP = 'triangle points up'
DOWN = 'triangle points down'

def apply_face(img, srcName, face, point, corners=None):
    """ Corners is a list of three (x, y) pairs
    """
    if corners is None:
        corners = map(face.project_vertex, face.vertices())
    
    # face coords
    (f1x, f1y), (f2x, f2y), (f3x, f3y) = corners
    
    # face bounding box
    xmin, ymin, xmax, ymax = min(f1x, f2x, f3x), min(f1y, f2y, f3y), max(f1x, f2x, f3x), max(f1y, f2y, f3y)
    
    if xmax < 0 or ymax < 0 or xmin > img.size[0] or ymin > img.size[1]:
        # face is not visible, so don't bother
        return

    src = Image.open(srcName)
    magnify = math.hypot(f2x - f3x, f2y - f3y) / src.size[0]
    
    if magnify > 1.35:
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
                    apply_face(img, '%s/%s%s' % (srcName[:-4], p, srcName[-4:]), face, {UP:DOWN, DOWN:UP}[point], corners)
                else:
                    apply_face(img, '%s/%s%s' % (srcName[:-4], p, srcName[-4:]), face, point, corners)

            return
                    
        except IOError:
            # uh oh, go on to the current zoom level, below
            pass

    print 'Rendering %s at %d%% magnification' % (srcName, magnify*100)
    
    # image coords
    if point == UP:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (128, 256 - 256 * math.sin(math.pi/3)), (256, 256), (0, 256)
    elif point == DOWN:
        (i1x, i1y), (i2x, i2y), (i3x, i3y) = (128, 256 * math.sin(math.pi/3)), (0, 0), (256, 0)
    else:
        raise Exception('Unknown point')
    
    t = transform.deriveTransformation(f1x, f1y, i1x, i1y, f2x, f2y, i2x, i2y, f3x, f3y, i3x, i3y)
    src = src.transform(img.size, Image.AFFINE, t.data())
    
    img.paste(src, (0, 0), src)

print 'Drawing faces...'
for f, face in icosahedron.faces.items():
    if face in faces:
        apply_face(img, 'out/tiles/%02d.png' % f, face, UP)

print 'Drawing lines...'
draw = ImageDraw(img)

for face in faces:
    for edge in face.edges():
        x1, y1 = face.project_vertex(edge.vertexA)
        x2, y2 = face.project_vertex(edge.vertexB)
        
        xmin, ymin, xmax, ymax = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        
        if xmax < 0 or ymax < 0 or xmin > img.size[0] or ymin > img.size[1]:
            # edge is not visible, so don't bother
            continue
    
        if edge.kind == icosahedron.LAND:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0xCC, 0x00))
        elif edge.kind == icosahedron.WATER:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0x66, 0xFF))

img.save('out.png')