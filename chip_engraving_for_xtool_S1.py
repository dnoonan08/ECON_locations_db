from ppf.datamatrix import DataMatrix
import itertools
import numpy as np
import json
import uuid
import time
import re

from datetime import datetime

from svg.path import parse_path, Move, Line, Close, Path

def sp(num):
    """
    Because svg.path represents x,y coordinates as complex
    numbers, I added this utility function to convert a complex
    number into a (real, imag) array.
    """
    return np.array([num.real, num.imag])

class SVGFont:
    def __init__(self, name='fonts/HersheySans1'):
        import xml.etree.ElementTree as ET
        tree = ET.parse(f'{name}.svg')

        self.paths = {}
        self.horiz = {}
        for glyph in tree.getroot().findall('./{http://www.w3.org/2000/svg}defs/{http://www.w3.org/2000/svg}font/{http://www.w3.org/2000/svg}glyph'):
            attrib = glyph.attrib
            if 'd' in attrib:
                self.paths[attrib['unicode']] = parse_path(attrib['d'])
            else:
                self.paths[attrib['unicode']] = Path()
            self.horiz[attrib['unicode']] = float(attrib['horiz-adv-x'])

        def examine_path(path):
            coords = []
            for seg in path:
                if isinstance(seg, Line) or isinstance(seg, Move) or isinstance(seg, Close):
                    coords.append(sp(seg.end))
            return np.array(coords)

        
        self.coords = {glyph: (examine_path(path)) for glyph, path in self.paths.items()}

        self.xmins = {glyph: np.amin(coord.reshape(-1,2)[:,0], initial=200) for glyph, coord in self.coords.items()}
        self.xmaxs = {glyph: np.amax(coord.reshape(-1,2)[:,0], initial=200) for glyph, coord in self.coords.items()}
        self.ymins = {glyph: np.amin(coord.reshape(-1,2)[:,1], initial=200) for glyph, coord in self.coords.items()}
        self.ymaxs = {glyph: np.amax(coord.reshape(-1,2)[:,1], initial=200) for glyph, coord in self.coords.items()}

        self.overall_ymax = np.amax(np.array(list(self.ymaxs.values())))
        self.overall_ymin = np.amin(np.array(list(self.ymins.values())))

        self.used_ymax = np.amax([self.ymaxs[c] for c in 'ABCDEFGHIJKLMNOPRSTUVWXYZ-0123456789'])
        self.used_ymin = np.amin([self.ymins[c] for c in 'ABCDEFGHIJKLMNOPRSTUVWXYZ-0123456789'])

stick_font = SVGFont('fonts/HersheySans1')
fill_font = SVGFont('fonts/HersheySansMed')
bold_font = SVGFont('fonts/HersheySansBold')

def joinPaths(*paths, start=(0+0j)):
    newpath = []
    for path in paths:
        if len(path):
            if np.abs(path[0].start - start) > 1e-9:
                newpath.append(Move(to=path[0].start))
            newpath.extend(list(path))
            start = path[-1].end
    return Path(*newpath)

def rasterizePATH(path, raster_step=0.03, raster_angle=0):

    starts = np.array([[segment.start.real, segment.start.imag] for segment in path if isinstance(segment, Line) or isinstance(segment, Close)])
    ends =   np.array([[segment.end.real,   segment.end.imag]   for segment in path if isinstance(segment, Line) or isinstance(segment, Close)])
    seg_vecs = ends - starts

    rast_vec = np.array([ np.cos(raster_angle * np.pi/180), np.sin(raster_angle * np.pi/180)])
    perp_vec = np.array([-np.sin(raster_angle * np.pi/180), np.cos(raster_angle * np.pi/180)])

    perp_min = np.amin(np.dot(np.array([starts, ends]), perp_vec))
    perp_max = np.amax(np.dot(np.array([starts, ends]), perp_vec))

    Nsteps = int((perp_max - perp_min) // raster_step)
    perp_offset = ((perp_max - perp_min) - Nsteps * raster_step) / 2
    perp_locs = np.linspace(perp_min + perp_offset, perp_max - perp_offset, Nsteps+1)

    raster_points = (perp_locs[:,np.newaxis] * perp_vec)

    path_segs = []
    for perp_loc in perp_locs:
        Rs = []
        Ss = []
        js = []
        perp = perp_loc*perp_vec
        for j in range(seg_vecs.shape[0]):
            # if np.dot(seg_vecs[j], perp_vec) != 0:
            detinv = (seg_vecs[j,1]*rast_vec[0] - seg_vecs[j,0]*rast_vec[1])
            x, y = (perp - starts[j])
            if detinv != 0:
                S = (-rast_vec[1] * x + rast_vec[0] * y) / detinv
                R = (-seg_vecs[j,1] * x + seg_vecs[j,0] * y) / detinv
            else:
                S = np.nan
                R = np.nan
            Ss.append(S)
            Rs.append(R)
            js.append(j)
        Ss = np.array(Ss)
        Rs = np.array(Rs)

        cut = (Ss >= 0) & (Ss <= 1)
        try:
            assert (sum(cut) % 2) == 0
        except AssertionError:
            print(cut)
            print(Ss[cut])
            raise
            
        Ss = Ss[cut]
        Rs = Rs[cut]

        sort_inds = np.argsort(Rs)

        Ss = Ss[sort_inds]
        Rs = Rs[sort_inds]

        points = (Rs[:,np.newaxis] * rast_vec + perp_loc * perp_vec)
        if len(points) > 0:
            for k in range(points.shape[0]-1):
                if (k % 2) == 0:
                    path_segs.append(Path(Line(start=points[k,0] + points[k,1]*1j, end=points[k+1,0] + points[k+1,1]*1j)))

    return joinPaths(*path_segs)

# This is the original "square spiral" version that works well with the galvo laser at Baylor, but works less well with the gantry laser at FNAL
# def pathRECT(xsize, ysize, raster_step=0.03):
#     paths = []

#     for shrink in np.linspace(raster_step/2, (min(xsize, ysize) - raster_step)/2, int(np.ceil((min(xsize, ysize)/2) / raster_step))):
#         path_segs = []
#         path_segs.append(Line(shrink+1j*shrink, xsize-shrink + 1j*shrink))
#         path_segs.append(Line((xsize-shrink) + 1j*shrink, (xsize-shrink) + 1j*(ysize-shrink)))
#         path_segs.append(Line((xsize-shrink) + 1j*(ysize-shrink), shrink + 1j*(ysize-shrink)))
#         path_segs.append(Line(shrink + 1j*(ysize-shrink), shrink + 1j*shrink))
#         paths.append(Path(*path_segs))
#     return joinPaths(*paths)

# This version just draws the four sides of a box, and lets XCS rasterize it.
def pathRECT(xsize, ysize, raster_step=0.03):
    x0 = raster_step/2
    x1 = xsize - raster_step/2
    y0 = raster_step/2
    y1 = ysize - raster_step/2
    paths = [[
        Line(x0 + 1j*y0, x1 + 1j*y0),
        Line(x1 + 1j*y0, x1 + 1j*y1),
        Line(x1 + 1j*y1, x0 + 1j*y1),
        Line(x0 + 1j*y1, x0 + 1j*y0)
    ]]
    return joinPaths(*paths)
    

def rot(x, y, angle):
    rotx = x * np.cos(angle * np.pi/180) + y *-np.sin(angle * np.pi/180)
    roty = x * np.sin(angle * np.pi/180) + y * np.cos(angle * np.pi/180)
    return rotx, roty

def transformPATH(path, x, y, angle=0, scale=[1,1]):
    segs = []
    for segment in path:
        start_x, start_y = segment.start.real * scale[0], segment.start.imag * scale[1]
        end_x, end_y = segment.end.real * scale[0], segment.end.imag * scale[1]
        rot_start_x, rot_start_y = rot(start_x, start_y, angle)
        rot_end_x, rot_end_y = rot(end_x, end_y, angle)
        segs.append(type(segment)((rot_start_x + x) + (rot_start_y + y)*1j, (rot_end_x + x) + (rot_end_y + y)*1j))
    return Path(*segs)

def maketextPATH(text, font=stick_font):
    items = []
    internal_xs = np.insert(np.cumsum([font.horiz[char] for char in text]), 0, 0)
    for char_i, char in enumerate(text):
        items.extend(transformPATH(font.paths[char], internal_xs[char_i], 0))
    return Path(*items)

def make_barcode(barcode_matrix, size, quiet_pad=1, laser_spot=0.03, framing=False):
    items = []
    data = np.array(barcode_matrix)
    scale = size / (data.shape[0] + 2*quiet_pad)
    iterator = np.nditer(data, flags=['multi_index'])
    if framing:
        xmin = scale*quiet_pad
        xmax = scale*(quiet_pad + data.shape[0])
        ymin = scale*quiet_pad
        ymax = scale*(quiet_pad + data.shape[1])
        return Path(Line(xmin + 1j*ymin, xmin + 1j*ymax),
                    Line(xmin + 1j*ymax, xmax + 1j*ymax),
                    Line(xmax + 1j*ymax, xmax + 1j*ymin),
                    Line(xmax + 1j*ymin, xmin + 1j*ymin))
    else:
        for val in iterator:
            ix, iy = iterator.multi_index
            if val == 1:
                # rotx, roty = rot(scale*(ix + quiet_pad) + laser_spot/2, scale*(iy + quiet_pad) + laser_spot/2, angle)
                items.extend(
                    transformPATH(pathRECT(scale, scale, laser_spot), scale*(ix+quiet_pad), scale*(iy+quiet_pad))
                )

        return joinPaths(items)


def convert_path_to_XCS_fragment(path, x, y, xsize, ysize, power, speed, passes, name=None, color='blue', fill=False):
    itemid = str(uuid.uuid4())
    scale = (1,1)
    skew = (0,0)
    pivot = (0,0)
    lskew = (0,0)
    x0, y0, x1, y1 = path.boundingbox()
    # fill = False
    itemcanvas = {
        'id': itemid,
        'name': name,
        'type': 'PATH',
        'x': x + x0,
        'y': y + y0,
        'angle': 0,
        'scale': {'x': scale[0], 'y': scale[1]},
        'skew': {'x': skew[0], 'y': skew[1]},
        'pivot': {'x': pivot[0], 'y': pivot[1]},
        'localSkew': {'x': lskew[0], 'y': lskew[1]},
        'offsetX': 0,
        'offsetY': 0,
        'localRatio': True,
        'isClosePath': False,
        'zOrder': None,
        'groupTag': str(uuid.uuid4()),
        'layerTag': '#000000',
        'layerColor': '#000000',
        'visible': True,
        'originColor': '#000000',
        'visibleState': True,
        'lockState': False,
        'resourceOrigin': '',
        'width': xsize,
        'height': ysize,
        'isFill': fill,
        'lineColor': 16421416,
        'fillColor': 16421416,
        'points': [],
        'dPath': path.d(),
        'fillRule': 'evenodd',
        'graphicX': 0,
        'graphicY': 0,
        'isCompoundPath': True,
    }
    if fill:
        itemdevice = {
            'isFill': True,
            'type': 'RECT',
            'processingType': 'FILL_VECTOR_ENGRAVING',
            'processIgnore': False,
            'data': {
                'FILL_VECTOR_ENGRAVING': {
                    'materialType': 'customize',
                    'planType': color,
                    'parameter': {
                        'customize': {
                            'power': power,
                            'speed': speed,
                            'repeat': passes,
                            'processingLightSource': color,
                            'density': 300,
                            'bitmapScanMode': 'zMode',
                            'enableKerf': False,
                            'kerfDistance': 0,
                        }
                    }
                }
            }
        }
    else:
        itemdevice = {
            'isFill': False,
            'type': 'PATH',
            'processingType': 'VECTOR_ENGRAVING',
            'processIgnore': False,
            'data': {
                'VECTOR_ENGRAVING': {
                    'materialType': 'customize',
                    'planType': "official",
                    'parameter': {
                        'customize': {
                            'power': power,
                            'speed': speed,
                            'repeat': passes,
                            'processingLightSource': color,
                            'enableKerf': False,
                            'kerfDistance': 0,
                        }
                    }
                }
            }
        }
    return itemid, itemcanvas, itemdevice


def make_proj(items, variety='LASER_PLANE'):
    topId = str(uuid.uuid4())

    canvas = {
        'id': topId,
        'title': 'ECON barcode',
        'layerData': {'#000000': {'name': '{Black}', 'order': 1, 'visible': True}},
        'groupData': {},
        'displays': [dict(itemcanvas, zOrder=itemcount) for (itemcount, (itemid, itemcanvas, itemdevice)) in enumerate(items)],
    }
    
    mode_data = {
        'mode': 'LASER_PLANE',
        'data': {
            'LASER_PLANE': {
                'material': 0,
                'focalLength': 4, #FIXME: Is this right?!?
                'isProcessByLayer': False,
                'pathPlanning': 'auto',
                'fillPlanning': 'separate',
                'scanDirection': 'topToBottom',
                'xcsUsed': [],
                # 'lightSourceMode': 'blue',
                # 'thickness': None,
                # 'perimeter': None,
                # 'diameter': None,
                # 'dreedyTsp': False,
            }
        }
    }
    
    device = {
        'id': 'S1',
        'power': 2,
        'materialList': [],
        'materialTypeList': [],
        'customProjectData': dict(),
        'data': {
            'dataType': 'Map',
            'value': [[topId,
                       {
                           'displays': {
                               'dataType': 'Map',
                               'value': [[itemid, itemdevice] for (itemid, itemcanvas, itemdevice) in items],
                           },
                       }
                      ]]
        },
    }
    device['data']['value'][0][1].update(mode_data)
    
    top = {
        'canvasId': topId,
        'canvas': [canvas],
        'extId': 'S1',
        'extName': 'S1',
        'device': device,
        'version': '1.0.17',
        'created': int(1000 * time.time()),
        'modify': int(1000 * time.time()),
        'ua': 'ECONbarcode/1.0.0',
        'meta': [],
        'cover': '',
    }
    return top

class chip_layout:
    def __init__(self, spot=0.06, font=bold_font):
        self.font = font

        self.ECON_re = re.compile(r'^(?P<HGCAL>320)(?P<ECON>ICEC)(?P<DT>[DT])(?P<grade>.)(?P<lot>.)(?P<SN>\w{5})$')
        
        # All units are millimeters
        self.chip_width = 13.8
        self.chip_height = 13.8
        self.barcode_size = 5.5
        self.barcode_x = self.chip_width - self.barcode_size - 0.5
        self.barcode_y = 1
        self.text_x = 0.75
        self.text_y = 0.75
        self.text_len = self.chip_height - self.text_y - 0.75
        self.text_height = 1.5
        
        self.grade_x = 9
        self.grade_y = 13
        self.grade_len = 3.5
        self.grade_height = 4

        self.N_chips_x = 6
        self.N_chips_y = 15
        self.chip_x0 = 15.45
        self.chip_y0 = 15.40
        self.chip_xstep = 21.00
        self.chip_ystep = 20.30
        
        self.laser_spot = spot
        self.quiet_pad = 1
        
        self.code_parms    = {'power': 64, 'speed': 1361, 'passes': 1, 'color': 'red'}
        self.grade_parms   = {'power': 64, 'speed': 1361, 'passes': 1, 'color': 'red'}
        self.barcode_parms = {'power': 64, 'speed': 1361, 'passes': 1, 'color': 'red'}
        self.bbox_parms    = {'power': 1,  'speed': 4000, 'passes': 1, 'color': 'red'}

    def _make_one_chip(self, code, x, y, angle=0, framing=False):
        match = self.ECON_re.match(code)
        if not match: raise ValueError(f"Bad ECON barcode {code}")
        grade = match.groupdict()['grade']
        code_data_matrix = DataMatrix(code).matrix
        code_path = transformPATH(make_barcode(code_data_matrix, self.barcode_size, quiet_pad=self.quiet_pad, laser_spot=self.laser_spot, framing=framing), self.barcode_x, self.barcode_y)
        code_text = transformPATH(maketextPATH(code, self.font), self.text_x, self.text_y, scale=[self.text_height/self.font.used_ymax, -self.text_height/self.font.used_ymax], angle=90)
        grade_text = transformPATH(maketextPATH(grade, self.font), self.grade_x, self.grade_y, scale=[self.grade_height/self.font.used_ymax, -self.grade_height/self.font.used_ymax])

        x0, y0, x1, y1 = code_text.boundingbox()
        code_text_2 = transformPATH(code_text, 0, 0, scale=[1, self.text_len / (y1 - y0)])
        x0, y0, x1, y1 = code_text_2.boundingbox()
        code_text_3 = transformPATH(code_text_2, 0, self.text_y - y0)
        code_text = code_text_3

        items = [
                 code_path,
                 code_text,
                 # rasterizePATH(code_text, raster_angle=20+angle), # Removed the rasterized stuff because the XCS rasterization works better with the S1.
                 grade_text,
                 # rasterizePATH(grade_text, raster_angle=1-angle)
                ]

        return transformPATH(transformPATH(joinPaths(*items), 0, 0, angle=angle), x, y, angle=0)

    def make_one_chip(self, code, x, y, angle=0, framing=False):
        
        path = self._make_one_chip(code, 0, 0, angle, framing)
        outline = transformPATH(pathRECT(self.chip_width, self.chip_height, raster_step=0), 0, 0, angle=angle)
        return [convert_path_to_XCS_fragment(outline, x, y, 0, 0, power=0, speed=600, passes=1, fill=False),
                convert_path_to_XCS_fragment(path, x, y, 0, 0, power=40, speed=400, passes=1, fill=True)]
    
    def make_tray(self, codes, x=0, y=0, angle=0):
        items = []
        for i in range(self.N_chips_x * self.N_chips_y):
            if codes[i] is not None:
                rotx, roty = rot(self.chip_x0 - self.chip_width/2 + (i%self.N_chips_x)*self.chip_xstep, self.chip_y0 - self.chip_height/2 + (i//self.N_chips_x)*self.chip_ystep, angle)
                items.extend(self.make_one_chip(codes[i], x+rotx, y+roty, angle))
        return items


######the following has been moved to a method in Locations_Database class
# layout = chip_layout()

# with open('test_single_chip.xcs', 'w') as outfile:
#     print(json.dumps(make_proj(layout.make_one_chip('320ICECDAX020002', x=100, y=100, angle=90))), file=outfile)

# # The list of barcodes starts from the "top left" corner, where "down" is the end of
# # the tray with the barcode sticker.  It then moves left to right across the "top" row
# # of 6 chips, then steps down a row and goes left to right, etc., eventually covering
# # all 15 rows of 6 chips.
# list_of_barcodes = [f'320ICECDAX02{i:04d}' for i in range(6*15)]
# # If any location in the tray does not have a chip in it, or if you want to not engrave
# # a chip, put None in the list of barcodes instead of a string.  I'm just blanking out
# # one here as an example.
# list_of_barcodes[13] = None
    
# with open('test_whole_tray.xcs', 'w') as outfile:
#     print(json.dumps(make_proj(layout.make_tray(list_of_barcodes, x=400, y=100, angle=90))), file=outfile)


# # Open the resulting .xcs file(s) in the XCS software and engrave trays of chips.
