import requests
from bs4 import BeautifulSoup
import urllib3
import re
import pandas as pd
import numpy as np
import time

word_base = 'Twitch'
base = "http://fr.wikipedia.org"

def code_word(word):
    output = "".join([c if c !=' ' else '_' for c in word])
    return output

word_base_encoded = code_word(word_base)

word = "/wiki/" + word_base_encoded

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


def remove_bad_links(links_list, word):
    to_remove = [
        'Nous vous encourageons à créer un compte utilisateur et vous connecter\u202f; ce n’est cependant pas obligatoire.',
        'International Standard Serial Number',
        'Agrandir', 'International Standard Book Number',
        'Nous vous encourageons à vous connecter\u202f; ce n’est cependant pas obligatoire. [o]',
        'La page de discussion pour les contributions depuis cette adresse IP [n]',
        'Une liste des modifications effectuées depuis cette adresse IP [y]', 
        'Affiche un article au hasard [x]', 
        'Accès à l’aide', 
        'Liste des modifications récentes sur le wiki [r]', 
        'Importer des fichiers [u]', 'Liste de toutes les pages spéciales [q]', 
        'Adresse permanente de cette version de la page', 
        'Plus d’informations sur cette page', 
        'Informations sur la manière de citer cette page', 
        'Version imprimable de cette page [p]', 
        'Voir le contenu de la page [c]', 
        'Discussion au sujet de cette page de contenu [t]',
        'Modèle:Section à internationaliser',
        'Projet:Accueil',
        f'Discussion:{word}',
        "Si ce bandeau n'est plus pertinent, retirez-le. Cliquez ici pour en savoir plus sur les bandeaux.",
        f"{word} (homonymie)",
        "Consultez la documentation du modèle"
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


def remove_doubles(tup_list):
    dic={}
    for link, title in tup_list:
        if title not in dic.values():
            dic[title] = link
    return list(zip(dic.values(),dic.keys()))


def scrap_all_pages(base_web = base, base_word_enc = word, base_word = word_base):
    tab = []
    page = get_page(base=base_web, word=base_word_enc)
    print(f"Scraping {base_word}...")
    links_list = get_links(page)
    clean_list = remove_bad_links(links_list, base_word)
    clean_list = remove_doubles(clean_list)
    title_list = [title for _, title in clean_list]

    for link in title_list:
        tab.append([base_word, link])
        #print(link)
    
    # for each link
    for link, title in clean_list:
        print(f"Scraping {title}...")
        page = get_page(base = base_web, word = link)
        links_list = get_links(page)
        list_clean = remove_bad_links(links_list, title)
        list_clean = remove_doubles(list_clean)
        title_list = [title for _, title in list_clean]
        assert len(list_clean) == len(title_list)
        # add each pair title, link in the list :
        for t in title_list:
            tab.append([title, t])
    
    return tab

def scrap_semi_pages(base_web = base, base_word_enc = word, base_word = word_base):
    tab = []
    page = get_page(base=base_web, word=base_word_enc)
    print(f"Scraping {base_word}...")
    links_list = get_links(page)
    clean_list = remove_bad_links(links_list)
    clean_list = remove_doubles(clean_list)
    # print(clean_list)
    title_list = [title for _, title in clean_list]

    for link in title_list:
        tab.append((base_word, link))
        #print(link)
    
    p=0

    # for each link
    for link, title in clean_list:
        if p%2==0:
            p+=1
            print(f"{title}...")
            page = get_page(base = base_web, word = link)
            links_list = get_links(page)
            list_clean = remove_bad_links(links_list)
            list_clean = remove_doubles(list_clean)
            title_list = [title for _, title in clean_list]
            # add each pair title, link in the list :
            for t in title_list:
                tab.append((title, t))
    
    return tab

if __name__ == '__main__':
    start = time.time()
    network = scrap_all_pages()
    npnet = np.array(network)
    df_links = pd.DataFrame(npnet, columns=['Source', 'Target'])

    a = df_links['Target'].value_counts().to_dict()

    list_code = list(zip(list(a.keys()),[i for i in range(len(list(a.keys())))]))
    dict_code = {k: v for k, v in list_code}

    enc = {"Source": dict_code, "Target": dict_code}
    df_links = df_links.replace(enc)

    lnet = [[k,v] for k,v in a.items()]
    df_nodes = pd.DataFrame(lnet, columns=['Label', 'Weight'])

    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words={'french'})
    X = vectorizer.fit_transform(a.keys())

    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    Sum_of_squared_distances = []
    K = range(2,10)
    for k in K:
        km = KMeans(n_clusters=k, max_iter=200, n_init=10)
        km = km.fit(X)
        Sum_of_squared_distances.append(km.inertia_)
    plt.plot(K, Sum_of_squared_distances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum_of_squared_distances')
    plt.title('Elbow Method For Optimal k')
    plt.show()

    input('Hit Enter one you have choosen a number of groups...')

    k = int(input('Number of groups choosen: '))

    true_k = k
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
    model.fit(X)
    labels=model.labels_
    clust_dic = {title: cluster for title, cluster in list(zip(a.keys(), labels))}

    df_nodes['Cluster'] = clust_dic.values()

    df_nodes.to_csv(f'Data/network_nodes_{word_base_encoded}.csv', index_label='Id')
    df_links.to_csv(f'Data/network_links_{word_base_encoded}.csv', index=False)

    print("The data has been scraped.")
    print("Number of lines in link file:", df_links.shape[0])
    print("Number of lines in node file:", df_nodes.shape[0])

    print("Execution time:", time.time()-start)