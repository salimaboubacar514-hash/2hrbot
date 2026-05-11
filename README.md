# Highrise Room Bot

Bot Python pour salle Highrise — emotes, téléportation, tenues aléatoires, animations, et plus.

## Fonctionnalités

- **82 emotes** (52 gratuits + 30 payants) en boucle individuelle
- **14 animations** (séquences d'emotes enchaînées)
- **20 messages de bienvenue** aléatoires avec emojis
- **Click-téléportation** à toutes les hauteurs (`tpon` / `tpoff`)
- **Portails automatiques** entre étages (F1→F4)
- **Navigation par étage** (`f1`, `f2`, `f3`, `f4`)
- **Spots** de téléportation nommés (`aller centre`, `aller vip`…)
- **Tenue aléatoire** du bot toutes les 5 minutes (commande `outfit`)
- Redémarrage automatique en cas de crash

---

## Déploiement sur Render (24h/24 gratuit)

### Étape 1 — GitHub

1. Crée un compte sur [github.com](https://github.com)
2. Clique **"New repository"** → nomme-le `highrise-bot` → **Public** → **Create**
3. Sur la page du repo, clique **"uploading an existing file"**
4. Glisse-dépose ces fichiers **uniquement** :
   - `bot.py`
   - `run.sh`
   - `requirements.txt`
   - `render.yaml`
   - `runtime.txt`
   - `Procfile`
   - `README.md`
5. Clique **"Commit changes"**

### Étape 2 — Render

1. Crée un compte sur [render.com](https://render.com) (gratuit)
2. Clique **"New +"** → **"Background Worker"**
3. Connecte ton compte GitHub → sélectionne le repo `highrise-bot`
4. Render détecte automatiquement `render.yaml`
5. Dans **"Environment Variables"**, ajoute :
   - `HIGHRISE_TOKEN` = ton token de bot Highrise
   - `HIGHRISE_ROOM_ID` = l'ID de ta salle
6. Clique **"Create Worker"**

Le bot tourne en continu, redémarre automatiquement si il plante.

---

## Variables d'environnement

| Variable | Description |
|---|---|
| `HIGHRISE_TOKEN` | Token API du bot (créé sur create.highrise.game) |
| `HIGHRISE_ROOM_ID` | ID de ta salle Highrise |

---

## Commandes (sans préfixe !)

| Commande | Action |
|---|---|
| `aide` | Liste toutes les commandes |
| `emotes1` … `emotes17` | Liste des emotes par page |
| `1` … `82` | Lancer un emote en boucle |
| `stop` / `stopanim` | Arrêter l'emote actuel |
| `stopall` | Arrêter tous les emotes |
| `party` `vibe` `chill` `rage` `flex` … | Animations enchaînées |
| `f1` `f2` `f3` `f4` | Aller à un étage |
| `aller <spot>` | Téléport vers un spot nommé |
| `spots` | Voir tous les spots |
| `tpon` / `tpoff` | Activer/désactiver click-téléport |
| `tp x y z` | Téléport libre (ex: `tp 15 6 21`) |
| `outfit` | Forcer un changement de tenue du bot |

---

## Obtenir les credentials Highrise

1. Va sur [create.highrise.game](https://create.highrise.game)
2. Connecte-toi → **Dashboard** → **Bots & API Keys**
3. Crée un bot → copie le **Token**
4. L'**Room ID** se trouve dans l'URL de ta salle : `highrise.game/rooms/ROOM_ID_ICI`

---

## Structure du projet

```
bot.py          — Bot principal
run.sh          — Boucle de redémarrage automatique
requirements.txt — Dépendances Python
render.yaml     — Config Render Background Worker
runtime.txt     — Version Python pour Render
Procfile        — Alternative Railway/Heroku
```
