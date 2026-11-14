# Teddy Coste — site des performances

Chaque performance est montrée à travers ses tirages Instax Wide scannés, présentés en éventail.
Les tirages se « développent » à l'écran comme un vrai Instax.

## Ce qu'il y a dans le dossier

| Élément | Rôle |
| --- | --- |
| `index.html` | Le site entier : mise en page, animations et liste des performances |
| `prints/` | Les tirages Instax en JPEG légers, utilisés par le site |
| `views/` | Les vues d'exposition en JPEG légers |
| `instant/` | Les Instax de la page Instant Photographs |
| `cv/` | Le portrait du CV |
| `images/` | Les scans originaux en TIFF. **Ne part pas sur GitHub** (trop lourd), reste sur l'ordinateur |
| `outil/preparer-scans.py` | Transforme les TIFF de `images/` en JPEG pour `prints/` |
| `.gitignore` | Dit à GitHub d'ignorer les TIFF et les fichiers de travail |

## Modifier un texte ou une performance

Tout se passe dans `index.html`, dans le bloc `const P=[ ... ]` (cherchez « the archive »).
Une ligne par performance, la plus récente en haut :

```js
{slug:'the-junction', title:'The Junction', year:2022,
 credit:'Performance · Lunchtime Gallery',
 prints:'TJ:L TJ1:L TJ2:L',
 desc:''},
```

- `slug` : le nom dans l'adresse (…/#the-junction). Minuscules et tirets, sans accents.
- `credit` : le type, puis les lieux, séparés par ` · `.
- `prints` : les noms des scans dans `prints/`, dans l'ordre, chacun suivi de son orientation :
  `L` = paysage, `P` = portrait avec la bande épaisse à droite, `Q` = portrait avec la bande à gauche.
- `desc` : le texte de la performance. Pour plusieurs paragraphes, séparez-les par `\n\n`.

## Les pages

Le menu du haut mène à quatre pages, toutes dans `index.html` :
- **Selected Performances** (la page d'accueil) : la liste, puis une page par performance.
- **Instant Photographs** : un éventail d'Instax comme pour les performances. Les tirages sont dans `instant/`,
  la liste est dans `const IP=` (cherchez « Instant Photographs ») : même format `nom:P`/`nom:Q`/`nom:L`.
  Pour en ajouter : mettez le scan dans `images/instax/`, puis
  `python3 outil/preparer-scans.py --de images/instax --vers instant NOM` et ajoutez la ligne affichée.
- **Exhibition Views** : une archive simple, sans effet Instax. Les images sont dans `views/`,
  la liste est dans le bloc `const EV=[ ... ]` (cherchez « exhibition views ») : une ligne par image,
  `['nom-du-fichier', 'légende']`. Les images qui se suivent avec la même légende sont regroupées sur une rangée.
  Pour ajouter une image : mettez l'original dans `images/EV/`, réduisez-la à 2000 px de large
  (Aperçu → Outils → Ajuster la taille), enregistrez-la dans `views/`, puis ajoutez sa ligne.
- **CV** : cherchez `id="page-cv"`. Le portrait est `cv/BIO.jpg` : il se développe à l'ouverture de la page, et à nouveau quand on clique dessus. Une ligne `<div class="yr">` par année, un `<p>` par entrée, les titres entre `<em>` et `</em>`.

L'adresse e-mail reste en bas de toutes les pages.

## Ajouter de nouveaux scans

1. Mettez les TIFF dans `images/` (par ex. `TJ3.tif`).
2. Dans le Terminal, depuis ce dossier : `python3 outil/preparer-scans.py TJ3`
   Le script redresse le tirage s'il a été scanné de travers, crée `prints/TJ3.jpg`
   et affiche son orientation (par ex. `TJ3:L`).
3. Ajoutez `TJ3:L` à la liste `prints` de la performance dans `index.html`.

## Mettre le site en ligne avec GitHub Pages

1. Créez un dépôt sur GitHub et envoyez-y ce dossier (avec GitHub Desktop, c'est un glisser-déposer).
2. Sur GitHub : **Settings → Pages → Branch : `main`, dossier `/ (root)`** → **Save**.
3. Après une minute, le site est en ligne à `https://<votre-nom>.github.io/<nom-du-dépôt>/`.
4. Pour utiliser `teddycoste.com`, indiquez le domaine dans **Settings → Pages → Custom domain**,
   puis faites pointer le domaine vers GitHub chez votre registrar (GitHub affiche les réglages DNS à saisir).
