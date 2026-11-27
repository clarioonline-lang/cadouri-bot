"""
Reel zilnic Cadouri pe Buget: un clip vertical de ~9,5 secunde (1080x1920, MP4, fara sunet).

Structura (ce a mers pe pagina: Reel, mai multe produse pe o tema, indemn la distribuire):
  0,0–1,6 s  carlig: „3 cadouri sub X lei / care par mult mai scumpe” (vizibil din primul cadru)
  1,6–8,2 s  3 produse, cate ~2,2 s: poza in arcada cu zoom lent, numar, nume, pret, reducere
  8,2–9,6 s  final: „Toate ideile de azi, cu link” + cadouripebuget.online
Sus, pe tot clipul: „Trimite-i asta cuiva care nu știe ce să-ți ia”.

Muzica: o melodie pe zi din muzica/ (6 piese din Meta Sound Collection, gratuite pe Facebook si
Instagram, taiate la 9,6 s cu final lin). Pe Instagram se poate inlocui din aplicatie cu un sunet la moda.

Rulare: python reel.py  -> imagini/reel.mp4 + idei/reel.json (textele) + sectiune in FACEBOOK.md
Textul important sta intre y=200 si y=1450: jos si in dreapta sunt butoanele aplicatiei.
"""

import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from imagine_postare import (AURIU, AURIU_DESCHIS, CREM, GRI, NEGRU, SMARALD, VISINIU,
                             contur_arcada, lumina, masca_arcada, rupe_randuri, sans, separator,
                             serif, text_auriu)

W, H, FPS = 1080, 1920, 30
AZI_MD = Path("idei/AZI.md")
IESIRE = Path("imagini/reel.mp4")
INFO = Path("idei/reel.json")
FACEBOOK_MD = Path("idei/FACEBOOK.md")
SITE = "https://cadouripebuget.online"

# (randul 1, randul 2 al bannerului de sus, inceputul textului postarii) - se rotesc zilnic
INDEMNURI = [
    ("Trimite-i asta cuiva", "care nu știe ce să-ți ia", "Trimite-i asta cuiva care nu știe ce să-ți ia 👀🎁"),
    ("Etichetează pe cine", "trebuie să vadă asta", "Etichetează pe cine trebuie să vadă asta 😉🎁"),
    ("Pentru cine zice", "că nu vrea nimic", "Pentru cine zice că „nu vrea nimic” de Crăciun 🎄"),
]
SUBTITLURI = ["care par mult mai scumpe", "pe care chiar le folosește", "reduse azi, cât mai sunt"]
SUS = INDEMNURI[0]


def fundal(seed=7):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), NEGRU)
    img = lumina(img, (60, 120), 1250, VISINIU, 0.95)
    img = lumina(img, (W - 40, H - 80), 1250, SMARALD, 0.95)
    img = lumina(img, (W // 2, 820), 620, (60, 22, 14), 0.5)
    strat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(strat)
    for _ in range(36):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(4, 24)
        d.ellipse([x - r, y - r, x + r, y + r], fill=AURIU_DESCHIS + (rnd.randint(25, 70),))
    return Image.alpha_composite(img.convert("RGBA"), strat.filter(ImageFilter.GaussianBlur(5)))


def bara_sus(img):
    """Indemnul la distribuire, mare, pe doua randuri: se citeste usor pe telefon."""
    d = ImageDraw.Draw(img, "RGBA")
    r1, r2 = SUS[0], SUS[1]
    f = sans(60, 700)
    lw = int(max(f.getlength(r1), f.getlength(r2))) + 110
    x = (W - lw) // 2
    d.rounded_rectangle([x, 120, x + lw, 300], 44, fill=(11, 8, 6, 215), outline=AURIU_DESCHIS + (230,), width=3)
    d.text((W // 2, 172), r1, font=f, fill=CREM, anchor="mm")
    d.text((W // 2, 248), r2, font=f, fill=AURIU_DESCHIS, anchor="mm")


def ecran_carlig(baza, pret_max, subtitlu="care par mult mai scumpe"):
    img = baza.copy()
    bara_sus(img)
    d = ImageDraw.Draw(img, "RGBA")
    text_auriu(img, (W // 2, 700), "3 cadouri", serif(170, 650))
    text_auriu(img, (W // 2, 890), f"sub {pret_max} lei", serif(170, 650))
    d = ImageDraw.Draw(img, "RGBA")
    separator(d, W // 2, 1010, 380)
    d.text((W // 2, 1095), subtitlu, font=serif(66, 400), fill=CREM, anchor="mm")
    d.text((W // 2, 1300), "ideea nr. 3 e preferata noastră ↓", font=sans(38, 500), fill=AURIU, anchor="mm")
    return img


def strat_produs(baza, p, nr):
    """Tot ce nu se misca: fundal, bara, numar, nume, pret. Poza se pune separat (zoom)."""
    img = baza.copy()
    bara_sus(img)
    d = ImageDraw.Draw(img, "RGBA")
    aw, ah, ax, ay = 740, 780, (W - 740) // 2, 380
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).rounded_rectangle([ax - 10, ay - 10, ax + aw + 10, ay + ah + 10], 70, fill=150)
    img.paste(Image.new("RGB", (W, H), AURIU), (0, 0), halo.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .35)))
    d = ImageDraw.Draw(img, "RGBA")
    contur_arcada(d, ax - 24, ay - 24, aw + 48, ah + 48, AURIU + (140,), 2)
    # peste poza: contur, numar, reducere (strat transparent)
    peste = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(peste)
    contur_arcada(od, ax, ay, aw, ah, AURIU_DESCHIS + (255,), 5)
    od.ellipse([ax + aw - 70, ay + ah - 70, ax + aw + 70, ay + ah + 70], fill=(122, 36, 27, 255), outline=AURIU_DESCHIS, width=3)
    text_auriu(peste, (ax + aw, ay + ah + 4), str(nr), serif(90, 700))
    if p["discount"] >= 10:
        txt, f = f"-{p['discount']}%", sans(46, 700)
        lw = int(f.getlength(txt)) + 50
        bx, by = ax - 10, ay + aw // 2 - 30
        od.rounded_rectangle([bx, by, bx + lw, by + 72], 36, fill=(122, 36, 27, 255), outline=AURIU_DESCHIS, width=2)
        od.text((bx + lw // 2, by + 36), txt, font=f, fill=AURIU_DESCHIS, anchor="mm")
    # nume + pret
    y = ay + ah + 110
    fn = serif(54, 500)
    for rand in rupe_randuri(p["nume"], fn, W - 160):
        d.text((W // 2, y), rand, font=fn, fill=CREM, anchor="mm")
        y += 66
    text_auriu(img, (W // 2, y + 70), f"{p['pret']} lei", serif(120, 650))
    d = ImageDraw.Draw(img, "RGBA")
    if p["discount"] >= 10:
        vechi = round(p["pret"] / (1 - p["discount"] / 100))
        d.text((W // 2, y + 165), f"în loc de {vechi} lei", font=sans(36, 400), fill=GRI, anchor="mm")
    return img, peste, (ax, ay, aw, ah)


def ecran_final(baza):
    img = baza.copy()
    bara_sus(img)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((W // 2, 640), "Toate cele 10 idei de azi,", font=serif(70, 500), fill=CREM, anchor="mm")
    d.text((W // 2, 730), "cu link direct la magazin:", font=serif(70, 500), fill=CREM, anchor="mm")
    separator(d, W // 2, 830, 380)
    text_auriu(img, (W // 2, 940), "cadouripebuget.online", serif(92, 650))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([W // 2 - 230, 1060, W // 2 + 230, 1150], 45, fill=(122, 36, 27), outline=AURIU_DESCHIS, width=2)
    d.text((W // 2, 1105), "Link în bio", font=sans(46, 700), fill=AURIU_DESCHIS, anchor="mm")
    d.text((W // 2, 1260), "Salvează pentru Crăciun", font=sans(40, 500), fill=AURIU, anchor="mm")
    d.text((W // 2, 1340), "@cadouripebuget · conține linkuri de afiliere", font=sans(30, 400), fill=GRI, anchor="mm")
    return img


def usor(t):  # ease-out
    return 1 - (1 - t) ** 3


def randeaza(produse, poze, iesire, subtitlu="care par mult mai scumpe", muzica=None):
    pret_max = max(p["pret"] for p in produse)
    pret_max = (pret_max // 5 + 1) * 5 if pret_max % 5 else pret_max
    baza = fundal()
    carlig = ecran_carlig(baza, pret_max, subtitlu).convert("RGB")
    final = ecran_final(baza).convert("RGB")
    scene = [strat_produs(baza, p, i + 1) for i, p in enumerate(produse)]

    t_carlig, t_prod, t_final = 1.6, 2.2, 1.4
    total = int((t_carlig + 3 * t_prod + t_final) * FPS)
    Path(iesire).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if muzica:   # melodie din Meta Sound Collection (taiata deja la 9,6 s, cu final lin)
        cmd += ["-i", str(muzica), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(iesire)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(total):
        t = k / FPS
        if t < t_carlig:
            cadru = carlig
        elif t < t_carlig + 3 * t_prod:
            i = int((t - t_carlig) // t_prod)
            tl = (t - t_carlig) - i * t_prod
            strat, peste, (ax, ay, aw, ah) = scene[i]
            z = 1.0 + 0.08 * (tl / t_prod)                    # zoom lent
            pw, ph = int(aw * z), int(ah * z)
            poza = ImageOps.fit(poze[i], (pw, ph), Image.BILINEAR, centering=(0.5, 0.45))
            poza = poza.crop(((pw - aw) // 2, (ph - ah) // 2, (pw - aw) // 2 + aw, (ph - ah) // 2 + ah))
            cadru = strat.copy()
            panou = Image.new("RGB", (aw, ah), (255, 255, 255))
            panou.paste(poza, (0, 0))
            cadru.paste(panou, (ax, ay), masca_arcada(aw, ah))
            cadru = Image.alpha_composite(cadru, peste)
            cadru = cadru.convert("RGB")
            if tl < 0.25:                                      # intrare din dreapta
                dx = int(W * (1 - usor(tl / 0.25)))
                prev = carlig if i == 0 else ultimul
                c2 = prev.copy()
                c2.paste(cadru.crop((0, 0, W - dx, H)), (dx, 0))
                cadru = c2
        else:
            tl = t - t_carlig - 3 * t_prod
            cadru = final if tl >= 0.2 else Image.blend(ultimul, final, tl / 0.2)
        ff.stdin.write(cadru.tobytes())
        if t_carlig <= t < t_carlig + 3 * t_prod and (t - t_carlig) % t_prod >= 0.25:
            ultimul = cadru
    ff.stdin.close()
    ff.wait()
    return iesire


def alege_trei(produse):
    """3 produse cu poza: cele mai mari reduceri; cea mai buna la final („ideea nr. 3”)."""
    cu_poza = [p for p in produse if p.get("poza")]
    top = sorted(cu_poza, key=lambda p: (p["discount"], -p["pret"]), reverse=True)[:3]
    return sorted(top, key=lambda p: (p["discount"], -p["pret"]))


def pret_vechi(p):
    return round(p["pret"] / (1 - p["discount"] / 100)) if p["discount"] >= 10 else None


def texte(trei, indemn):
    cifre = ["1️⃣", "2️⃣", "3️⃣"]
    randuri = []
    for c, p in zip(cifre, trei):
        v = pret_vechi(p)
        randuri.append(f"{c} {p['nume']} – {p['pret']} lei" + (f" (în loc de {v} lei)" if v else ""))
    lista = "\n".join(randuri)
    fb = (f"{indemn}\n\n{lista}\n\nVrei linkurile? Scrie CADOU în comentarii și ți le trimit pe Messenger 📩\n"
          f"Toate cele 10 idei de azi sunt și pe site-ul din profilul paginii.\n\n"
          f"#cadouripebuget #ideicadouri #cadouri #cadouridecraciun #afiliere")
    ig = (f"{indemn}\n\n{lista}\n\n🔗 Link în bio → toate cele 10 idei de azi, cu link direct la magazin.\n"
          f"Salvează Reel-ul ca să-l ai la îndemână 📌\n\n"
          f"#cadouripebuget #ideicadouri #cadouri #cadouridecraciun #cadou #romania #afiliere")
    return fb, ig


def main():
    import json
    from datetime import date
    from facebook_post import citeste_idei
    from imagine_postare import descarca_poza
    global SUS

    if not AZI_MD.exists():
        print("Nu exista idei/AZI.md - nu fac Reel.")
        return
    trei = alege_trei(citeste_idei(AZI_MD.read_text(encoding="utf-8")))
    if len(trei) < 3:
        print("Sub 3 produse cu poza - nu fac Reel.")
        return
    poze = [descarca_poza(p["poza"]) for p in trei]
    if any(p is None for p in poze):
        print("Nu am putut descarca toate pozele - nu fac Reel.")
        return

    azi = date.today()
    SUS = INDEMNURI[azi.toordinal() % len(INDEMNURI)]
    subtitlu = SUBTITLURI[azi.toordinal() % len(SUBTITLURI)]
    melodii = sorted(Path(__file__).resolve().parent.glob("muzica/*.m4a"))
    muzica = melodii[azi.toordinal() % len(melodii)] if melodii else None
    randeaza(trei, poze, IESIRE, subtitlu, muzica)
    print(f"Muzica: {muzica.name if muzica else 'fara'}")
    fb, ig = texte(trei, SUS[2])
    INFO.write_text(json.dumps({"data": azi.isoformat(), "fisier": str(IESIRE), "text_facebook": fb,
                                "text_instagram": ig, "produse": [p["nume"] for p in trei]},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    if FACEBOOK_MD.exists() and "## Reel" not in FACEBOOK_MD.read_text(encoding="utf-8"):
        with FACEBOOK_MD.open("a", encoding="utf-8") as f:
            f.write(f"\n\n## Reel pentru Instagram (de pe telefon)\n\n"
                    f"1. Descarcă clipul (după ~06:10): {SITE}/imagini/reel.mp4\n"
                    f"2. Instagram → + → Reel → alege clipul → adaugă o melodie la modă.\n"
                    f"3. Lipește textul de mai jos.\n\n```\n{ig}\n```\n")
    print(f"Reel: {IESIRE} ({', '.join(p['nume'] for p in trei)})")


if __name__ == "__main__":
    if len(sys.argv) == 4:   # proba locala: python3 reel.py poza1 poza2 poza3
        produse = [
            {"nume": "Cană de cafea cu pereți dubli, 450 ml", "pret": 36, "discount": 50},
            {"nume": "Set caligrafie vintage cu pană", "pret": 68, "discount": 49},
            {"nume": "Ceas LED cu încărcare wireless", "pret": 70, "discount": 50},
        ]
        poze = [Image.open(c).convert("RGB") for c in sys.argv[1:4]]
        print(randeaza(produse, poze, Path("reel-proba.mp4")))
    else:
        main()
