import requests
from bs4 import BeautifulSoup
import urllib3
import re
import pandas as pd
import numpy as np

word = "/wiki/Intelligence_artificielle"
base = "http://fr.wikipedia.org"

def get_page(base=base, word=word):
    response = requests.get(base + word)
    return BeautifulSoup(response.content, "html.parser")

def get_links(page):
    LinksList = []
    for link in page.findAll('a'):
        linkfound = link.get('href')
        name_link=link.get('title')
        LinksList.append((linkfound, name_link))
        # print(linkfound, name_link)
    print("Number of links found:",len(LinksList))
    return LinksList

# To remove :
# If 'Portail' in the link
# If plus de 3 fois '/' 
# If 'Cat' in the link 
# If 'Wikip' in the link
# If '501c' in the link
# If title is None
# If '(page inexistante)' in the title
# If 'Modifier la section' in the title
# If 'Correction des liens externes' in the title
# If 'Référence' in the title
# If 'Aide:' in the title
# if 'Modifier cette page [v] 1' in the title
# if 'Vous pouvez modifier cette page ! [e] 1' in the title
# if 'Historique des versions de cette page [h] 1' in the title


def remove_bad_links(links_list):
    to_remove = ['Nous vous encourageons à créer un compte utilisateur et vous connecter\u202f; ce n’est cependant pas obligatoire.',
                 'International Standard Serial Number', 
                 'Agrandir', 'International Standard Book Number', 
                 'Nous vous encourageons à vous connecter\u202f; ce n’est cependant pas obligatoire. [o]', 
                 'La page de discussion pour les contributions depuis cette adresse IP [n]', 
                 'Une liste des modifications effectuées depuis cette adresse IP [y]', 
                 'Affiche un article au hasard [x]',
                 'Accès à l’aide',
                 'Liste des modifications récentes sur le wiki [r]',
                 'Importer des fichiers [u]',
                 'Liste de toutes les pages spéciales [q]',
                 'Adresse permanente de cette version de la page',
                 'Plus d’informations sur cette page',
                 'Informations sur la manière de citer cette page',
                 'Version imprimable de cette page [p]', 
                 'Voir le contenu de la page [c]',
                 'Discussion au sujet de cette page de contenu [t]',
                 ]
    clean_list = []
    for elt in links_list:
        if elt[0] is not None and elt[1] is not None:
            if ('Portail' not in elt[0]) and ('Cat' not in elt[0]) and ('Wikip' not in elt[0]) and ('501c' not in elt[0]) and ('Modifier cette page' not in elt[1]) and ('Vous pouvez modifier cette page' not in elt[1]) and ('Historique des versions de cette page' not in elt[1]) and ('page inexistante)' not in elt[1]) and ('Modifier la section' not in elt[1]) and ('Correction des liens externes' not in elt[1]) and ('Aide:' not in elt[1]) and ('Référence' not in elt[1]):
                if elt[0].count('/') < 3:
                    if elt[1] is not None:
                        if elt[1] not in to_remove:
                            clean_list.append(elt)
    print("Number of clean links:", len(clean_list))
    # print(clean_list)
    return clean_list

def count_titles(links_list):
    count_dict = {}
    titles_list = [title for _, title in links_list]

    for title in titles_list:
        if title not in count_dict.keys():
            count_dict[title] = 1
        else:
            count_dict[title] += 1
    # sort by value

    final_dict = {k : v for k, v in sorted(count_dict.items(), key=lambda item: item[1])}

    return final_dict


def scrap_all_pages(base_web = base, base_word_enc = word, base_word = "Artificial Intelligence"):
    tab = np.ndarray(shape=(500000, 2), dtype=object)
    tab[0,0] = 'title'
    tab[0,1] = 'link'
    row = 1
    page = get_page(base=base_web, word=base_word_enc)
    links_list = get_links(page)
    clean_list = remove_bad_links(links_list)
    # assert 'Nous vous encourageons à créer un compte utilisateur et vous connecter\u202f; ce n’est cependant pas obligatoire.' in clean_list
    #print(clean_list)
    title_list = [title for _, title in clean_list]

    for link in title_list:
        tab[row, 0] = base_word
        tab[row, 1] = link
        row+=1
        #print(link)
        
    # for each link
    for link, title in clean_list:
        page = get_page(base = base_web, word = link)
        links_list = get_links(page)
        list_clean = remove_bad_links(links_list)
        title_list = [title for _, title in clean_list]
        # add each link and his links in the list :
        
scrap_all_pages()
