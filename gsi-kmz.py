import math
import os

def latlon_to_xy(zoomlevel, lat_deg, lon_deg):
    lat_rad = math.radians(lat_deg)
    n = pow(2, zoomlevel)
    xtile = int(n * ((lon_deg + 180) / 360))
    ytile = int(n * (1 - (math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)) / 2)
    return xtile, ytile

def zxy_to_latlon_nw(z, xtile, ytile):
    n = 2.0 ** z
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def download_tile(z, x, y):
    url = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'.format(z=z, x=x, y=y)
    local_file_name = '{z}_{x}_{y}.png'.format(z=z, x=x, y=y)
    file_name_jpg = '{z}_{x}_{y}.jpg'.format(z=z, x=x, y=y)
    return file_name_jpg

    cmd = 'curl -o {filename} {url}'.format(filename=local_file_name, url=url)
    os.system(cmd)
    os.system('convert {} {}'.format(local_file_name, file_name_jpg))
    os.system('rm {}'.format(local_file_name))

    return file_name_jpg

def generate_kmz(tiles):

    header = '''<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document id="gsi-kmz-map">
'''
    footer = '''</Document></kml>
'''

    overlay_template = '''<GroundOverlay id="overlay_{z}_{x}_{y}">
  <name>{z}_{x}_{y}</name>
  <Icon id="link_{z}_{x}_{y}">
    <href>{filename}</href>
  </Icon>
  <LatLonBox>
    <north>{north}</north>
    <south>{south}</south>
    <east>{east}</east>
    <west>{west}</west>
  </LatLonBox>
</GroundOverlay>
'''

    f = open('doc.kml', 'w')
    f.write(header)
    for z, x, y, filename, n, s, w, e in tiles:
        overlay = overlay_template.format(z=z, x=x, y=y, filename=filename, north=n, south=s, west=w, east=e)
        f.write(overlay)
    f.write(footer)

def main():

    zoom_level = 16

    ll_sw = 36.8523322, 138.7048822
    ll_ne = 36.8842369, 138.742167

    xy_sw = latlon_to_xy(zoom_level, *ll_sw)
    xy_ne = latlon_to_xy(zoom_level, *ll_ne)
    print(xy_sw, xy_ne)

    tiles = []
    for x in range(xy_sw[0], xy_ne[0] + 1):
        for y in range(xy_ne[1], xy_sw[1] + 1):
            print(zoom_level, x, y)
            file_name_jpg = download_tile(zoom_level, x, y)
            ll_nw = zxy_to_latlon_nw(zoom_level, x, y)
            ll_se = zxy_to_latlon_nw(zoom_level, x+1, y+1)
            north, south, west, east = ll_nw[0], ll_se[0], ll_nw[1], ll_se[1]
            print('latlonbox nswe = ', north, south, west, east)
            tiles.append((zoom_level, x, y, file_name_jpg, north, south, west, east))

    generate_kmz(tiles)


if __name__ == '__main__':
    main()

