# L'objectif

L'objectif est de réaliser une cartographie des communes ou bureaux de vote où la population est susceptible d'être intéressée par notre discours.
Le premier objectif est de générer de compiler les données +suivante+s :
 * présidentielles 2007
 * présidentielles 2012
 * législatives 2012
 * européennes également

En exploitant les données par bureau de vote.

Il faudra ensuite idéalement identifier les transferts suivants :
 * PS -> PG
 * PS -> FN
 * PS -> abstention
 
L'objectif est aussi de répérer les régions avec un fort vote NON "de gauche" au référendum de 2005.


# Comment ?

Le code est assez simple à comprendre, pour qui connait python.
Les cartes sont générées à partir d'un fichier SVG et de feuilles de style XSLT.

```
sudo apt-get install libsaxonb-java basex inkscape
```

```
make maps
```

```make clean``` supprime les fichiers temporaires.

Pour générer le rapport des résultats des candidats par circonscriptions sur les années 2012 et 2017 aux législatives et présidentielles :

python3 ./get_candidats_par_circo.py

Le rapport est créé dans output/rapport_candidats.pdf

# Contributeurs

Un grand merci à tous ceux qui ont participé à ce projet :

lucasgautheron
aktiur
neokeld

