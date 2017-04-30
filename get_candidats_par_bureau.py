#!/usr/bin/env python
# coding: utf8

from __future__ import unicode_literals

import pandas as pd
import json
from json import encoder
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

encoder.FLOAT_REPR = lambda o: format(o, '.2f')

def calculer_totaux(df):
    stats_index = ['departement', 'circo', 'tour']
    choix_index = stats_index + ['commune_code', 'bureau'] + ['choix']

    # on vérifie que le nombre d'inscrits, votants et exprimes est le même à chaque ligne d'un même bureau
    verif_unique = df.groupby(stats_index + ['commune_code', 'bureau']).agg({
        'inscrits': 'nunique',
        'votants': 'nunique',
        'exprimes': 'nunique',
    })
    assert (verif_unique == 1).all().all()
   
    stats = (
        df
            # on a vérifié que les stats étaient les mêmes pour chaque bureau, donc on déduplique en prenant
            # la première valeur
            .groupby(stats_index + ['commune_code', 'bureau']).agg({
            'inscrits': 'first',
            'votants': 'first',
            'exprimes': 'first',
        })
            # puis on dépile le numéro de tour et on le met en premier index de colonne
            .unstack(['tour']).swaplevel(0, 1, axis=1).sortlevel(axis=1)
            # enfin, on remplace les valeurs manquantes avec des 0 (pour les élections sans second tour)
            .fillna(0, downcast='infer')
    )
    
    stats.columns = stats.columns.set_names(['tour', 'statistique'])

    # le fillna est utilisé pour les législatives : toutes les nuances ne sont pas présentes dans toutes
    # les circos, donc il faut remplacer les valeurs manquantes par des 0, et recaster en int
    choix = df.groupby(choix_index)['voix'].sum().unstack(['tour', 'choix']).fillna(0, downcast='infer').sortlevel(axis=1)

    # on vérifie que le nombre de suffrages exprimés est égal à la somme des votes pour chaque choix, et ce pour chaque
    # tour de l'élection
    assert (
       stats.swaplevel(0, 1, axis=1)['exprimes'] == choix.sum(axis=1, level=0)
    ).all().all()

    return stats, choix


def calculer_scores(stats, choix, tour):
    scores = 100 * choix[tour].divide(stats[tour]['exprimes'], axis=0)
    scores['ABSTENTION'] = 100-100 * stats[tour]['exprimes'] / stats[tour]['inscrits']
    return scores

use_columns = [
    'tour', 'departement', 'circo', 'commune_code', 'bureau',
    'inscrits', 'votants', 'exprimes',
    'choix', 'voix'
]

print("donnees presidentielles 2012")
df_pres_2012 = pd.read_csv(
    'data/pres_2012.csv',
    sep=';',
    encoding='cp1252',
    names=['tour', 'departement', 'commune_code', 'commune_nom', 'circo', 'canton', 'bureau', 'inscrits', 'votants', 'exprimes',
           'numero_candidat', 'nom_candidat', 'prenom_candidat', 'choix', 'voix'],
    dtype={'departement': str, 'commune_code': str, 'bureau': str},
    usecols=use_columns
)

print("donnees legislatives 2012")
df_legi_2012 = pd.read_csv(
    'data/legi_2012.csv',
    sep=';',
    skiprows=18,
    names=['tour', 'departement', 'commune_code', 'commune_nom', 'circo', 'canton', 'bureau', 'inscrits', 'votants', 'exprimes',
           'numero_candidat', 'nom_candidat', 'prenom_candidat', 'choix', 'voix'],
    dtype={'departement': str, 'choix': str, 'commune_code': str, 'bureau': str},
    usecols=use_columns
)

print("donnees presidentielles 2017")
df_pres_2017 = pd.read_csv(
    'data/pres_2017.csv',
    sep=';',
    encoding='cp1252',
    names=['tour', 'departement', 'lib_dpt', 'circo', 'lib_circo', 'commune_code', 'lib_commune', 'bureau', 'inscrits', 'abstentions', 'abs_ins',
           'votants', 'vot_ins', 'blancs', 'bla_ins', 'bla_vot',
           'nuls', 'nul_ins', 'nul_vot', 'exprimes', 'exp_ins', 'exp_vot', 'sexe', 'choix', 'prenom', 'voix', 'dummy1', 'dummy2', 'panneau'],
    dtype={'departement': str, 'commune_code': str, 'bureau': str},
    usecols=use_columns
)

stats_2012, choix_2012 = calculer_totaux(df_pres_2012)
stats_legi_2012, choix_legi_2012 = calculer_totaux(df_legi_2012)
stats_2017, choix_2017 = calculer_totaux(df_pres_2017)

print("statistiques presidentielles 2012")
scores_pres_2012 = calculer_scores(stats_2012, choix_2012, 1)

print("statistiques legislatives 2012")
scores_legi1_2012 = calculer_scores(stats_legi_2012, choix_legi_2012, 1)

scores_legi2_2012 = calculer_scores(stats_legi_2012, choix_legi_2012, 2)

print("statistiques presidentielles 2017")
scores_pres_2017 = calculer_scores(stats_2017, choix_2017, 1)

print("fusion des resultats")
df_circonscriptions = pd.concat([
    scores_pres_2012.rename(columns=lambda c: c + '\nPRES\n2012'),
    scores_legi1_2012.rename(columns=lambda c: c + '\nLEGI1\n2012'),
    scores_legi2_2012.rename(columns=lambda c: c + '\nLEGI2\n2012'),
    scores_pres_2017.rename(columns=lambda c: c + '\nPRES\n2017')
], axis=1)

pd.options.display.float_format = '{:.2f}'.format

number_of_pdfs = 0
output_file_base="output/rapport_candidats_par_bureau"
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("candidats_report.html")
groups = df_circonscriptions.groupby(level=['departement', 'circo'])
for group_key, group_content in groups:
    number_of_pdfs += 1
    print("generation du rapport pdf "+str(number_of_pdfs)) 
    template_vars = {"title" : "Candidats par bureau",
                 "candidats_table": group_content.to_html()}
    html_out = template.render(template_vars)
    pdf_output_file_name=output_file_base+('-'.join(map(str,group_key)))+".pdf"
    HTML(string=html_out).write_pdf(pdf_output_file_name)
    print("Le rapport pdf a ete cree dans "+pdf_output_file_name)
    csv_output_file_name=output_file_base+('-'.join(map(str,group_key)))+"csv"
    group_content.to_csv(csv_output_file_name, sep=';')
    print("La version csv a ete cree dans "+csv_output_file_name)
