# Site Mika — mode d'emploi

Interface web pour lire tes vidéos `.mp4` hébergées sur ton NAS Synology, sans PHP.

## 1. Installation sur le NAS

1. Ouvre **File Station** → va dans `/web/site_mika` (c'est déjà fait vu ta capture d'écran).
2. Copie ces 3 fichiers dedans :
   - `index.html`
   - `generate_manifest.py`
   - `manifest.json`
3. Dans ce même dossier, organise tes vidéos comme tu veux :

```
web/site_mika/
├── index.html
├── generate_manifest.py
├── manifest.json
├── Films/
│   ├── inception.mp4
│   └── le_voyage_de_chihiro.mp4
├── Series/
│   └── episode_01.mp4
└── ma_video_du_weekend.mp4      <- pas dans un sous-dossier -> catégorie "Vidéos"
```

Chaque **sous-dossier devient une catégorie** dans l'interface. Les fichiers
posés directement à la racine (pas dans un sous-dossier) sont regroupés dans
la catégorie "Vidéos". Tu peux tout mettre à plat aussi (pas de sous-dossiers
du tout) si tu préfères une liste simple : tout ira dans "Vidéos".

## 2. Activer Web Station (si pas déjà fait)

- **Panneau de configuration de DSM** → **Centre de paquets** → installe **Web Station**.
- Dans Web Station, crée un "portail web" qui pointe vers `/web/site_mika`
  (ou utilise le dossier `web` partagé par défaut, qui sert déjà ce que tu
  vois dans ton URL `.../site_mika`).
- Aucune configuration PHP n'est nécessaire, ce site est 100% statique (HTML + JS).

## 3. Générer la liste des vidéos (manifest.json)

Le site ne "voit" pas automatiquement les fichiers ajoutés : il lit un fichier
`manifest.json` qu'il faut régénérer après chaque ajout. Deux façons de le faire :

### Option A — depuis un ordinateur (le plus simple pour démarrer)
Si Python 3 est installé sur ton PC/Mac, copie le dossier `site_mika` en local,
puis dans un terminal :

```bash
cd chemin/vers/site_mika
python3 generate_manifest.py
```

Cela crée/actualise `manifest.json`. Recopie ensuite ce fichier sur le NAS.

### Option B — directement sur le NAS (automatique, recommandé)
1. Installe le paquet **Python 3** via le Centre de paquets DSM.
2. Va dans **Panneau de configuration → Planificateur de tâches → Créer →
   Tâche déclenchée → Script défini par l'utilisateur**.
3. Programme-la (ex. toutes les 30 minutes) avec la commande :
   ```bash
   python3 /volume1/web/site_mika/generate_manifest.py
   ```
   (adapte le chemin exact à ton NAS — regarde le chemin réel dans File Station,
   généralement `/volume1/web/...`).
4. À partir de là, dès que tu ajoutes une vidéo, elle apparaît automatiquement
   sur le site dans les 30 minutes (ou clique sur "↻ Recharger" dans le site
   après avoir lancé la tâche manuellement pour un effet immédiat).

### Vignettes et durée des vidéos (optionnel)
Si **ffmpeg** est installé sur la machine qui exécute le script (paquet
disponible sur certains NAS, ou installable en local), lance :
```bash
python3 generate_manifest.py --with-thumbnails
```
Cela génère une vignette par vidéo et détecte sa durée. Sans ffmpeg, le site
affiche simplement les initiales du titre à la place de la vignette — ça
reste très propre visuellement.

## 4. Accéder au site

Ouvre dans un navigateur :
```
http://192.168.1.2:5001/site_mika/index.html
```
(ou l'adresse que Web Station t'indique — souvent sans le port `:5001`, qui
est celui de DSM lui-même, pas celui du site).

## Notes

- Formats vidéo lus nativement par les navigateurs : **.mp4** (H.264) fonctionne
  partout. `.mov`/`.mkv` peuvent ne pas se lire selon le codec interne — si un
  fichier ne se lance pas dans la fenêtre de lecture, reconvertis-le en mp4.
- Le titre affiché est déduit automatiquement du nom de fichier
  (`mon_super-film.mp4` → "Mon super film"). Renomme tes fichiers proprement
  si tu veux des titres plus jolis.
- Tout est statique : aucune base de données, aucune donnée envoyée ailleurs
  que sur ton NAS.
