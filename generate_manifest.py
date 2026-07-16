#!/usr/bin/env python3
"""
generate_manifest.py
---------------------
Scanne le dossier courant (ou celui passé en argument) et génère un fichier
manifest.json utilisé par index.html pour afficher la liste des vidéos.

Organisation attendue :
  site_mika/
    index.html
    generate_manifest.py
    manifest.json        <- généré par ce script
    Films/
      mon_film.mp4
    Series/
      episode1.mp4
    ma_video_racine.mp4   <- regroupée dans la catégorie "Vidéos"

Utilisation :
  python3 generate_manifest.py
  python3 generate_manifest.py --with-thumbnails   (nécessite ffmpeg installé)
  python3 generate_manifest.py /chemin/vers/site_mika

Pour une mise à jour automatique sans PHP : programme ce script dans le
Planificateur de tâches du NAS (DSM > Panneau de configuration > Planificateur
de tâches > Créer > Tâche déclenchée > Script défini par l'utilisateur), par
exemple toutes les 30 minutes.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".ogg", ".mov", ".m4v"}
THUMBNAIL_DIRNAME = ".thumbnails"
DEFAULT_CATEGORY = "Vidéos"


def humanize_title(filename: str) -> str:
    """Transforme 'mon_super-Film_2019.mp4' en 'Mon super Film 2019'."""
    stem = Path(filename).stem
    stem = stem.replace("_", " ").replace("-", " ")
    stem = " ".join(stem.split())
    return stem[:1].upper() + stem[1:] if stem else stem


def has_ffmpeg() -> bool:
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, check=True)
        except (OSError, subprocess.CalledProcessError):
            return False
    return True


def get_duration(path: Path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True, text=True
        )
        return round(float(out.stdout.strip()))
    except Exception:
        return None


def make_thumbnail(path: Path, thumb_path: Path):
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", "00:00:03", "-i", str(path),
             "-frames:v", "1", "-q:v", "4", "-vf", "scale=480:-1", str(thumb_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return thumb_path.exists()
    except Exception:
        return False


def scan(root: Path, with_thumbnails: bool):
    ffmpeg_ok = with_thumbnails and has_ffmpeg()
    if with_thumbnails and not ffmpeg_ok:
        print("⚠️  ffmpeg/ffprobe introuvable : les vignettes et durées seront ignorées.")

    categories = {}

    def add_video(file_path: Path, category: str):
        rel_file = file_path.relative_to(root).as_posix()
        duration = get_duration(file_path) if ffmpeg_ok else None

        thumbnail_rel = None
        if ffmpeg_ok:
            thumb_name = file_path.stem + ".jpg"
            thumb_path = root / THUMBNAIL_DIRNAME / category / thumb_name
            if make_thumbnail(file_path, thumb_path):
                thumbnail_rel = thumb_path.relative_to(root).as_posix()

        categories.setdefault(category, []).append({
            "title": humanize_title(file_path.name),
            "file": rel_file,
            "thumbnail": thumbnail_rel,
            "duration": duration,
        })

    # Fichiers directement à la racine
    for entry in sorted(root.iterdir()):
        if entry.is_file() and entry.suffix.lower() in VIDEO_EXTENSIONS:
            add_video(entry, DEFAULT_CATEGORY)

    # Sous-dossiers = catégories (on ignore les dossiers cachés / techniques)
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and not entry.name.startswith(".") and entry.name != THUMBNAIL_DIRNAME:
            for file_path in sorted(entry.rglob("*")):
                if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                    add_video(file_path, entry.name)

    result = {
        "categories": [
            {"name": name, "videos": videos}
            for name, videos in categories.items()
        ]
    }
    return result


def main():
    args = sys.argv[1:]
    with_thumbnails = "--with-thumbnails" in args
    args = [a for a in args if a != "--with-thumbnails"]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent

    if not root.is_dir():
        print(f"Dossier introuvable : {root}")
        sys.exit(1)

    manifest = scan(root, with_thumbnails)
    out_path = root / "manifest.json"
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    total = sum(len(c["videos"]) for c in manifest["categories"])
    print(f"✅ manifest.json généré : {total} vidéo(s) dans {len(manifest['categories'])} catégorie(s).")
    print(f"   → {out_path}")


if __name__ == "__main__":
    main()
