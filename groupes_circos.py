import json
import csv
from geopy.distance import vincenty
from dicttoxml import dicttoxml

groupes = []
emplacements = []

with open('data/groupes.json') as data_file:    
    groupes = json.load(data_file)

groupes = groupes['_items']

with open('data/circo_gps.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if row[0] == 'EU_circo':
            continue

        dpt_format = ''
        circo_format = ''

        try:
          dpt_format = '{:02d}'.format(int(row[4]))
        except:
          dpt_format = row[4]

        try:
          circo_format = '{:02d}'.format(int(row[7]))
        except:
          circo_format = row[7]

        emplacement = {}
        try:
          emplacement['lat'] = float(row[11])
          emplacement['long'] = float(row[12])
        except:
          continue

        emplacement['circo'] = dpt_format + circo_format
        emplacements.append(emplacement)

for g in groupes:
    if 'location' in g and 'country_code' in g['location'] and g['location']['country_code'] and 'coordinates' in g:
        nearest_circo = ''
        nearest_distance = 25000
        for emplacement in emplacements:
            if abs(emplacement['lat']-float(g['coordinates']['coordinates'][1])) > 0.5 or abs(emplacement['long']-float(g['coordinates']['coordinates'][0])) > 0.5:
                continue

            distance = vincenty((emplacement['lat'],emplacement['long']), (float(g['coordinates']['coordinates'][1]), float(g['coordinates']['coordinates'][0]))).kilometers
            if distance < nearest_distance:
                nearest_circo = emplacement['circo']
                nearest_distance = distance


        g['circo'] = nearest_circo

xml = dicttoxml(groupes, custom_root='groupes', attr_type=False)
open("groupes.xml", "wb").write(xml) 
