# B-SY INSTITUTE

Site vitrine statique : ouvrir `index.html` ou servir ce dossier avec un serveur HTTP.

## Organisation

- `index.html`, `services.html`, `galery.html`, `about.html` : pages publiques.
- `assets/css/main.css` et `assets/sass/` : base Editorial de HTML5 UP conservée.
- `assets/css/institute.css` : personnalisation commune, responsive et accessibilité.
- `assets/js/site.js` : agrandissement des photos avec un dialogue natif. Les liens photo fonctionnent également sans JavaScript.
- `images/` : visuels existants. Les anciens scripts du template restent disponibles mais ne sont plus chargés par les pages publiques.

Les menus et coordonnées restent en HTML pour fonctionner sans JavaScript. Toute modification des coordonnées doit être reportée dans les quatre pages, y compris les liens WhatsApp et téléphone. Aucun traitement serveur ou formulaire de collecte n'est installé.

## Vérifications

Avec Python, Playwright et Chromium déjà installés :

```sh
python tests/check_site.py
node --check assets/js/site.js
```

Le contrôle couvre les liens locaux, les ancres, les images, les largeurs 360/768/1440 px, le clavier et l'ouverture répétée des photos. Les captures de l'accueil sont enregistrées dans le dossier temporaire du système. Les contacts externes ne sont pas sollicités par les tests.

## À confirmer avant publication

- Numéro actuel de l'institut : les chiffres historiques ont été conservés ; vérifier le téléphone et WhatsApp avec le responsable.
- Adresse, horaires, tarifs et durées. Aucun tarif ni avis client n'a été inventé.
- La carte lance une recherche du quartier, pas un point GPS vérifié de l'institut.
- Relire les descriptions de prestations avec l'équipe.
- Une fois le domaine public connu, ajouter les URL canoniques, le sitemap et les métadonnées de partage complètes.

Base graphique : [Editorial / HTML5 UP](https://html5up.net), attribution conservée dans le pied de page et les sources.
