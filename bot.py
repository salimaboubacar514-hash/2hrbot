import asyncio
import os
import random
import logging
import time
from highrise import BaseBot, __main__
from highrise.models import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BOT_START_X    = 15.0
BOT_START_Y    = 0.0
BOT_START_Z    = 21.0
MAX_MSG        = 120
OUTFIT_DELAY   = 300   # secondes entre chaque changement de tenue automatique
TP_DEBOUNCE    = 1.8   # anti-boucle téléportation (secondes)

# ─── Messages de bienvenue aléatoires ────────────────────────────────────────
WELCOMES = [
    "🌟✨ Yo @{u} ! Bienvenue ici ! Tape aide pour les commandes 🎉🔥",
    "💫🎊 @{u} vient d'atterrir ! Content de te voir 🙌😎",
    "🔥🌈 Wsh @{u} ! Tu arrives au bon moment 😏💃",
    "⚡🎭 Ah @{u} est là ! La fête peut commencer 🎶🕺",
    "🌺💎 Bienvenue @{u} ! Installe-toi et profite 😊✨",
    "🎆🎇 @{u} debarque ! Toute la salle s'enflamme 🔥💥",
    "🦋🌙 Hey @{u} ! Bonne arrivee dans notre monde 🌍💫",
    "🎵🎤 @{u} entre dans la salle ! DJ lance la musique 🎧🔊",
    "💥🌠 @{u} ! On t'attendait ! Bienvenue champ 🏆✨",
    "🌸🎀 Coucou @{u} ! Super contente de te voir 💖🎊",
    "🚀⭐ @{u} a rejoint ! La legende est arrivee 🦁👑",
    "🎸🎺 @{u} est la ! C'est la fete totale 🥳🎉🔥",
    "🌊🏄 @{u} surfe dans la salle ! Welcome 🤙😜✨",
    "🦊💥 Oh ! @{u} vient de pop ! Bienvenue dans la zone 🎯🔥",
    "🍀🌟 @{u} a rejoint ! Que la chance soit avec toi 🎲💫",
    "🎪🎡 @{u} ! Le cirque peut commencer 🃏🎠✨",
    "👑💜 Royale entree de @{u} ! Bienvenue dans le palais 🏰🌟",
    "🌈☄️ @{u} vient de tomber du ciel ! Welcome 👼💫",
    "🔮🦄 @{u} ! Les etoiles ont guide tes pas ici ✨🌠",
    "🎭🔥 Attention ! @{u} est dans la place ! 👀💥",
]

# ─── EMOTES — IDs officiels confirmés ────────────────────────────────────────
# Format réel : dance-*, emoji-*, emote-*
# 🆓 = gratuit   💎 = payant (doit être possédé par l'utilisateur)
EMOTES: dict[str, tuple[str, str, bool]] = {
    # ── Danses gratuites ──────────────────────────────────────────────────────
    "1":  ("dance-tiktok3",      "TikTok 3",         True),
    "2":  ("dance-tiktok4",      "TikTok 4",         True),
    "3":  ("dance-tiktok5",      "TikTok 5",         True),
    "4":  ("dance-tiktok6",      "TikTok 6",         True),
    "5":  ("dance-tiktok7",      "TikTok 7",         True),
    "6":  ("dance-tiktok9",      "TikTok 9",         True),
    "7":  ("dance-tiktok10",     "TikTok 10",        True),
    "8":  ("dance-macarena",     "Macarena",         True),
    "9":  ("dance-russian",      "Russian Dance",    True),
    "10": ("dance-savage",       "Savage",           True),
    "11": ("dance-pennywise",    "Pennywise",        True),
    "12": ("dance-shoppingcart", "Shopping Cart",    True),
    "13": ("dance-worm",         "The Worm",         True),
    "14": ("dance-weird",        "Dance Weird",      True),
    "15": ("dance-creep",        "Creep",            True),
    "16": ("dance-penman",       "Penman",           True),
    "17": ("dance-mood",         "Mood Dance",       True),
    "18": ("dance-naenae",       "Nae Nae",          True),
    "19": ("dance-kick",         "Kick Dance",       True),
    "20": ("dance-floss",        "Floss",            True),
    "21": ("dance-grave",        "Grave Dance",      True),
    "22": ("dance-shuffle",      "Shuffle",          True),
    "23": ("dance-viral",        "Viral Groove",     True),
    # ── Emoji gratuits ────────────────────────────────────────────────────────
    "24": ("emoji-clap",         "Clap",             True),
    "25": ("emoji-thumbsup",     "Thumbs Up",        True),
    "26": ("emoji-angry",        "Angry",            True),
    "27": ("emoji-gagging",      "Tummy Ache",       True),
    "28": ("emoji-flex",         "Flex Emoji",       True),
    "29": ("emoji-cursing",      "Cursing",          True),
    # ── Actions gratuites ─────────────────────────────────────────────────────
    "30": ("emote-hello",        "Hello / Wave",     True),
    "31": ("emote-tired",        "Tired",            True),
    "32": ("emote-pose",         "Pose",             True),
    "33": ("emote-happy",        "Happy",            True),
    "34": ("emote-shy",          "Shy",              True),
    "35": ("emote-snowflake",    "Snowflake",        True),
    "36": ("emote-curtsy",       "Curtsy",           True),
    "37": ("emote-bow",          "Bow",              True),
    "38": ("emote-telekinesis",  "Telekinesis",      True),
    "39": ("emote-charging",     "Charging",         True),
    "40": ("emote-enthusiastic", "Enthusiastic",     True),
    "41": ("emote-float",        "Float",            True),
    "42": ("emote-cute",         "Cute",             True),
    "43": ("emote-no",           "No",               True),
    "44": ("emote-yes",          "Yes",              True),
    "45": ("emote-ugh",          "Ugh",              True),
    "46": ("emote-eyeroll",      "Eye Roll",         True),
    "47": ("emote-facepalm",     "Facepalm",         True),
    "48": ("emote-lust",         "Lust",             True),
    "49": ("emote-greedy",       "Greedy",           True),
    "50": ("emote-model",        "Model",            True),
    "51": ("emote-floating",     "Floating",         True),
    "52": ("emote-singalong",    "Sing Along",       True),
    # ── Emotes PAYANTS (nécessitent d'être achetés) ───────────────────────────
    "53": ("emote-gravity",      "Gravity Zero 💎",  False),
    "54": ("emote-levitation",   "Levitation 💎",    False),
    "55": ("emote-ghostfloat",   "Ghost Float 💎",   False),
    "56": ("emote-kickingback",  "Kicking Back 💎",  False),
    "57": ("emote-rest",         "Rest 💎",          False),
    "58": ("emote-posh",         "Posh 💎",          False),
    "59": ("emote-cozy",         "Cozy 💎",          False),
    "60": ("emote-moonwalk",     "Moonwalk 💎",      False),
    "61": ("dance-tiktok1",      "TikTok 1 💎",      False),
    "62": ("dance-tiktok2",      "TikTok 2 💎",      False),
    "63": ("dance-tiktok8",      "TikTok 8 💎",      False),
    "64": ("idle-sleep",         "Sleep 💎",         False),
    "65": ("idle-sad",           "Pouty 💎",         False),
    "66": ("idle-posh",          "Idle Posh 💎",     False),
    "67": ("idle-loop-tired",    "Loop Tired 💎",    False),
    "68": ("idle_layingdown",    "Lay Down 💎",      False),
    "69": ("idle_layingdown2",   "Relax Down 💎",    False),
    "70": ("idle_zombie",        "Zombie 💎",        False),
    "71": ("sit-idle-cute",      "Sit Cute 💎",      False),
    "72": ("idle-loop-tapdance", "Tap Dance 💎",     False),
    "73": ("dance-smoothwalk",   "Smooth Walk 💎",   False),
    "74": ("dance-singleladies", "Ring on It 💎",    False),
    "75": ("dance-robotic",      "Robotic 💎",       False),
    "76": ("dance-orangejustice","OJ Dance 💎",      False),
    "77": ("dance-metal",        "Rock Out 💎",      False),
    "78": ("dance-spiritual",    "Yoga Flow 💎",     False),
    "79": ("emote-singer",       "Singer 💎",        False),
    "80": ("emote-joyful",       "Joyful 💎",        False),
    "81": ("emote-wink",         "Wink 💎",          False),
    "82": ("emote-kiss",         "Kiss 💎",          False),
}

# ─── Animations (séquences en boucle, emotes gratuits uniquement) ─────────────
ANIMATIONS: dict[str, list[tuple[str, float]]] = {
    "party":   [("dance-tiktok4",6),("dance-tiktok6",6),("dance-macarena",6),
                ("dance-naenae",6),("dance-savage",5),("emoji-clap",4)],
    "showtime":[("emote-pose",3),("dance-tiktok3",6),("emote-float",5),
                ("emote-telekinesis",6),("emote-charging",4),("emote-floating",5)],
    "vibe":    [("emote-float",7),("emote-cute",5),("emote-happy",6),
                ("emote-singalong",6),("emote-shy",5)],
    "rage":    [("emoji-angry",3),("dance-creep",6),("dance-pennywise",6),
                ("emoji-cursing",4),("emote-ugh",3)],
    "chill":   [("emote-float",8),("emote-floating",8),("emote-tired",6),
                ("emote-bow",4),("emote-curtsy",5)],
    "cute":    [("emote-cute",5),("emote-shy",5),("emoji-clap",4),
                ("emote-happy",5),("emote-hello",4)],
    "flex":    [("emoji-flex",4),("emote-pose",4),("emote-model",5),
                ("dance-savage",6),("emote-charging",4)],
    "cry":     [("emote-ugh",4),("emote-facepalm",4),("emote-tired",5),
                ("emote-eyeroll",4)],
    "gravity": [("emote-float",7),("emote-floating",7),("emote-telekinesis",6),
                ("emote-charging",6)],
    "bboy":    [("dance-tiktok5",6),("dance-tiktok7",6),("dance-worm",6),
                ("dance-shuffle",6)],
    "ninja":   [("emote-charging",4),("dance-tiktok9",6),("emote-telekinesis",5),
                ("dance-kick",6)],
    "zen":     [("emote-bow",5),("emote-float",7),("emote-floating",7),
                ("emote-curtsy",5)],
    "disco":   [("dance-shuffle",6),("dance-viral",6),("dance-mood",6),
                ("dance-naenae",6)],
    "vote":    [("emoji-thumbsup",4),("emoji-clap",4),("emote-happy",4),
                ("emote-enthusiastic",5)],
}

# ─── Coordonnées des spots et étages ─────────────────────────────────────────
FLOORS = {
    "f1": (BOT_START_X, 0.0,  BOT_START_Z),
    "f2": (BOT_START_X, 6.0,  BOT_START_Z),
    "f3": (BOT_START_X, 12.0, BOT_START_Z),
    "f4": (BOT_START_X, 18.0, BOT_START_Z),
}
SPOTS = {
    "centre":  (BOT_START_X,       0.0,  BOT_START_Z),
    "entree":  (BOT_START_X,       0.0,  BOT_START_Z + 4),
    "scene":   (BOT_START_X,       0.0,  BOT_START_Z - 4),
    "coin1":   (BOT_START_X + 3,   0.0,  BOT_START_Z + 3),
    "coin2":   (BOT_START_X - 3,   0.0,  BOT_START_Z + 3),
    "coin3":   (BOT_START_X + 3,   0.0,  BOT_START_Z - 3),
    "coin4":   (BOT_START_X - 3,   0.0,  BOT_START_Z - 3),
    "vip":     (BOT_START_X,       6.0,  BOT_START_Z),
    "top":     (BOT_START_X,       18.0, BOT_START_Z),
}

# Portails (xmin, xmax, zmin, zmax, ymin, ymax) → (dest_x, dest_y, dest_z, label)
# Actifs à n'importe quelle hauteur dans la zone XZ définie
PADS: list[tuple[float,float,float,float,float,float, float,float,float, str]] = [
    (12.0, 14.0, 17.0, 19.0, -1.0, 1.5,   13.0,  6.0, 18.0, "🔵 Portail → F2"),
    (12.0, 14.0, 17.0, 19.0,  5.0, 7.5,   13.0, 12.0, 18.0, "🟣 Portail → F3"),
    (12.0, 14.0, 17.0, 19.0, 11.0,13.5,   13.0, 18.0, 18.0, "🟡 Portail → F4"),
    (16.0, 18.0, 23.0, 25.0, -1.0, 1.5,   17.0,  6.0, 24.0, "🟢 Portail B → F2"),
    (16.0, 18.0, 23.0, 25.0,  5.0, 7.5,   17.0,  0.0, 24.0, "🔴 Portail B → F1"),
    (16.0, 18.0, 23.0, 25.0, 11.0,13.5,   17.0,  6.0, 24.0, "🟠 Portail B → F2"),
]

INVALID_EMOTES: set[str] = set()

user_emote_tasks: dict[str, asyncio.Task] = {}
click_tp_users:   set[str]                = set()
last_tp_time:     dict[str, float]        = {}


# ─── Helpers ──────────────────────────────────────────────────────────────────
def px(t: str) -> str:
    return t[:MAX_MSG]

def chunked(text: str, size: int = MAX_MSG) -> list[str]:
    chunks, cur = [], ""
    for line in text.split("\n"):
        test = (cur + "\n" + line).strip() if cur else line
        if len(test) > size:
            if cur: chunks.append(cur.strip())
            cur = line[:size]
        else:
            cur = test
    if cur: chunks.append(cur.strip())
    return chunks or [text[:size]]

def build_emote_pages() -> list[str]:
    pages, items = [], list(EMOTES.items())
    for i in range(0, len(items), 5):
        chunk = items[i:i+5]
        pages.append("\n".join(
            f"{n} {name}" for n, (_, name, _f) in chunk
        ))
    return pages

EMOTE_PAGES = build_emote_pages()
ANIM_LIST   = " | ".join(ANIMATIONS.keys())


# ─── Bot ──────────────────────────────────────────────────────────────────────
class MyBot(BaseBot):

    # ── Init : attributs d'INSTANCE (pas de classe) ───────────────────────────
    def __init__(self):
        self._bot_id:      str             = ""
        self._base_outfit: list[Item]      = []   # BUG CORRIGE : liste propre par instance
        self._outfit_task: asyncio.Task | None = None  # référence pour annulation

    # ── Démarrage ─────────────────────────────────────────────────────────────
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self._bot_id = session_metadata.user_id
        logger.info(f"Connecte ! bot_id={self._bot_id}")
        await asyncio.sleep(1.5)
        await self._tp(self._bot_id, BOT_START_X, BOT_START_Y, BOT_START_Z)
        await self._load_base_outfit()
        # BUG CORRIGE : annuler l'ancienne boucle avant d'en créer une nouvelle
        if self._outfit_task and not self._outfit_task.done():
            self._outfit_task.cancel()
        self._outfit_task = asyncio.create_task(self._outfit_loop())

    # ── Charger la tenue de base ──────────────────────────────────────────────
    async def _load_base_outfit(self) -> None:
        try:
            resp = await self.highrise.get_user_outfit(self._bot_id)
            if hasattr(resp, "outfit"):
                self._base_outfit = list(resp.outfit)
                logger.info(f"Tenue chargee : {len(self._base_outfit)} items")
        except Exception as e:
            logger.warning(f"Tenue non chargee: {e}")

    # ── Boucle changement de tenue toutes les N minutes ───────────────────────
    async def _outfit_loop(self) -> None:
        await asyncio.sleep(5)           # premier changement rapide après démarrage
        while True:
            try:                         # BUG CORRIGE : exceptions ne tuent plus la boucle
                await self._apply_random_outfit()
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.warning(f"_outfit_loop iteration error: {e}")
            await asyncio.sleep(OUTFIT_DELAY)

    # ── Appliquer une tenue aléatoire ─────────────────────────────────────────
    async def _apply_random_outfit(self) -> None:
        if not self._base_outfit:
            await self._load_base_outfit()
            if not self._base_outfit:
                return
        try:
            new_outfit = []
            for item in self._base_outfit:
                # Changer la palette de couleur aléatoirement si supportée
                new_palette = item.active_palette
                if item.active_palette is not None:
                    new_palette = random.randint(0, 9)
                new_outfit.append(Item(
                    type=item.type,
                    amount=item.amount,
                    id=item.id,
                    account_bound=item.account_bound,
                    active_palette=new_palette,
                ))
            # BUG CORRIGE : shuffle supprimé — l'ordre des slots doit rester intact
            result = await self.highrise.set_outfit(new_outfit)
            if result is None:
                logger.info("Tenue changee !")
            else:
                logger.warning(f"set_outfit: {result}")
        except Exception as e:
            logger.warning(f"Outfit error: {e}")

    # ── Arrivée utilisateur ───────────────────────────────────────────────────
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        msg = random.choice(WELCOMES).replace("{u}", user.username)
        await self._chat(msg)
        logger.info(f"JOIN: {user.username}")

    # ── Départ utilisateur ────────────────────────────────────────────────────
    async def on_user_leave(self, user: User) -> None:
        await self._cancel(user.id)
        click_tp_users.discard(user.id)
        last_tp_time.pop(user.id, None)
        logger.info(f"LEAVE: {user.username}")

    # ── Mouvement utilisateur (téléportation immersive universelle) ───────────
    async def on_user_move(self, user: User, destination: Position | AnchorPosition) -> None:
        try:
            # On ignore les AnchorPosition (s'asseoir sur un meuble)
            if not isinstance(destination, Position):
                return
            now = time.monotonic()
            # ── Portails automatiques (fonctionne à toutes les hauteurs) ──────
            for xmin, xmax, zmin, zmax, ymin, ymax, dx, dy, dz, label in PADS:
                if (xmin <= destination.x <= xmax
                        and zmin <= destination.z <= zmax
                        and ymin <= destination.y <= ymax):
                    if now - last_tp_time.get(user.id, 0) > TP_DEBOUNCE:
                        last_tp_time[user.id] = now
                        await self._tp(user.id, dx, dy, dz)
                        await self._whisper(user.id, f"{label} !")
                    return
            # ── Click-téléportation instantanée (mode tpon) ───────────────────
            # Fonctionne à toutes les hauteurs, utilise les coords exactes du clic
            if user.id in click_tp_users:
                if now - last_tp_time.get(user.id, 0) > TP_DEBOUNCE:
                    last_tp_time[user.id] = now
                    # Conserver la hauteur (y) exacte de destination
                    await self._tp(user.id, destination.x, destination.y, destination.z)
        except Exception as e:
            logger.warning(f"on_user_move: {e}")

    # ── Réception message ─────────────────────────────────────────────────────
    async def on_chat(self, user: User, message: str) -> None:
        try:
            await self._handle(user, message)
        except Exception as e:
            logger.error(f"on_chat ({user.username}): {e}")

    # ── Routeur de commandes ──────────────────────────────────────────────────
    async def _handle(self, user: User, message: str) -> None:
        msg = message.strip().lower()

        # aide ─────────────────────────────────────────────────────────────────
        if msg in ("aide", "help", "commandes"):
            lines = [
                "── COMMANDES ──",
                "emotes1..17 — liste emotes",
                "1 a 82 — lancer emote",
                "stop / stopanim — arreter",
                f"ANIMS: {ANIM_LIST}",
                "f1 f2 f3 f4 — etager",
                "aller <spot> — teleport",
                "spots — liste spots",
                "tpon — click-tp ON",
                "tpoff — click-tp OFF",
                "outfit — nouvelle tenue bot",
                "💎 = emote payant",
            ]
            for chunk in chunked("\n".join(lines)):
                await self._whisper(user.id, chunk)
                await asyncio.sleep(0.35)
            return

        # emotes<page> ─────────────────────────────────────────────────────────
        if msg.startswith("emotes"):
            suffix = msg[6:].strip()
            idx = (int(suffix) - 1) if suffix.isdigit() else 0
            if 0 <= idx < len(EMOTE_PAGES):
                await self._whisper(user.id, f"Emotes {idx+1}/{len(EMOTE_PAGES)}:")
                await asyncio.sleep(0.25)
                for chunk in chunked(EMOTE_PAGES[idx]):
                    await self._whisper(user.id, chunk)
                    await asyncio.sleep(0.3)
            else:
                await self._whisper(user.id, f"Pages: 1 a {len(EMOTE_PAGES)}")
            return

        # stop ─────────────────────────────────────────────────────────────────
        if msg in ("stop", "stopanim"):
            await self._cancel(user.id)
            await self._whisper(user.id, "✅ Arrete.")
            return

        # stopall ──────────────────────────────────────────────────────────────
        if msg == "stopall":
            for uid in list(user_emote_tasks.keys()):
                await self._cancel(uid)
            await self._chat("✅ Tout stoppe.")
            return

        # tpon / tpoff ─────────────────────────────────────────────────────────
        if msg == "tpon":
            click_tp_users.add(user.id)
            await self._whisper(user.id, "✅ Click-teleport ON ! Clique n'importe ou, tu teleportes instantanement (toutes hauteurs).")
            return
        if msg == "tpoff":
            click_tp_users.discard(user.id)
            await self._whisper(user.id, "❌ Click-teleport OFF.")
            return

        # outfit ───────────────────────────────────────────────────────────────
        if msg == "outfit":
            await self._apply_random_outfit()
            await self._chat(f"✨ @{user.username} a demande un changement de style ! Nouvelle tenue !")
            return

        # spots ────────────────────────────────────────────────────────────────
        if msg == "spots":
            await self._whisper(user.id, "Spots: " + " | ".join(SPOTS.keys()))
            return

        # aller <spot> ─────────────────────────────────────────────────────────
        if msg.startswith("aller "):
            spot = msg[6:].strip()
            if spot in SPOTS:
                x, y, z = SPOTS[spot]
                await self._tp(user.id, x, y, z)
                await self._whisper(user.id, f"🌀 Teleporte a {spot} !")
            else:
                await self._whisper(user.id, "Spot inconnu. Tape spots")
            return

        # f1 / f2 / f3 / f4 ───────────────────────────────────────────────────
        if msg in ("f1", "f2", "f3", "f4"):
            x, y, z = FLOORS[msg]
            await self._tp(user.id, x, y, z)
            await self._whisper(user.id, f"🏢 Etage {msg.upper()} !")
            return

        # tp x y z  (téléportation libre vers des coordonnées) ─────────────────
        if msg.startswith("tp "):
            parts = msg.split()
            if len(parts) == 4:
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    await self._tp(user.id, x, y, z)
                    await self._whisper(user.id, f"🌀 Teleporte a ({x},{y},{z})")
                except ValueError:
                    await self._whisper(user.id, "Format: tp x y z  ex: tp 15 6 21")
            else:
                await self._whisper(user.id, "Format: tp x y z  ex: tp 15 6 21")
            return

        # animation nommée ─────────────────────────────────────────────────────
        if msg in ANIMATIONS:
            await self._cancel(user.id)
            await self._whisper(user.id, f"🎬 Animation {msg} ! (stopanim pour arreter)")
            task = asyncio.create_task(self._run_anim(user.id, msg))
            user_emote_tasks[user.id] = task
            return

        # emote numérotée ──────────────────────────────────────────────────────
        if msg.isdigit() and msg in EMOTES:
            emote_id, emote_name, is_free = EMOTES[msg]
            if emote_id in INVALID_EMOTES:
                await self._whisper(user.id, f"Emote indisponible.")
                return
            await self._cancel(user.id)
            note = "" if is_free else " — tu dois posseder cet emote dans Highrise"
            await self._whisper(user.id, f"▶ {emote_name}{note} (stop pour arreter)")
            task = asyncio.create_task(self._loop_emote(user.id, emote_id, emote_name, is_free))
            user_emote_tasks[user.id] = task
            return

    # ─── Boucle emote ─────────────────────────────────────────────────────────
    async def _loop_emote(self, user_id: str, emote_id: str, name: str, is_free: bool):
        errors = 0
        while True:
            try:
                await self.highrise.send_emote(emote_id, user_id)
                errors = 0
                await asyncio.sleep(7)
            except asyncio.CancelledError:
                return
            except Exception as e:
                err = str(e).lower()
                if "not in room" in err or "user not found" in err:
                    user_emote_tasks.pop(user_id, None)
                    return
                if "not free or owned" in err:
                    await self._whisper(user_id,
                        f"💎 {name} est payant. Achete-le dans le shop Highrise !")
                    user_emote_tasks.pop(user_id, None)
                    return
                if "unknown emote" in err or "invalid" in err:
                    INVALID_EMOTES.add(emote_id)
                    logger.warning(f"Blacklist emote: {emote_id}")
                    user_emote_tasks.pop(user_id, None)
                    return
                errors += 1
                logger.warning(f"Emote ({emote_id}) err {errors}/5: {e}")
                if errors >= 5:
                    user_emote_tasks.pop(user_id, None)
                    return
                await asyncio.sleep(4)

    # ─── Animation séquence ───────────────────────────────────────────────────
    async def _run_anim(self, user_id: str, key: str):
        sequence = ANIMATIONS[key]
        while True:
            for emote_id, dur in sequence:
                if emote_id in INVALID_EMOTES:
                    continue
                try:
                    await self.highrise.send_emote(emote_id, user_id)
                    await asyncio.sleep(dur)
                except asyncio.CancelledError:
                    return
                except Exception as e:
                    err = str(e).lower()
                    if "not in room" in err or "user not found" in err:
                        user_emote_tasks.pop(user_id, None)
                        return
                    if "unknown emote" in err or "invalid" in err:
                        INVALID_EMOTES.add(emote_id)
                    logger.warning(f"Anim step ({emote_id}): {e}")
                    await asyncio.sleep(2)

    # ─── Annuler tâche ────────────────────────────────────────────────────────
    async def _cancel(self, user_id: str):
        task = user_emote_tasks.pop(user_id, None)
        if task and not task.done():
            task.cancel()
            try:
                # BUG CORRIGE : shield() empêchait l'annulation et levait CancelledError
                # On attend directement la tâche annulée avec un timeout
                await asyncio.wait_for(task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass

    # ─── Téléportation sécurisée ──────────────────────────────────────────────
    async def _tp(self, user_id: str, x: float, y: float, z: float,
                  facing: str = "FrontRight"):
        try:
            await self.highrise.teleport(user_id, Position(x=x, y=y, z=z, facing=facing))
        except Exception as e:
            logger.warning(f"TP ({user_id}→{x},{y},{z}): {e}")

    # ─── Whisper sécurisé ─────────────────────────────────────────────────────
    async def _whisper(self, user_id: str, text: str):
        try:
            await self.highrise.send_whisper(user_id, px(text))
        except Exception as e:
            logger.warning(f"Whisper: {e}")

    # ─── Chat sécurisé ────────────────────────────────────────────────────────
    async def _chat(self, text: str):
        try:
            await self.highrise.chat(px(text))
        except Exception as e:
            logger.warning(f"Chat: {e}")


if __name__ == "__main__":
    token   = os.environ.get("HIGHRISE_TOKEN", "")
    room_id = os.environ.get("HIGHRISE_ROOM_ID", "")
    if not token or not room_id:
        logger.error("HIGHRISE_TOKEN et HIGHRISE_ROOM_ID manquants !")
        exit(1)
    definition = __main__.BotDefinition(bot=MyBot(), room_id=room_id, api_token=token)
    asyncio.run(__main__.main([definition]))
