# Automatisation Nexus Mods (via GitHub Actions)

Publier une release GitHub qui contient `WTTG3-FR-Traduction-Nexus.zip` peut aussi
pousser automatiquement une **nouvelle version de fichier** sur Nexus Mods.

Action utilisee : [Nexus-Mods/upload-action](https://github.com/Nexus-Mods/upload-action)
(workflow : `.github/workflows/nexus-upload.yml`).

## Prerequisites (une fois)

1. Page mod Nexus creee + **premier zip deja uploade** (meme en quarantaine).
2. Cle API Nexus : [Settings → API keys](https://www.nexusmods.com/settings/api-keys)
3. **File ID** : onglet Files de ta page → menu **API Info** (ou Manage Files → API Info).

## Configurer le repo GitHub

Sur https://github.com/Mbappinho/WTTG3-FR-Traduction :

| Ou | Nom | Valeur |
|----|-----|--------|
| **Settings → Secrets and variables → Actions → Secrets** | `NEXUSMODS_API_KEY` | ta cle API Nexus |
| **Settings → Secrets and variables → Actions → Variables** | `NEXUSMODS_FILE_ID` | l’ID numerique du fichier Nexus |

## Utilisation

### Automatique

1. Build le pack Nexus :
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\build_beginner_pack.ps1 -Distribution Nexus
   Compress-Archive -Path release\WTTG3-FR-Beginner-Nexus\* -DestinationPath release\WTTG3-FR-Traduction-Nexus.zip -Force
   ```
2. Cree / mets a jour une GitHub Release (`vX.Y.Z`) avec l’asset
   `WTTG3-FR-Traduction-Nexus.zip` (et le zip Full si tu veux).
3. Le workflow **Upload to Nexus Mods** demarre sur `release: published`
   et envoie le zip Nexus avec la version = tag sans le `v` (`v1.2.6` → `1.2.6`, `1.3` → `1.3`).
   Le job definit `GH_REPO` (pas de checkout) pour que `gh release download` fonctionne.

### Manuel

Actions → **Upload to Nexus Mods** → Run workflow  
- `tag` : ex. `v1.2.5` (vide = derniere release)  
- `dry_run` : coche pour tester le telechargement sans uploader

## Limites

- Ne cree **pas** la page mod ; met a jour un **fichier existant**.
- Ne reecrit pas toute la description longue de la page (seulement la note de version fichier).
- Si le fichier est encore en quarantaine, l’upload d’une nouvelle version peut echouer
  jusqu’a validation par un modo Nexus.
- L’action est encore en beta : le workflow pin `v1.0.0-beta.9`.

## Depannage

| Symptome | Piste |
|----------|--------|
| `Missing ... NEXUSMODS_API_KEY` | Secret Actions non cree / mauvais repo |
| `Missing ... NEXUSMODS_FILE_ID` | Variable Actions manquante |
| Echec API Nexus | File ID incorrect, ou fichier encore bloque en quarantaine |
| Asset introuvable | La release GitHub n’inclut pas `WTTG3-FR-Traduction-Nexus.zip` |
