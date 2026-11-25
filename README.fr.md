# RotoPDF

[English](README.md) | **Français**

Transforme une vidéo en planches d'images numérotées au format PDF.

- Choix du nombre d'images par seconde (fps) extraites
- Choix du nombre d'images par page (mise en page automatique, portrait ou paysage)
- Numéro de chaque image, avec le temps de la vidéo en option
- Interface sombre simple, installateur Windows fourni

## Installer

Télécharge `RotoPDF_Setup.exe` dans la section **Releases** et lance-le.

### Avertissement Windows à l'installation

Les versions ne sont pas encore signées numériquement : Windows SmartScreen peut afficher
« Windows a protégé votre ordinateur ». Clique sur **Informations complémentaires**, puis
**Exécuter quand même**. L'empreinte SHA-256 de chaque installateur est publiée avec la Release
(`RotoPDF_Setup.exe.sha256`) pour vérifier ton téléchargement.

## Lancer depuis le code source

```
pip install -r requirements.txt
python rotopdf.py
```

Ou double-clique sur `lancer.bat` (Windows).

## Construire l'installateur (Windows)

1. Installe Python 3.10 ou plus récent et [Inno Setup](https://jrsoftware.org/isdl.php) (gratuit, version 6 ou 7).
2. Double-clique sur `creer_installateur.bat`.
3. L'installateur est créé dans `Output\RotoPDF_Setup.exe`.

`creer_exe.bat` crée à la place un exe unique portable (`dist\RotoPDF.exe`).
Les Releases sont aussi construites automatiquement par GitHub Actions (`.github/workflows/build.yml`).

## Politique de signature du code (Code Signing Policy)

Une candidature au programme gratuit de signature de code de la fondation SignPath est prévue.
Si elle est acceptée, les versions Windows seront construites automatiquement par GitHub Actions
depuis ce dépôt public puis signées : « Free code signing provided by SignPath.io, certificate by
SignPath Foundation ».

- **Auteur, relecteur et approbateur :** Mattt6
- **Confidentialité :** ce programme fonctionne hors ligne et ne transmet aucune information
  à d'autres systèmes en réseau.

## Licence

Copyright (C) 2026 Mattt6

Publié sous licence GNU GPL v3 ou ultérieure, voir [LICENSE](LICENSE).
Les composants tiers sont listés dans [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt).
