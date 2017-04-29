import csv
import codecs
from collections import deque
from unidecode import unidecode

lignes = []

with codecs.open('raw/pres_2017.csv', mode='r', encoding='iso-8859-1') as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    n = 0
    for row in reader:
        n = n+1
        if n == 1:
            continue

        ligne_base = ['1'] + row[:21]
        for i in range(1, 12):
            row[21+(i-1)*7+2] = unidecode(row[21+(i-1)*7+2][:4])
            lignes.append(ligne_base + row[21+(i-1)*7 + 1:21+i*7+1])

with open('data/pres_2017.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(lignes)
        
