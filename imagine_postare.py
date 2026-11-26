"""
Deseneaza imaginile postarii de Facebook in stilul paginii Cadouri pe Buget:
fundal aproape negru cu lumini visinii si verzi, produsul intr-o arcada aurie,
numele cu litere serif si pretul mare, auriu.

Citeste idei/facebook_post.json (scris de facebook_post.py), salveaza imaginile in
imagini/ (1080x1350, JPG) si adauga lista lor in json, la "imagini".
post_facebook.py le urca pe Facebook. Daca ceva nu merge, postarea foloseste poza
originala a produsului, ca pana acum.
"""

import io
import json
import random
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

POSTARE = Path("idei/facebook_post.json")
FOLDER = Path("imagini")
FONTURI = Path(__file__).resolve().parent / "fonturi"

W, H = 1080, 1350
NEGRU = (11, 8, 6)
VISINIU = (97, 28, 21)
SMARALD = (24, 53, 33)
AURIU = (219, 166, 102)
AURIU_DESCHIS = (240, 200, 150)
AURIU_INCHIS = (168, 118, 58)
CREM = (243, 230, 212)
GRI = (185, 168, 148)


def font(nume, marime, greutate):
    f = ImageFont.truetype(str(FONTURI / nume), marime)
    try:
        f.set_variation_by_axes([greutate] if nume.startswith("Playfair") else [14, greutate])
    except Exception:
        pass
    return f


def serif(m, g=500):
    return font("PlayfairDisplay.ttf", m, g)


def sans(m, g=500):
    return font("Inter.ttf", m, g)


def lumina(img, centru, raza, culoare, intensitate):
    """O lumina moale, rotunda, ca in fundalul postarilor."""
    grad = Image.radial_gradient("L").resize((raza * 2, raza * 2))      # 0 in centru, 128 pe cerc
    alfa = grad.point(lambda v: int(max(0.0, 1 - v / 128) ** 1.15 * 255 * intensitate))
    strat = Image.new("L", img.size, 0)
    x, y = centru
    strat.paste(alfa, (x - raza, y - raza))
    return Image.composite(Image.new("RGB", img.size, culoare), img, strat)


def fundal(seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), NEGRU)
    img = lumina(img, (40, 60), 900, VISINIU, 0.95)
    img = lumina(img, (W - 20, H - 40), 900, SMARALD, 0.95)
    img = lumina(img, (W // 2, 560), 520, (60, 22, 14), 0.5)
    # puncte aurii estompate (bokeh)
    strat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(strat)
    for _ in range(28):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(4, 22)
        d.ellipse([x - r, y - r, x + r, y + r], fill=AURIU_DESCHIS + (rnd.randint(25, 70),))
    strat = strat.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img.convert("RGBA"), strat)
    return img


def masca_arcada(w, h):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([0, w // 2, w, h], fill=255)
    d.ellipse([0, 0, w, w], fill=255)
    return m


def contur_arcada(d, x, y, w, h, culoare, grosime):
    r = w // 2
    d.arc([x, y, x + w, y + w], 180, 360, fill=culoare, width=grosime)
    d.line([x + grosime // 2, y + r, x + grosime // 2, y + h], fill=culoare, width=grosime)
    d.line([x + w - grosime // 2 - 1, y + r, x + w - grosime // 2 - 1, y + h], fill=culoare, width=grosime)
    d.line([x, y + h - grosime // 2, x + w, y + h - grosime // 2], fill=culoare, width=grosime)


def descarca_poza(url):
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 cadouri-bot"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGB")
    except Exception as e:
        print(f"Nu am putut descarca poza: {e}")
        return None


def text_auriu(img, xy, text, f, ancora="mm"):
    """Text cu gradient auriu de sus in jos, ca in postari."""
    masca = Image.new("L", img.size, 0)
    try:   # cifre drepte (ca in postari); fara libraqm, cifrele raman cele implicite
        ImageDraw.Draw(masca).text(xy, text, font=f, fill=255, anchor=ancora, features=["lnum"])
    except Exception:
        ImageDraw.Draw(masca).text(xy, text, font=f, fill=255, anchor=ancora)
    st, sus, dr, jos = masca.getbbox() or (0, 0, 1, 1)
    grad = Image.new("RGB", img.size, AURIU)
    gd = ImageDraw.Draw(grad)
    inalt = max(1, jos - sus)
    for i in range(inalt):
        t = i / inalt
        c1, c2 = (AURIU_DESCHIS, AURIU) if t < 0.6 else (AURIU, AURIU_INCHIS)
        tt = t / 0.6 if t < 0.6 else (t - 0.6) / 0.4
        gd.line([(st, sus + i), (dr, sus + i)], fill=tuple(int(a + (b - a) * tt) for a, b in zip(c1, c2)))
    img.paste(grad, (0, 0), masca)


def rupe_randuri(text, f, latime, maxim=2):
    cuvinte, randuri, rand = text.split(), [], ""
    for c in cuvinte:
        test = (rand + " " + c).strip()
        if f.getlength(test) <= latime:
            rand = test
        else:
            randuri.append(rand)
            rand = c
    randuri.append(rand)
    if len(randuri) > maxim:
        randuri = randuri[:maxim]
        while f.getlength(randuri[-1] + "…") > latime and " " in randuri[-1]:
            randuri[-1] = randuri[-1].rsplit(" ", 1)[0]
        randuri[-1] += "…"
    return [r for r in randuri if r]


def separator(d, cx, y, latime):
    for i in range(latime // 2):
        a = int(200 * (1 - i / (latime / 2)))
        d.point([(cx - 18 - i, y), (cx + 18 + i, y)], fill=AURIU + (a,))
    d.polygon([(cx, y - 7), (cx + 7, y), (cx, y + 7), (cx - 7, y)], fill=AURIU_DESCHIS)


def fara_emoji(text):
    """Fonturile nu au emoji: le scoatem din eticheta."""
    curat = "".join(c for c in text if ord(c) < 0x2600)
    return " ".join(curat.replace("()", "").split())


def deseneaza(p, eticheta, seed, cale):
    eticheta = fara_emoji(eticheta)
    img = fundal(seed)
    d = ImageDraw.Draw(img, "RGBA")

    # eticheta de sus (tema zilei)
    d.text((W // 2, 92), eticheta.upper(), font=sans(30, 600), fill=AURIU, anchor="mm")
    separator(d, W // 2, 132, 220)

    # arcada cu produsul
    aw, ah = 660, 700
    ax, ay = (W - aw) // 2, 170
    # stralucire calda in spatele arcadei
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).rounded_rectangle([ax - 10, ay - 10, ax + aw + 10, ay + ah + 10], 60, fill=150)
    halo = halo.filter(ImageFilter.GaussianBlur(36))
    img.paste(Image.new("RGB", (W, H), AURIU), (0, 0), halo.point(lambda v: int(v * 0.35)))
    d = ImageDraw.Draw(img, "RGBA")
    contur_arcada(d, ax - 22, ay - 22, aw + 44, ah + 44, AURIU + (140,), 2)

    panou = Image.new("RGB", (aw, ah), (255, 255, 255))
    poza = descarca_poza(p.get("poza"))
    if poza:
        poza = ImageOps.fit(poza, (aw, ah), Image.LANCZOS, centering=(0.5, 0.45))
        panou.paste(poza, (0, 0))
    else:
        ImageDraw.Draw(panou).text((aw // 2, ah // 2), "Cadouri pe Buget", font=serif(64, 600),
                                   fill=AURIU_INCHIS, anchor="mm")
    img.paste(panou, (ax, ay), masca_arcada(aw, ah))
    contur_arcada(d, ax, ay, aw, ah, AURIU_DESCHIS, 5)

    # reducerea
    if p.get("discount", 0) >= 10:
        txt = f"-{p['discount']}%"
        f = sans(40, 700)
        lw = int(f.getlength(txt)) + 44
        bx, by = ax - 6, ay + aw // 2 - 40
        d.rounded_rectangle([bx, by, bx + lw, by + 62], 31, fill=(122, 36, 27), outline=AURIU_DESCHIS, width=2)
        d.text((bx + lw // 2, by + 31), txt, font=f, fill=AURIU_DESCHIS, anchor="mm")

    # numele produsului
    y = ay + ah + 64
    fn = serif(44, 500)
    for rand in rupe_randuri(p["nume"], fn, W - 170):
        d.text((W // 2, y), rand, font=fn, fill=CREM, anchor="mm")
        y += 54
    separator(d, W // 2, y + 4, 320)

    # pretul
    text_auriu(img, (W // 2, y + 72), f"{p['pret']} lei", serif(100, 600))
    d = ImageDraw.Draw(img, "RGBA")
    if p.get("discount", 0) >= 10:
        vechi = f"în loc de {round(p['pret'] / (1 - p['discount'] / 100))} lei"
        d.text((W // 2, y + 150), vechi, font=sans(28, 400), fill=GRI, anchor="mm")

    # chenarul subtire al imaginii
    d.rectangle([24, 24, W - 25, H - 25], outline=AURIU + (90,), width=2)
    d.text((W // 2, H - 58), "@cadouripebuget  ·  conține link de afiliere", font=sans(24, 400),
           fill=GRI, anchor="mm")

    cale.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(cale, "JPEG", quality=90, optimize=True, progressive=True)
    return cale


def main():
    if not POSTARE.exists():
        print("Nu exista idei/facebook_post.json - nimic de desenat.")
        return
    post = json.loads(POSTARE.read_text(encoding="utf-8"))
    produse = post.get("produse") or []
    if not produse:
        print("Postarea nu are date despre produse - raman pozele originale.")
        return
    tema = post.get("tema", "Ideea zilei")
    imagini = []
    for i, p in enumerate(produse, 1):
        eticheta = f"Top 5 · locul {i}" if len(produse) > 1 else tema
        try:
            cale = deseneaza(p, eticheta, f"{post.get('data')}-{i}", FOLDER / f"postare-{i}.jpg")
            imagini.append(str(cale))
            print(f"Desenat: {cale}")
        except Exception as e:   # o imagine stricata nu opreste postarea
            print(f"EROARE la desenarea imaginii {i}: {e}")
    if len(imagini) == len(produse):
        post["imagini"] = imagini
        POSTARE.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print("Nu toate imaginile au iesit - postarea foloseste pozele originale.")
        sys.exit(0)


if __name__ == "__main__":
    main()
