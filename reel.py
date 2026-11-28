"""
Reel zilnic Cadouri pe Buget: un clip vertical de 9,6 secunde (1080x1920, MP4, cu muzica).

Acelasi stil vizual in fiecare zi, dar formatul se schimba dupa zi, ca urmaritorii sa nu se
plictiseasca si ca sa vedem in statistici ce format merge:
  luni, vineri, sambata, duminica  -> LISTA: „3 cadouri sub X lei / care par mult mai scumpe”
  marti                            -> PENTRU EA: „Trimite-i asta iubitului” + 3 cadouri pentru ea
  miercuri                         -> PENTRU EL: „Trimite-i asta iubitei” + 3 cadouri pentru el
  joi                              -> GHICESTE PRETUL: produsul, „Cât crezi că costă?”, 3-2-1, pretul

Textul important sta intre y=120 si y=1550: jos si in dreapta sunt butoanele aplicatiei.
Muzica: o melodie pe zi din muzica/ (piese din Meta Sound Collection, gratuite pe Facebook si
Instagram, taiate la 9,6 s cu final lin). Pe Instagram se poate inlocui din aplicatie.

Rulare: python reel.py  -> imagini/reel.mp4 + idei/reel.json (textele) + sectiune in FACEBOOK.md
"""

import json
import random
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from imagine_postare import (AURIU, AURIU_DESCHIS, CREM, GRI, NEGRU, SMARALD, VISINIU,
                             contur_arcada, lumina, masca_arcada, rupe_randuri, sans, separator,
                             serif, text_auriu)

W, H, FPS = 1080, 1920, 30
DURATA = 9.6
AZI_MD = Path("idei/AZI.md")
IESIRE = Path("imagini/reel.mp4")
INFO = Path("idei/reel.json")
FACEBOOK_MD = Path("idei/FACEBOOK.md")
SITE = "https://cadouripebuget.online"
VISINIU_BUTON = (122, 36, 27)

# formatul pe zile (0 = luni ... 6 = duminica)
FORMAT = {0: "lista", 1: "ea", 2: "el", 3: "ghiceste", 4: "lista", 5: "lista", 6: "lista"}

# LISTA: (banner rand 1, banner rand 2, inceputul textului postarii) - se rotesc
INDEMNURI = [
    ("Trimite-i asta cuiva", "care nu știe ce să-ți ia", "Trimite-i asta cuiva care nu știe ce să-ți ia 👀🎁"),
    ("Etichetează pe cine", "trebuie să vadă asta", "Etichetează pe cine trebuie să vadă asta 😉🎁"),
    ("Pentru cine zice", "că nu vrea nimic", "Pentru cine zice că „nu vrea nimic” de Crăciun 🎄"),
]
SUBTITLURI = ["care par mult mai scumpe", "pe care chiar le folosește", "reduse azi, cât mai sunt"]

CUVINTE_EA = ["ea", "femei", "dama", "bijuter", "bratara", "colier", "cercei", "inel", "manichiura",
              "parfum", "cosmetic", "fata", "ten", "spa", "lumanare", "cana", "beauty", "ruj",
              "machiaj", "par", "geanta", "esarfa", "pijama", "halat", "flori", "trandafir"]
CUVINTE_EL = ["barbat", "el ", "tata", "whisky", "bere", "gadget", "carti de joc", "portofel",
              "ceas", "brichet", "unelte", "cool", "black", "gentleman", "gamer", "joc", "sofer",
              "masina", "cafea", "gratar", "bucatar", "barba", "x si o", "sah"]


# ---------- desen ----------

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


def bara_sus(img, r1, r2):
    """Mesajul de sus, mare, pe doua randuri: se citeste usor pe telefon."""
    d = ImageDraw.Draw(img, "RGBA")
    f = sans(60, 700)
    lw = int(max(f.getlength(r1), f.getlength(r2))) + 110
    x = (W - lw) // 2
    d.rounded_rectangle([x, 120, x + lw, 300], 44, fill=(11, 8, 6, 215), outline=AURIU_DESCHIS + (230,), width=3)
    d.text((W // 2, 172), r1, font=f, fill=CREM, anchor="mm")
    d.text((W // 2, 248), r2, font=f, fill=AURIU_DESCHIS, anchor="mm")
    d.text((W // 2, 334), "#publicitate · conține linkuri de afiliere", font=sans(30, 500), fill=CREM + (200,), anchor="mm")


def ecran_carlig(baza, banner, titlu1, titlu2, subtitlu):
    img = baza.copy()
    bara_sus(img, *banner)
    text_auriu(img, (W // 2, 700), titlu1, serif(170, 650))
    text_auriu(img, (W // 2, 890), titlu2, serif(170 if len(titlu2) <= 11 else 140, 650))
    d = ImageDraw.Draw(img, "RGBA")
    separator(d, W // 2, 1010, 380)
    d.text((W // 2, 1095), subtitlu, font=serif(66, 400), fill=CREM, anchor="mm")
    d.text((W // 2, 1300), "ideea nr. 3 e preferata noastră ↓", font=sans(38, 500), fill=AURIU, anchor="mm")
    return img.convert("RGB")


ARCADA = (740, 780, (W - 740) // 2, 380)   # latime, inaltime, x, y


def strat_produs(baza, banner, p, nr=None, pret="arata"):
    """Partea fixa a unui ecran cu produs + stratul transparent de peste poza.
    pret: "arata" (pretul si reducerea), "ascuns" (Cât crezi că costă?)."""
    aw, ah, ax, ay = ARCADA
    img = baza.copy()
    bara_sus(img, *banner)
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).rounded_rectangle([ax - 10, ay - 10, ax + aw + 10, ay + ah + 10], 70, fill=150)
    img.paste(Image.new("RGB", (W, H), AURIU), (0, 0),
              halo.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .35)))
    d = ImageDraw.Draw(img, "RGBA")
    contur_arcada(d, ax - 24, ay - 24, aw + 48, ah + 48, AURIU + (140,), 2)

    peste = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(peste)
    contur_arcada(od, ax, ay, aw, ah, AURIU_DESCHIS + (255,), 5)
    if nr is not None:
        od.ellipse([ax + aw - 70, ay + ah - 70, ax + aw + 70, ay + ah + 70], fill=VISINIU_BUTON + (255,),
                   outline=AURIU_DESCHIS, width=3)
        text_auriu(peste, (ax + aw, ay + ah + 4), str(nr), serif(90, 700))
    if pret == "arata" and p["discount"] >= 10:
        txt, f = f"-{p['discount']}%", sans(46, 700)
        lw = int(f.getlength(txt)) + 50
        bx, by = ax - 10, ay + aw // 2 - 30
        od.rounded_rectangle([bx, by, bx + lw, by + 72], 36, fill=VISINIU_BUTON + (255,), outline=AURIU_DESCHIS, width=2)
        od.text((bx + lw // 2, by + 36), txt, font=f, fill=AURIU_DESCHIS, anchor="mm")

    y = ay + ah + 110
    fn = serif(54, 500)
    for rand in rupe_randuri(p["nume"], fn, W - 160):
        d.text((W // 2, y), rand, font=fn, fill=CREM, anchor="mm")
        y += 66
    if pret == "arata":
        text_auriu(img, (W // 2, y + 70), f"{p['pret']} lei", serif(120, 650))
        d = ImageDraw.Draw(img, "RGBA")
        v = pret_vechi(p)
        if v:
            d.text((W // 2, y + 165), f"în loc de {v} lei", font=sans(36, 400), fill=GRI, anchor="mm")
    else:
        text_auriu(img, (W // 2, y + 60), "Cât crezi că costă?", serif(84, 600))
        d = ImageDraw.Draw(img, "RGBA")
        d.text((W // 2, y + 150), "scrie în comentarii, apoi uită-te ↓", font=sans(36, 500), fill=GRI, anchor="mm")
    return img, peste, y


def ecran_final(baza, banner):
    img = baza.copy()
    bara_sus(img, *banner)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((W // 2, 640), "Toate cele 10 idei de azi,", font=serif(70, 500), fill=CREM, anchor="mm")
    d.text((W // 2, 730), "cu link direct la magazin:", font=serif(70, 500), fill=CREM, anchor="mm")
    separator(d, W // 2, 830, 380)
    text_auriu(img, (W // 2, 940), "cadouripebuget.online", serif(92, 650))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([W // 2 - 230, 1060, W // 2 + 230, 1150], 45, fill=VISINIU_BUTON, outline=AURIU_DESCHIS, width=2)
    d.text((W // 2, 1105), "Link în bio", font=sans(46, 700), fill=AURIU_DESCHIS, anchor="mm")
    d.text((W // 2, 1260), "Salvează pentru Crăciun", font=sans(40, 500), fill=AURIU, anchor="mm")
    d.text((W // 2, 1340), "@cadouripebuget · conține linkuri de afiliere", font=sans(30, 400), fill=GRI, anchor="mm")
    return img.convert("RGB")


def cadru_cu_poza(strat, peste, poza, progres):
    """Pune poza in arcada, cu zoom lent (progres 0..1)."""
    aw, ah, ax, ay = ARCADA
    z = 1.0 + 0.08 * progres
    pw, ph = int(aw * z), int(ah * z)
    pz = ImageOps.fit(poza, (pw, ph), Image.BILINEAR, centering=(0.5, 0.45))
    pz = pz.crop(((pw - aw) // 2, (ph - ah) // 2, (pw - aw) // 2 + aw, (ph - ah) // 2 + ah))
    cadru = strat.copy()
    panou = Image.new("RGB", (aw, ah), (255, 255, 255))
    panou.paste(pz, (0, 0))
    cadru.paste(panou, (ax, ay), masca_arcada(aw, ah))
    return Image.alpha_composite(cadru, peste).convert("RGB")


def usor(t):  # ease-out
    return 1 - (1 - t) ** 3


def intrare(prev, cadru, tl, durata=0.25):
    """Ecranul nou intra din dreapta peste cel vechi."""
    if tl >= durata:
        return cadru
    dx = int(W * (1 - usor(tl / durata)))
    c2 = prev.copy()
    c2.paste(cadru.crop((0, 0, W - dx, H)), (dx, 0))
    return c2


def ffmpeg(iesire, muzica):
    Path(iesire).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if muzica:
        cmd += ["-i", str(muzica), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(iesire)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


# ---------- formatele ----------

def randeaza_lista(produse, poze, iesire, banner, titlu1, titlu2, subtitlu, muzica=None):
    baza = fundal()
    carlig = ecran_carlig(baza, banner, titlu1, titlu2, subtitlu)
    final = ecran_final(baza, banner)
    scene = [strat_produs(baza, banner, p, i + 1)[:2] for i, p in enumerate(produse)]
    t_carlig, t_prod = 1.6, 2.2
    ff = ffmpeg(iesire, muzica)
    ultimul = carlig
    for k in range(int(DURATA * FPS)):
        t = k / FPS
        if t < t_carlig:
            cadru = carlig
        elif t < t_carlig + 3 * t_prod:
            i = int((t - t_carlig) // t_prod)
            tl = (t - t_carlig) - i * t_prod
            plin = cadru_cu_poza(*scene[i], poze[i], tl / t_prod)
            cadru = intrare(carlig if i == 0 else ultimul, plin, tl)
            if tl >= 0.25:
                ultimul = cadru
        else:
            tl = t - t_carlig - 3 * t_prod
            cadru = final if tl >= 0.2 else Image.blend(ultimul, final, tl / 0.2)
        ff.stdin.write(cadru.tobytes())
    ff.stdin.close()
    ff.wait()
    return iesire


def randeaza_ghiceste(p, poza, iesire, muzica=None):
    banner = ("Ghicește prețul", "înainte să apară")
    baza = fundal(11)
    ascuns, peste_a, y = strat_produs(baza, banner, p, pret="ascuns")
    aratat, peste_b, _ = strat_produs(baza, banner, p, pret="arata")
    final = ecran_final(baza, banner)
    t_ghici, t_pret = 4.6, 3.4          # 0-4,6 s intrebarea (cu 3-2-1), apoi pretul, apoi finalul
    f_num = serif(230, 700)
    ff = ffmpeg(iesire, muzica)
    ultimul = None
    for k in range(int(DURATA * FPS)):
        t = k / FPS
        if t < t_ghici:
            cadru = cadru_cu_poza(ascuns, peste_a, poza, t / (t_ghici + t_pret))
            if t >= 2.2:                 # numaratoare inversa 3-2-1 peste poza
                n = 3 - int((t - 2.2) // 0.8)
                c = cadru.convert("RGBA")
                strat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                sd = ImageDraw.Draw(strat)
                cx, cy = W // 2, 380 + 390
                sd.ellipse([cx - 170, cy - 170, cx + 170, cy + 170], fill=(11, 8, 6, 175),
                           outline=AURIU_DESCHIS + (255,), width=5)
                text_auriu(strat, (cx, cy + 6), str(max(n, 1)), f_num)
                cadru = Image.alpha_composite(c, strat).convert("RGB")
        elif t < t_ghici + t_pret:
            tl = t - t_ghici
            cadru = cadru_cu_poza(aratat, peste_b, poza, t / (t_ghici + t_pret))
            if tl < 0.18:                # sclipire scurta la dezvaluire
                cadru = Image.blend(cadru, Image.new("RGB", (W, H), AURIU_DESCHIS), 0.35 * (1 - tl / 0.18))
            ultimul = cadru
        else:
            tl = t - t_ghici - t_pret
            cadru = final if tl >= 0.2 else Image.blend(ultimul, final, tl / 0.2)
        ff.stdin.write(cadru.tobytes())
    ff.stdin.close()
    ff.wait()
    return iesire


# ---------- alegerea produselor si textele ----------

def pret_vechi(p):
    return round(p["pret"] / (1 - p["discount"] / 100)) if p["discount"] >= 10 else None


def plafon(produse):
    m = max(p["pret"] for p in produse)
    return (m // 5 + 1) * 5 if m % 5 else m


def ordoneaza(trei):
    """Cea mai buna reducere la final („ideea nr. 3”)."""
    return sorted(trei, key=lambda p: (p["discount"], -p["pret"]))


def alege_trei(produse, cuvinte=None):
    from facebook_post import norm
    cu_poza = [p for p in produse if p.get("poza")]
    potrivite = []
    if cuvinte:
        def se_potriveste(p):
            text = norm(p["nume"] + " " + p.get("categorie", ""))
            cuv = text.split()
            for c in (norm(x) for x in cuvinte):
                if (" " in c and c in text) or any(w.startswith(c) for w in cuv):
                    return True
            return False
        potrivite = [p for p in cu_poza if se_potriveste(p)]
    if cuvinte and len(potrivite) < 2:
        return []          # prea putine produse pe tema: main() trece la formatul lista
    top = sorted(potrivite, key=lambda p: p["discount"], reverse=True)[:3]
    restul = sorted([p for p in cu_poza if p not in top], key=lambda p: (p["discount"], -p["pret"]), reverse=True)
    return ordoneaza((top + restul)[:3])


def lista_text(trei):
    cifre = ["1️⃣", "2️⃣", "3️⃣"]
    randuri = []
    for c, p in zip(cifre, trei):
        v = pret_vechi(p)
        randuri.append(f"{c} {p['nume']} – {p['pret']} lei" + (f" (în loc de {v} lei)" if v else ""))
    return "\n".join(randuri)


def texte(indemn, corp):
    from facebook_post import MARCAJ
    fb = (f"{indemn}\n{MARCAJ}\n\n{corp}\n\nVrei linkurile? Scrie CADOU în comentarii și ți le trimit pe Messenger 📩\n"
          f"Toate cele 10 idei de azi sunt și pe site-ul din profilul paginii.\n\n"
          f"#cadouripebuget #ideicadouri #cadouri #cadouridecraciun #afiliere")
    ig = (f"{indemn}\n{MARCAJ}\n\n{corp}\n\n🔗 Link în bio → toate cele 10 idei de azi, cu link direct la magazin.\n"
          f"Salvează Reel-ul ca să-l ai la îndemână 📌\n\n"
          f"#cadouripebuget #ideicadouri #cadouri #cadouridecraciun #cadou #romania #afiliere")
    return fb, ig


def main(forteaza_format=None):
    from facebook_post import citeste_idei
    from imagine_postare import descarca_poza

    if not AZI_MD.exists():
        print("Nu exista idei/AZI.md - nu fac Reel.")
        return
    produse = citeste_idei(AZI_MD.read_text(encoding="utf-8"))
    azi = date.today()
    fmt = forteaza_format or FORMAT[azi.weekday()]
    melodii = sorted(Path(__file__).resolve().parent.glob("muzica/*.m4a"))
    muzica = melodii[azi.toordinal() % len(melodii)] if melodii else None

    if fmt == "ghiceste":
        cu_poza = sorted([p for p in produse if p.get("poza") and p["discount"] >= 10],
                         key=lambda p: p["discount"], reverse=True)
        if not cu_poza:
            fmt = "lista"
        else:
            p = cu_poza[0]
            poza = descarca_poza(p["poza"])
            if poza is None:
                fmt = "lista"
            else:
                randeaza_ghiceste(p, poza, IESIRE, muzica)
                alese = [p]
                indemn = "Ghicește prețul înainte să apară 👀 Scrie în comentarii cât crezi că costă!"
                corp = (f"🎁 {p['nume']}\n💸 Răspunsul: {p['pret']} lei în loc de {pret_vechi(p)} lei "
                        f"(-{p['discount']}%)")

    if fmt in ("ea", "el") and not alege_trei(produse, CUVINTE_EA if fmt == "ea" else CUVINTE_EL):
        print(f"Prea putine produse pentru formatul „{fmt}” azi - fac lista.")
        fmt = "lista"
    if fmt != "ghiceste":
        if fmt == "ea":
            trei = alege_trei(produse, CUVINTE_EA)
            banner = ("Trimite-i asta", "iubitului. Acum.")
            titluri = ("3 cadouri", "pentru ea", f"sub {plafon(trei)} lei, care par scumpe")
            indemn = "Trimite-i asta iubitului 👀💝 (sau ia-ți singură unul)"
        elif fmt == "el":
            trei = alege_trei(produse, CUVINTE_EL)
            banner = ("Trimite-i asta", "iubitei. Pe față.")
            titluri = ("3 cadouri", "pentru el", f"sub {plafon(trei)} lei, care chiar îi plac")
            indemn = "Trimite-i asta iubitei 😏🎁 Ca să nu mai primești șosete"
        else:
            trei = alege_trei(produse)
            banner = INDEMNURI[azi.toordinal() % len(INDEMNURI)][:2]
            titluri = ("3 cadouri", f"sub {plafon(trei)} lei", SUBTITLURI[azi.toordinal() % len(SUBTITLURI)])
            indemn = INDEMNURI[azi.toordinal() % len(INDEMNURI)][2]
        if len(trei) < 3:
            print("Sub 3 produse cu poza - nu fac Reel.")
            return
        poze = [descarca_poza(p["poza"]) for p in trei]
        if any(p is None for p in poze):
            print("Nu am putut descarca toate pozele - nu fac Reel.")
            return
        randeaza_lista(trei, poze, IESIRE, banner, *titluri, muzica)
        alese = trei
        corp = lista_text(trei)

    fb, ig = texte(indemn, corp)
    INFO.write_text(json.dumps({"data": azi.isoformat(), "format": fmt, "fisier": str(IESIRE),
                                "muzica": muzica.name if muzica else None,
                                "text_facebook": fb, "text_instagram": ig,
                                "produse": [p["nume"] for p in alese]},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    if FACEBOOK_MD.exists() and "## Reel" not in FACEBOOK_MD.read_text(encoding="utf-8"):
        with FACEBOOK_MD.open("a", encoding="utf-8") as f:
            f.write(f"\n\n## Reel pentru Instagram (de pe telefon)\n\n"
                    f"1. Descarcă clipul (după ~06:10): {SITE}/imagini/reel.mp4\n"
                    f"2. Instagram → + → Reel → alege clipul (are deja muzică; o poți schimba cu una la modă).\n"
                    f"3. Lipește textul de mai jos.\n\n```\n{ig}\n```\n")
    print(f"Reel ({fmt}, muzica: {muzica.name if muzica else 'fara'}): "
          f"{IESIRE} ({', '.join(p['nume'] for p in alese)})")


if __name__ == "__main__":
    # python reel.py            -> formatul zilei
    # python reel.py ghiceste   -> forteaza un format (lista / ea / el / ghiceste), pentru proba
    main(sys.argv[1] if len(sys.argv) > 1 else None)
