"""
Caruselul zilnic pentru TikTok (Photo Mode): 10 imagini 1080x1920.
  1 = coperta ("Băieți, salvați asta" + tema + Partea N)
  2-9 = cate un produs (poza, nume, pret)
  10 = final (salvează, link în bio, #publicitate)

De ce: analiza din 28 nov. 2026 a cautarilor TikTok din Romania - merg postarile care
vorbesc direct cu cumparatorul ("Băieți, salvați asta"), seriile pe parti si listele
lungi pe care oamenii le salveaza.

Doi pasi:
  python tiktok_carusel.py alege      (zilnic.yml) alege produsele din feed, scrie
                                      idei/tiktok.json + sectiunea TikTok din FACEBOOK.md
  python tiktok_carusel.py deseneaza  (pagina.yml) deseneaza imaginile in site/tiktok/
                                      + pagina https://cadouripebuget.online/tiktok/
                                      (de acolo le salvezi pe telefon) + carusel.zip
"""

import html
import io
import json
import os
import random
import re
import sys
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AICI = Path(__file__).resolve().parent
FONTURI = AICI / "fonturi"
JSON = Path("idei/tiktok.json")
ISTORIC = Path("idei/tiktok_istoric.json")
FACEBOOK_MD = Path("idei/FACEBOOK.md")
SITE_DIR = Path("site/tiktok")
SITE = "https://cadouripebuget.online"
NR_PRODUSE = 8
ZILE_FARA_REPETARE = 21
MARCAJ = "📢 #publicitate · conține linkuri de afiliere"

W, H = 1080, 1920
NEGRU = (11, 8, 6)
VISINIU = (97, 28, 21)
VISINIU_BUTON = (122, 36, 27)
SMARALD = (24, 53, 33)
AURIU = (219, 166, 102)
AURIU_DESCHIS = (240, 200, 150)
CREM = (243, 230, 212)
GRI = (185, 168, 148)

CUVINTE_EA = ["femei", "dama", "bijuter", "bratar", "colier", "cercei", "inel", "manichiur",
              "parfum", "cosmetic", "fata", "ten", "spa", "lumanar", "beauty", "ruj", "machiaj",
              "geanta", "esarf", "pijama", "halat", "flori", "trandafir", "pandantiv", "oglind",
              "unghii", "par ", "ea ", "pentru ea", "mama", "iubita", "sotie"]
CUVINTE_EL = ["barbat", "tata", "whisky", "bere", "gadget", "carti de joc", "portofel", "ceas",
              "brichet", "unelte", "gentleman", "gamer", "sofer", "masina", "gratar", "bucatar",
              "barba", "sah", "pentru el", "iubit", "sot", "briceag", "multifunct", "bar ", "vin"]

# cuvinte care scot produsul din tema (un ceas de dama nu e cadou "pentru el")
NU_EL = ["dama", "femei", "bijuter", "cercei", "colier", "ruj", "machiaj", "unghii", "pentru ea", "fete"]
NU_EA = ["barbat", "barba", "pentru el", "baieti"]
# nu arata a cadou intr-un carusel (chiar daca trec de filtrul general)
NU_CADOU = ["pastile", "depozitare", "lunch box", "sticker", "termoizolant", "organizator", "suport conuri"]

# tema pe zile (0 = luni). kicker = cui ii vorbim; titlu = ce promitem.
TEME = {
    0: dict(cheie="ea100", kicker="Băieți, salvați asta", titlu="cadouri pentru ea sub 100 de lei",
            cuvinte=CUVINTE_EA, nu=NU_EA, pret=(30, 100), tag="#cadouripentruea"),
    1: dict(cheie="el150", kicker="Fete, salvați asta", titlu="cadouri pentru el sub 150 de lei",
            cuvinte=CUVINTE_EL, nu=NU_EL, pret=(30, 150), tag="#cadouripentruel"),
    2: dict(cheie="sub50", kicker="Secret Santa? Salvează asta", titlu="cadouri sub 50 de lei care nu par ieftine",
            cuvinte=None, pret=(20, 50), tag="#secretsanta"),
    3: dict(cheie="ea200", kicker="Băieți, salvați asta", titlu="cadouri pentru ea sub 200 de lei",
            cuvinte=CUVINTE_EA, nu=NU_EA, pret=(60, 200), tag="#cadouripentruea"),
    4: dict(cheie="redus", kicker="Salvează până nu se termină", titlu="cadouri reduse la jumătate de preț",
            cuvinte=None, pret=(30, 300), discount=40, tag="#reduceri"),
    5: dict(cheie="el100", kicker="Fete, salvați asta", titlu="cadouri pentru el sub 100 de lei",
            cuvinte=CUVINTE_EL, nu=NU_EL, pret=(30, 100), tag="#cadouripentruel"),
    6: dict(cheie="tot100", kicker="Pentru cine are deja tot", titlu="cadouri sub 100 de lei care chiar se folosesc",
            cuvinte=None, pret=(30, 100), tag="#ideidecadouri"),
}
MOS_NICOLAE = dict(cheie="mos50", kicker="Pentru ghetuță: salvează asta", titlu="cadouri de Moș Nicolae sub 50 de lei",
                   cuvinte=None, pret=(15, 50), tag="#mosnicolae")


def tema_zilei(azi):
    if azi.month == 12 and 1 <= azi.day <= 5:
        return MOS_NICOLAE
    return TEME[azi.weekday()]


# ---------------- alegerea produselor ----------------

def potriveste(text, cuvinte):
    """Cuvantul trebuie sa inceapa un cuvant din text (altfel 'ea' prinde 'cafea')."""
    t = " " + text + " "
    return any(re.search(r"(?<![a-z])" + re.escape(c.strip()), t) for c in cuvinte)


def nume_scurt(nume):
    """Numele din feed sunt lungi: pastram partea de inceput, fara coduri si detalii tehnice."""
    n = re.split(r"\s[-–|]\s|,|\(|\bcod\b", nume, maxsplit=1)[0]
    n = re.sub(r"\b[A-Z]{1,4}[\s-]?\d{2,}\b", "", n)          # coduri gen CR 2169
    n = re.sub(r"\s+", " ", n).strip(" -–")
    if len(n) > 60:
        n = n[:60].rsplit(" ", 1)[0] + "…"
    return n[:1].upper() + n[1:] if n else nume[:60]


def alege(produse, tema, istoric, norm, scor, exclude):
    azi = date.today()
    folosite = {k for k, d in istoric.get("folosite", {}).items()
                if (azi - date.fromisoformat(d)).days <= ZILE_FARA_REPETARE}
    lo, hi = tema["pret"]

    def candidati(cu_cuvinte):
        out = []
        for p in produse:
            if not p.get("imagine") or not p.get("link", "").startswith("http"):
                continue
            if not (lo <= p["pret"] <= hi):
                continue
            if p["discount"] < tema.get("discount", 0):
                continue
            n = norm(p["nume"] + " " + p["categorie"])
            if any(norm(w) in n for w in exclude):
                continue
            if any(w in n for w in NU_CADOU):
                continue
            if tema.get("nu") and potriveste(n, tema["nu"]):
                continue
            if cu_cuvinte and tema["cuvinte"] and not potriveste(n, [norm(c) for c in tema["cuvinte"]]):
                continue
            if f"{p['magazin']}|{p['cod']}" in folosite:
                continue
            out.append(p)
        return sorted(out, key=scor, reverse=True)

    lista = candidati(True)
    if len(lista) < NR_PRODUSE:                 # prea putine pe tema: completam fara filtrul de cuvinte
        lista += [p for p in candidati(False) if p not in lista]

    ales, pe_magazin, nume_vazute, primul_cuvant = [], {}, set(), {}
    for p in lista:
        if pe_magazin.get(p["magazin"], 0) >= 3:
            continue
        cheie_nume = " ".join(norm(p["nume"]).split()[:3])   # variante de culoare/marime = acelasi produs
        if cheie_nume in nume_vazute:
            continue
        pc = (norm(p["nume"]).split() or [""])[0]           # max 2 de acelasi fel (ex. 3 ceasuri)
        if primul_cuvant.get(pc, 0) >= 2:
            continue
        primul_cuvant[pc] = primul_cuvant.get(pc, 0) + 1
        ales.append(p)
        pe_magazin[p["magazin"]] = pe_magazin.get(p["magazin"], 0) + 1
        nume_vazute.add(cheie_nume)
        if len(ales) == NR_PRODUSE:
            break
    return sorted(ales, key=lambda p: p["pret"])   # de la ieftin la scump: te tine pana la final


def text_tiktok(tema, parte, produse):
    lista = "\n".join(f"{i}. {p['nume_scurt']} – {p['pret']:.0f} lei" for i, p in enumerate(produse, 1))
    tags = " ".join(dict.fromkeys([tema["tag"], "#ideidecadouri", "#cadouricraciun", "#cadouripebuget"]))
    return (f"{tema['kicker']} 📌 {len(produse)} {tema['titlu']} (Partea {parte})\n"
            f"{MARCAJ}\n\n{lista}\n\n"
            f"Pe care l-ai alege? Scrie în comentarii 👇\n"
            f"Link-urile sunt în bio 🔗 (prețuri de azi, se pot schimba)\n\n{tags}")


def pas_alege():
    sys.path.insert(0, str(AICI))
    import idei_cadouri as ic
    surse = os.environ.get("FEED_URL", "") + "," + os.environ.get("FEED_URL_2", "")
    urls = [u.strip() for u in re.split(r"[,\n]", surse) if u.strip()]
    if not urls:
        print("Lipsesc FEED_URL / FEED_URL_2: nu fac caruselul.")
        return
    produse = ic.incarca_produse(urls)
    for p in produse:
        p["magazin"] = (p.get("magazin") or "").strip()
        p["cod"] = str(p.get("cod") or "").strip()
    azi = date.today()
    tema = tema_zilei(azi)
    istoric = json.loads(ISTORIC.read_text(encoding="utf-8")) if ISTORIC.exists() else {}
    random.seed(azi.toordinal())
    ales = alege(produse, tema, istoric, ic.norm, ic.scor, ic.EXCLUDE)
    if len(ales) < 5:
        print(f"Prea putine produse pentru tema {tema['cheie']}: {len(ales)}. Nu fac caruselul azi.")
        return
    # aceeasi zi rulata de doua ori = aceeasi parte (nu sarim numere)
    parti = istoric.get("parti", {})
    if istoric.get("ultima_zi") == azi.isoformat() and istoric.get("ultima_tema") == tema["cheie"]:
        parte = parti.get(tema["cheie"], 1)
    else:
        parte = parti.get(tema["cheie"], 0) + 1
    parti[tema["cheie"]] = parte
    for p in ales:
        p["nume_scurt"] = nume_scurt(p["nume"])
    folosite = istoric.get("folosite", {})
    for p in ales:
        folosite[f"{p['magazin']}|{p['cod']}"] = azi.isoformat()
    folosite = {k: d for k, d in folosite.items() if (azi - date.fromisoformat(d)).days <= 60}
    ISTORIC.write_text(json.dumps({"parti": parti, "folosite": folosite, "ultima_zi": azi.isoformat(),
                                   "ultima_tema": tema["cheie"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    text = text_tiktok(tema, parte, ales)
    pastrat = ["nume", "nume_scurt", "pret", "pret_vechi", "discount", "imagine", "magazin", "link"]
    JSON.write_text(json.dumps({
        "data": azi.isoformat(), "tema": {k: v for k, v in tema.items() if k != "cuvinte"}, "parte": parte,
        "produse": [{k: p[k] for k in pastrat} for p in ales], "text": text,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    if FACEBOOK_MD.exists():
        fb = FACEBOOK_MD.read_text(encoding="utf-8")
        if "## TikTok (carusel)" not in fb:
            fb += (f"\n\n## TikTok (carusel)\n\nImaginile (10, în ordine): {SITE}/tiktok/ "
                   f"(după ~06:30; ține apăsat pe fiecare → Salvează)\n\nText:\n\n```\n{text}\n```\n\n"
                   f"La postare: „Afișează mai mult” → „Dezvăluie conținutul postării” → „Marca ta”. "
                   f"Adaugă un sunet popular din TikTok.\n")
            FACEBOOK_MD.write_text(fb, encoding="utf-8")
    print(f"Carusel TikTok: {tema['cheie']} partea {parte}, {len(ales)} produse.")


# ---------------- desen ----------------

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
    grad = Image.radial_gradient("L").resize((raza * 2, raza * 2))
    alfa = grad.point(lambda v: int(max(0.0, 1 - v / 128) ** 1.15 * 255 * intensitate))
    strat = Image.new("L", img.size, 0)
    strat.paste(alfa, (centru[0] - raza, centru[1] - raza))
    return Image.composite(Image.new("RGB", img.size, culoare), img, strat)


def fundal(seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), NEGRU)
    img = lumina(img, (60, 120), 1100, VISINIU, 0.95)
    img = lumina(img, (W - 40, H - 120), 1100, SMARALD, 0.9)
    strat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(strat)
    for _ in range(36):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(4, 22)
        d.ellipse([x - r, y - r, x + r, y + r], fill=AURIU_DESCHIS + (rnd.randint(25, 65),))
    strat = strat.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(img.convert("RGBA"), strat)


def centrat(d, text, f, y, fill):
    d.text((W / 2, y), text, font=f, fill=fill, anchor="mt")


def rupe(text, f, latime, maxim):
    cuv, randuri, r = text.split(), [], ""
    for c in cuv:
        t = (r + " " + c).strip()
        if f.getlength(t) <= latime:
            r = t
        else:
            randuri.append(r)
            r = c
    randuri.append(r)
    randuri = [x for x in randuri if x]
    if len(randuri) > maxim:
        randuri = randuri[:maxim]
        randuri[-1] = randuri[-1].rstrip(".,") + "…"
    return randuri


def fara_emoji(t):
    return " ".join("".join(c for c in t if ord(c) < 0x2600).split())


def descarca(url):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.8"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGB")
    except Exception as e:
        print(f"Nu am putut descarca poza: {type(e).__name__}")
        return None


def separator(d, y, lat=300):
    d.line([W / 2 - lat / 2, y, W / 2 - 16, y], fill=AURIU, width=2)
    d.line([W / 2 + 16, y, W / 2 + lat / 2, y], fill=AURIU, width=2)
    d.polygon([(W / 2, y - 8), (W / 2 + 8, y), (W / 2, y + 8), (W / 2 - 8, y)], fill=AURIU_DESCHIS)


def eticheta_sus(d, tema, i, total):
    t = f"{fara_emoji(tema['kicker']).upper()}  ·  {i}/{total}"
    centrat(d, t, sans(32, 600), 165, AURIU)


def slide_coperta(data, poze):
    tema, parte = data["tema"], data["parte"]
    img = fundal(1)
    d = ImageDraw.Draw(img)
    centrat(d, f"PARTEA {parte}", sans(40, 700), 300, AURIU)
    y = 400
    for r in rupe(fara_emoji(tema["kicker"]), serif(120, 700), 960, 2):
        centrat(d, r, serif(120, 700), y, CREM)
        y += 142
    separator(d, y + 40, 360)
    y += 110
    titlu = f"{len(data['produse'])} {tema['titlu']}"
    for r in rupe(titlu, serif(80, 600), 940, 3):
        centrat(d, r, serif(80, 600), y, AURIU_DESCHIS)
        y += 100
    # 4 poze mici, rotunde, pe un rand (miniatura arata produse reale)
    y += 60
    r = 105
    xs = [W / 2 - 3 * (r + 12) - 6, W / 2 - (r + 12) + 2, W / 2 + (r + 12) - 2, W / 2 + 3 * (r + 12) + 6]
    for cx, poza in zip(xs, [p for p in poze if p][:4]):
        mic = ImageOps.fit(poza, (2 * r, 2 * r))
        m = Image.new("L", (2 * r, 2 * r), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 2 * r, 2 * r], fill=255)
        img.paste(mic, (int(cx - r), int(y)), m)
        ImageDraw.Draw(img).ellipse([cx - r, y, cx + r, y + 2 * r], outline=AURIU, width=4)
    d = ImageDraw.Draw(img)
    centrat(d, "prețuri verificate azi  ·  link în bio", sans(36, 500), y + 2 * r + 50, GRI)
    return img


def slide_produs(data, p, poza, i, total):
    img = fundal(10 + i)
    d = ImageDraw.Draw(img)
    eticheta_sus(d, data["tema"], i + 1, total)
    # cardul cu poza
    cx0, cy0, cw, ch = 70, 240, 940, 940
    card = Image.new("RGB", (cw, ch), (250, 246, 240))
    if poza:
        poza = ImageOps.contain(poza, (cw - 60, ch - 60))
        card.paste(poza, ((cw - poza.width) // 2, (ch - poza.height) // 2))
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, ch], 44, fill=255)
    img.paste(card, (cx0, cy0), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx0 - 4, cy0 - 4, cx0 + cw + 4, cy0 + ch + 4], 48, outline=AURIU, width=4)
    # numarul
    nx, ny, r = cx0 + 20, cy0 + 20, 56
    d.ellipse([nx, ny, nx + 2 * r, ny + 2 * r], fill=VISINIU_BUTON, outline=AURIU, width=3)
    d.text((nx + r, ny + r), str(i), font=serif(64, 700), fill=CREM, anchor="mm")
    # reducerea
    if p["discount"] >= 10:
        t = f"-{p['discount']}%"
        f = sans(40, 700)
        lw = f.getlength(t) + 44
        d.rounded_rectangle([cx0 + cw - lw - 24, cy0 + 28, cx0 + cw - 24, cy0 + 96], 34, fill=VISINIU_BUTON)
        d.text((cx0 + cw - 24 - lw / 2, cy0 + 62), t, font=f, fill=CREM, anchor="mm")
    # nume + pret
    y = cy0 + ch + 60
    for r_ in rupe(fara_emoji(p["nume_scurt"]), serif(64, 600), 940, 2):
        centrat(d, r_, serif(64, 600), y, CREM)
        y += 80
    y += 18
    centrat(d, f"{p['pret']:.0f} lei", serif(140, 700), y, AURIU_DESCHIS)
    y += 175
    if p["discount"] >= 10:
        t = f"în loc de {p['pret_vechi']:.0f} lei"
        f = sans(36, 500)
        centrat(d, t, f, y, GRI)
        y += 56
    mag = re.sub(r"\.ro$", ".ro", p["magazin"]) if p["magazin"] else ""
    if mag:
        centrat(d, f"de pe {mag}", sans(32, 500), y, GRI)
    return img


def slide_final(data):
    img = fundal(99)
    d = ImageDraw.Draw(img)
    y = 520
    for r in ["Salvează", "ca să nu le pierzi"]:
        centrat(d, r, serif(96, 700), y, CREM)
        y += 120
    separator(d, y + 40)
    y += 110
    centrat(d, "Toate linkurile, cu prețul de azi:", sans(40, 500), y, CREM)
    y += 90
    bw = 520
    d.rounded_rectangle([W / 2 - bw / 2, y, W / 2 + bw / 2, y + 110], 55, fill=VISINIU_BUTON, outline=AURIU, width=3)
    d.text((W / 2, y + 55), "Link în bio", font=sans(50, 700), fill=CREM, anchor="mm")
    y += 200
    centrat(d, "Trimite-i asta cuiva care n-a luat", sans(38, 500), y, AURIU_DESCHIS)
    centrat(d, "încă niciun cadou", sans(38, 500), y + 54, AURIU_DESCHIS)
    centrat(d, "@cadouripebuget.online", sans(34, 600), y + 170, GRI)
    centrat(d, "#publicitate · conține linkuri de afiliere", sans(28, 500), y + 222, GRI)
    return img


def pas_deseneaza():
    if not JSON.exists():
        print("Nu exista idei/tiktok.json: niciun carusel azi.")
        return
    data = json.loads(JSON.read_text(encoding="utf-8"))
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for vechi in SITE_DIR.glob("*.jpg"):
        vechi.unlink()
    poze = [descarca(p["imagine"]) for p in data["produse"]]
    # unele magazine blocheaza serverele GitHub: fara poza, produsul iese din carusel (si din text)
    pastrate = [(p, poza) for p, poza in zip(data["produse"], poze) if poza]
    if len(pastrate) < len(data["produse"]):
        print(f"Fara poza: {len(data['produse']) - len(pastrate)} produse scoase din carusel.")
        data["produse"] = [p for p, _ in pastrate]
        poze = [poza for _, poza in pastrate]
        tema = dict(data["tema"])
        data["text"] = text_tiktok(tema, data["parte"], data["produse"])
    total = len(data["produse"]) + 2
    slides = [slide_coperta(data, poze)]
    slides += [slide_produs(data, p, poza, i, total) for i, (p, poza) in enumerate(zip(data["produse"], poze), 1)]
    slides.append(slide_final(data))
    nume = []
    for i, s in enumerate(slides, 1):
        n = f"{data['data']}-{i:02d}.jpg"
        s.convert("RGB").save(SITE_DIR / n, quality=90)
        nume.append(n)
    with zipfile.ZipFile(SITE_DIR / "carusel.zip", "w", zipfile.ZIP_STORED) as z:
        for n in nume:
            z.write(SITE_DIR / n, n)
    imgs = "\n".join(f'<figure><img src="{n}" alt="Imaginea {i}" loading="lazy"><figcaption>{i}/{len(nume)}</figcaption></figure>'
                     for i, n in enumerate(nume, 1))
    (SITE_DIR / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Carusel TikTok – {data['data']}</title>
<style>body{{margin:0;background:#160d0b;color:#f3e6d4;font-family:Arial,sans-serif;text-align:center}}
h1{{font-size:20px;margin:18px 12px 6px}}p{{margin:6px 16px;color:#cbb79c;font-size:15px}}
a.b{{display:inline-block;margin:10px;padding:12px 20px;border-radius:24px;background:#7a241b;color:#f3e6d4;text-decoration:none;font-weight:bold}}
figure{{margin:16px auto;max-width:420px}}img{{width:100%;border-radius:12px}}figcaption{{color:#dba666}}
textarea{{width:92%;max-width:420px;height:220px;background:#24140f;color:#f3e6d4;border:1px solid #dba666;border-radius:10px;padding:8px}}</style></head>
<body><h1>Carusel TikTok · {html.escape(data['tema']['kicker'])} · Partea {data['parte']}</h1>
<p>Pe telefon: ține apăsat pe fiecare imagine → Salvează. Încarcă-le în ordine (1 → {len(nume)}).</p>
<a class="b" href="carusel.zip" download>Descarcă toate (zip)</a>
<p>Textul postării:</p><textarea id="t" readonly>{html.escape(data['text'])}</textarea><br>
<a class="b" href="#" onclick="navigator.clipboard.writeText(document.getElementById('t').value);this.textContent='Copiat';return false">Copiază textul</a>
{imgs}
</body></html>""", encoding="utf-8")
    print(f"Carusel desenat: {len(nume)} imagini in {SITE_DIR}")


if __name__ == "__main__":
    pas = sys.argv[1] if len(sys.argv) > 1 else "alege"
    pas_deseneaza() if pas == "deseneaza" else pas_alege()
