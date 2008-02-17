import sys, optparse
import Faumaxion

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
    
Output file, center, dimensions, and triangle side options are required.""")

parser.add_option('-v', '--verbose', dest='verbose',
                  help='Make a bunch of noise',
                  action='store_true')

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

parser.add_option('-j', '--join', dest='join',
                  help='Which kind of edges to join: LAND or WATER, defaults to LAND',
                  type='choice', choices=('LAND', 'WATER'), default='LAND')

if __name__ == '__main__':

    (options, args) = parser.parse_args()
    
    if options.join == 'WATER':
        map = Faumaxion.Map((parser.width, parser.height), (parser.latitude, parser.longitude), parser.side, Faumaxion.icosahedron.WATER)

    elif options.join == 'LAND':
        map = Faumaxion.Map((parser.width, parser.height), (parser.latitude, parser.longitude), parser.side, Faumaxion.icosahedron.LAND)

    map.draw(options.verbose).save(options.outfile)
