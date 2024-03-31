import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def code_word(word):
    output = "".join([c if c != " " else "_" for c in word])
    return output


def get_page(base, word):
    response = requests.get(base + word)
    return BeautifulSoup(response.content, "html.parser")


def get_links(page):
    LinksList = []
    for link in page.findAll("a"):
        linkfound = link.get("href")
        name_link = link.get("title")
        LinksList.append((linkfound, name_link))
    return LinksList


def remove_bad_links(links_list, word, pbar=None):
    to_remove = [
        "Nous vous encourageons à créer un compte utilisateur et vous connecter\u202f; ce n’est cependant pas obligatoire.",
        "International Standard Serial Number",
        "Agrandir",
        "International Standard Book Number",
        "Nous vous encourageons à vous connecter\u202f; ce n’est cependant pas obligatoire. [o]",
        "La page de discussion pour les contributions depuis cette adresse IP [n]",
        "Une liste des modifications effectuées depuis cette adresse IP [y]",
        "Affiche un article au hasard [x]",
        "Accès à l’aide",
        "Liste des modifications récentes sur le wiki [r]",
        "Importer des fichiers [u]",
        "Liste de toutes les pages spéciales [q]",
        "Adresse permanente de cette version de la page",
        "Plus d’informations sur cette page",
        "Informations sur la manière de citer cette page",
        "Version imprimable de cette page [p]",
        "Voir le contenu de la page [c]",
        "Discussion au sujet de cette page de contenu [t]",
        "Modèle:Section à internationaliser",
        "Projet:Accueil",
        f"Discussion:{word}",
        "Si ce bandeau n'est plus pertinent, retirez-le. Cliquez ici pour en savoir plus sur les bandeaux.",
        f"{word} (homonymie)",
        "Consultez la documentation du modèle",
        "Rechercher sur Wikipédia [f]",
        "Cette page est protégée.\nVous pouvez toutefois en visualiser la source. [e]",
        "Si ce bandeau n'est plus pertinent, retirez-le. Cliquez ici pour en savoir plus.",
        "Adresse permanente de cette version de cette page",
        "Davantage d’informations sur cette page",
        "Modifier le wikicode [e]",
        "Modifier le wikicode de cette page [e]",
        "Téléverser des fichiers [u]",
        "Modifier le code source de la section : Notes et références",
        "Modifier le code source de la section : Articles connexes",
        "Modifier le code source de la section : Voir aussi",
        "Modifier le code source de la section : Liens externes",
        "Modifier le code source de la section : Bibliographie",
        "Modifier le code source de la section : Économie"
        "Modifier le code source de la section : Géographie",
        "A list of edits made from this IP address [y]",
        "Visit the main page [z]",
        "A list of recent changes to Wikipedia [r]",
        "Discussion about edits from this IP address [n]",
        "Learn how to edit Wikipedia",
        "Guidance on how to use and edit Wikipedia",
        "Visit the main page",
        "You're encouraged to log in; however, it's not mandatory. [o]",
        "Visit a randomly selected article [x]",
        "A list of all special pages [q]",
        "You are encouraged to create an account and log in; however, it is not mandatory",
        "Articles related to current events",
        "More information about this page",
        "Past revisions of this page [h]",
        "Discuss improvements to the content page [t]",
        "View the content page [c]",
        "Printable version of this page [p]",
        "Permanent link to this revision of this page",
        "Download this page as a PDF file",
        "Information on how to cite this page",
        "Edit this page [e]",
        "Edit section: References",
        "Help:Authority control",
        "Enlarge",
        "Edit section: External link",
        "ISBN (identifier)",
        "Edit section: See also",
        "Edit section: History",
        "Doi (identifier)",
        "VIAF (identifier)",
        "Help:Maintenance template removal",
        "S2CID (identifier)",
        "Template:Cite web",
        "ISSN (identifier)",
        "ISNI (identifier)",
        "Help:Referencing for beginners",
        "Help:Edit summary",
        "PMID (identifier)",
        "Edit section: Further reading",
        "Bibcode (identifier)",
        "SUDOC (identifier)",
        "Edit this page",
        "Help:CS1 errors",
        "Template:Cite journal",
        "MBAREA (identifier)",
        "Edit section: External links",
        "Portal",
        "OCLC (identifier)",
        "PMC (identifier)",
        "Edit section: Notes",
        "Hdl (identifier)",
        "JSTOR (identifier)",
        "About this sound",
        "Edit section: Geography",
        "This page is protected.\nYou can view its source [e]",
        "Edit section: Education",
        "Wayback Machine",
        "Geographic coordinate system",
        "Search Wikipedia [f]",
        "Search Wikipedia",
        "Search in custom namespaces",
        "Search for files",
        "Search in (Article)",
        "Search all of content (including talk pages)",
    ]
    years = [str(i) for i in range(2022)] + [f"{i}s" for i in range(2022)]
    clean_list = []
    for elt in links_list:
        if elt[0] is not None and elt[1] is not None:
            if (
                ("Portail" not in elt[0])
                and ("Cat" not in elt[0])
                and ("Wikip" not in elt[0])
                and ("501c" not in elt[0])
                and ("Modifier cette page" not in elt[1])
                and ("Vous pouvez modifier cette page" not in elt[1])
                and ("Historique des versions de cette page" not in elt[1])
                and ("page inexistante)" not in elt[1])
                and ("Modifier la section" not in elt[1])
                and ("Correction des liens externes" not in elt[1])
                and ("Aide:" not in elt[1])
                and ("Référence" not in elt[1])
            ):
                if elt[0].count("/") < 3:
                    if elt[1] is not None:
                        if elt[1] not in to_remove:
                            if (
                                "Edit section" not in elt[1]
                                and "(page does not exist)" not in elt[1]
                                and "Template" not in elt[1]
                                and "List of" not in elt[1]
                                and "History of" not in elt[1]
                                and "Modifier le code" not in elt[1]
                                and "Modifier le wikicode" not in elt[1]
                            ):
                                if elt[1] not in years:
                                    clean_list.append(elt)
    if pbar is not None:
        pbar.set_description(f"Number of clean links: {len(clean_list)}")
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

    final_dict = {k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1])}

    return final_dict


def remove_doubles(tup_list):
    dic = {}
    for link, title in tup_list:
        if title not in dic.values():
            dic[title] = link
    return list(zip(dic.values(), dic.keys()))


def scrap_all_pages(base_web, base_word_enc, base_word):
    tab = []
    page = get_page(base=base_web, word=base_word_enc)
    print(f"Scraping {base_word}...")
    links_list = get_links(page)
    clean_list = remove_bad_links(links_list, base_word)
    clean_list = remove_doubles(clean_list)
    title_list = [title for _, title in clean_list]

    for link in title_list:
        tab.append([base_word, link])

    # for each link
    pbar = tqdm(clean_list)
    for link, title in pbar:
        pbar.set_description(f"Scraping {title}...")
        page = get_page(base=base_web, word=link)
        links_list = get_links(page)
        list_clean = remove_bad_links(links_list, title, pbar)
        list_clean = remove_doubles(list_clean)
        title_list = [title for _, title in list_clean]
        assert len(list_clean) == len(title_list)
        # add each pair title, link in the list :
        for t in title_list:
            tab.append([title, t])

    return tab


def main(language, word):
    word_base = word
    base = f"http://{language}.wikipedia.org"

    word_base_encoded = code_word(word_base)

    word = "/wiki/" + word_base_encoded

    filepath = Path(f"Data/{word_base}/network_nodes_{word_base_encoded}.csv")
    filepath.parent.mkdir(parents=True, exist_ok=True)

    filepath = Path(f"Data/{word_base}/network_links_{word_base_encoded}.csv")
    filepath.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    network = scrap_all_pages(base_web=base, base_word_enc=word, base_word=word_base)
    print("\nAll pages scraped.")
    npnet = np.array(network)
    df_links = pd.DataFrame(npnet, columns=["Source", "Target"])
    print("Network created")
    a = df_links["Target"].value_counts().to_dict()

    list_code = list(zip(list(a.keys()), [i for i in tqdm(range(len(list(a.keys()))))]))
    dict_code = {k: v for k, v in tqdm(list_code)}

    print("Preprocessing links...")
    enc = {"Source": dict_code, "Target": dict_code}
    print("Encoding...")
    df_links = df_links.replace(enc)
    print("Links ready.")
    print("Preprocessing nodes...")
    lnet = [[k, v] for k, v in tqdm(a.items())]
    df_nodes = pd.DataFrame(lnet, columns=["Label", "Weight"])
    print("Nodes ready.")

    print("Creating nodes csv...")
    df_nodes.to_csv(
        f"Data/{word_base}/network_nodes_{word_base_encoded}.csv", index_label="Id"
    )
    print("Nodes csv created.")
    print("Creating links csv...")
    df_links.to_csv(
        f"Data/{word_base}/network_links_{word_base_encoded}.csv", index=False
    )
    print("Links csv created.")

    print("The data has been scraped.")
    print("Number of lines in link file:", df_links.shape[0])
    print("Number of lines in node file:", df_nodes.shape[0])

    print("Execution time:", time.time() - start)


if __name__ == "__main__":
    main(language=input("Language [en, fr] : "), word=input("Concept : "))
