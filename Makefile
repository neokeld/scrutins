SHELL=/bin/bash

SOURCE_DIR := processors
BUILD_DIR := output

# les fichiers et URLS dans le meme ordre
FILES := pres_2012.csv pres_2007.csv 2005.csv legi_2012.csv pres_2017.csv
URLS := \
    https://www.data.gouv.fr/s/resources/election-presidentielle-2012-resultats-par-bureaux-de-vote-1/20150925-102751/PR12_Bvot_T1T2.txt \
    https://www.data.gouv.fr/s/resources/election-presidentielle-2007-resultats-par-bureaux-de-vote/20151001-154056/PR07_Bvot_T1T2.txt \
    https://www.data.gouv.fr/s/resources/referendum-de-2005-resultats-par-bureaux-de-vote/20150925-112918/RF05_BVot.txt \
    https://www.data.gouv.fr/s/resources/elections-legislatives-2012-resultats-par-bureaux-de-vote/20150925-103435/LG12_Bvot_T1T2.txt \
    https://www.data.gouv.fr/s/resources/election-presidentielle-des-23-avril-et-7-mai-2017-resultats-definitifs-du-1er-tour-par-bureaux-de-vote/20170427-100955/PR17_BVot_T1_FE.txt

RAW_FILES := $(addprefix raw/,$(FILES))
DATA_FILES := $(addprefix data/,$(FILES))

PROCESSORS := $(wildcard processors/*.xsl)
#SVG_FILES := $(PROCESSORS:processors/%.xsl=output/%.svg)
#PNG_FILES := $(SVG_FILES:.svg=.png)

.PHONY: download circonscriptions

all: download circonscriptions

#maps: output/non_2005.png output/hollande.png

circonscriptions: circos.xml groupes.xml
	python get_candidats_par_circo.py && \
	saxonb-xslt -s:circos.xml -xsl:processors/circonscriptions.xsl -o:circonscriptions/document.tex -ext:on && \
	cd circonscriptions && (pdflatex --shell-escape -interaction=nonstopmode document.tex || true) && \
	(pdflatex --shell-escape -interaction=nonstopmode document.tex || true)


#$(PNG_FILES) $(SVG_FILES): | output

#$(PNG_FILES): %.png: %.svg
#	inkscape -f $< -e "$@"

#$(SVG_FILES): output/%.svg: processors/%.xsl maps/communes.svg communes.xml
#	saxonb-xslt -s:maps/communes.svg -xsl:$< -o:$@ -ext:on

output:
	mkdir output

groupes.xml:
	python groupes_circos.py

#communes.xml: communes.json
#	basex -q "let \$$file := \"communes.json\" return json-to-xml(file:read-text(\$$file))" > communes.xml

#communes.json: $(DATA_FILES)
#	python get_election_data.py

circos.xml: circos.json
	basex -q "let \$$file := \"circos.json\" return json-to-xml(file:read-text(\$$file))" > circos.xml

circos.json: data/pres_2012.csv data/legi_2012.csv data/pres_2017.csv
	python get_circo.py

$(DATA_FILES): | data

$(DATA_FILES): data/%.csv: raw/%.csv
	cp $< $@

# override previous rule
data/2005.csv: raw/2005.csv
	# les numeros de bureau de vote de Caen ont un probleme
	sed 's/Caen;\([0-9]\{2\}\);\([0-9]\);/Caen;\1\2;/' $< > $@

data/pres_2017.csv: raw/pres_2017.csv
	python transform_2017.py

data:
	mkdir data

$(RAW_FILES): download

download:
	mkdir -p raw
	files=( $(RAW_FILES) ); urls=( $(URLS) ); \
	for i in $${!files[@]}; do \
	curl -o $${files[$$i]} -z $${files[$$i]} $${urls[$$i]}; \
	done

clean:
	rm -f communes.* circos.* $(RAW_FILES) $(DATA_FILES) $(SVG_FILES) $(PNG_FILES)
