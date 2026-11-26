"""
Cadouri Bot - descarca feed-ul Profitshare, alege produsele bune de cadou
si scrie un fisier cu idei de postari pentru pagina de Instagram.

Ruleaza zilnic prin GitHub Actions. Link-ul feed-ului vine din secretul FEED_URL.
Poti pune mai multe feed-uri separate prin virgula sau linie noua.
"""

import csv
import io
import os
import random
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

# ---------------- SETARI (le poti modifica) ----------------
PRET_MIN = 30          # lei
PRET_MAX = 400         # lei
NR_IDEI = 10           # cate produse pe zi
DISCOUNT_MIN = 0       # % minim de reducere (0 = accepta si fara reducere)
FOLDER_IESIRE = Path("idei")
FISIER_ISTORIC = Path("istoric.txt")  # ca sa nu repete produse
ZILE_FARA_REPETARE = 30
# ------------------------------------------------------------


def norm(text: str) -> str:
    """lowercase, fara diacritice, fara spatii in plus"""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


# Numele coloanelor posibile (Profitshare foloseste nume in romana, uneori in engleza)
COLOANE = {
    "magazin": ["nume advertiser", "advertiser name", "advertiser"],
    "categorie": ["categorie", "category"],
    "nume": ["nume produs", "product name", "name", "title"],
    "descriere": ["descriere produs", "product description", "description"],
    "link": ["link afiliere produs", "affiliate link", "product affiliate link"],
    "imagine": ["imagine produs", "product image", "image"],
    "pret": ["pret cu tva", "price with vat", "price vat", "price"],
    "pret_redus": ["pret cu discount, cu tva", "price with discount, with vat",
                   "price discounted with vat", "discounted price with vat"],
    "cod": ["cod produs", "product code", "product id", "sku"],
    "stoc": ["disponibilitate", "availability"],
}


def gaseste_coloane(header):
    h = {norm(c): c for c in header}
    rezultat = {}
    for cheie, variante in COLOANE.items():
        for v in variante:
            if v in h:
                rezultat[cheie] = h[v]
                break
    return rezultat


def numar(val):
    if val is None:
        return None
    s = str(val).strip().replace(" ", "")
    if not s:
        return None
    # "1.234,56" -> 1234.56 ; "1234.56" ramane
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    s = re.sub(r"[^0-9.]", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def repara_link(url):
    url = (url or "").strip()
    return "https:" + url if url.startswith("//") else url


def descarca(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 cadouri-bot"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    for enc in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def citeste_csv(text):
    mostra = text[:5000]
    try:
        dialect = csv.Sniffer().sniff(mostra, delimiters=",;|\t")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def incarca_produse(urls):
    produse = []
    for url in urls:
        text = descarca(url)
        randuri = citeste_csv(text)
        if not randuri:
            print(f"Feed gol: {url[:50]}...")
            continue
        col = gaseste_coloane(randuri[0].keys())
        print("Coloane gasite:", col)
        lipsa = [k for k in ("nume", "link", "pret") if k not in col]
        if lipsa:
            print("ATENTIE: lipsesc coloanele", lipsa, "| header:", list(randuri[0].keys()))
            continue
        for r in randuri:
            pret = numar(r.get(col["pret"]))
            redus = numar(r.get(col.get("pret_redus", ""), None)) if "pret_redus" in col else None
            if redus and pret and redus < pret:
                pret_final, discount = redus, round((1 - redus / pret) * 100)
            else:
                pret_final, discount = pret, 0
            produse.append({
                "magazin": r.get(col.get("magazin", ""), "") if "magazin" in col else "",
                "categorie": r.get(col.get("categorie", ""), "") if "categorie" in col else "",
                "nume": (r.get(col["nume"]) or "").strip(),
                "descriere": r.get(col.get("descriere", ""), "") if "descriere" in col else "",
                "link": repara_link(r.get(col["link"])),
                "imagine": r.get(col.get("imagine", ""), "") if "imagine" in col else "",
                "pret_vechi": pret,
                "pret": pret_final,
                "discount": discount,
                "cod": r.get(col.get("cod", ""), "") if "cod" in col else "",
            })
    return produse


# Cuvinte care arata ca produsul e potrivit / nepotrivit pentru cadou
BUN_DE_CADOU = ["cadou", "gift", "set", "kit", "lampa", "lampă", "puzzle", "joc", "cana", "cană",
                "personalizat", "decor", "lumina", "led", "gadget", "breloc", "ceas", "parfum",
                "cutie", "box", "proiector", "difuzor", "aroma", "plus", "plush", "lego", "mini"]
EXCLUDE = ["piesa schimb", "piesă", "cablu", "adaptor", "filtru", "garantie", "garanție",
           "rezerva", "rezervă", "baterie de schimb", "surub", "șurub"]


def scor(p):
    n = norm(p["nume"] + " " + p["categorie"])
    s = p["discount"] * 1.5
    s += sum(8 for w in BUN_DE_CADOU if norm(w) in n)
    s -= sum(50 for w in EXCLUDE if norm(w) in n)
    if p["imagine"]:
        s += 5
    s += random.random() * 10  # putina varietate de la o zi la alta
    return s


def incarca_istoric():
    if not FISIER_ISTORIC.exists():
        return {}
    ist = {}
    for linie in FISIER_ISTORIC.read_text(encoding="utf-8").splitlines():
        if "|" in linie:
            d, k = linie.split("|", 1)
            ist[k] = d
    return ist


def salveaza_istoric(ist):
    azi = date.today()
    pastrate = {k: d for k, d in ist.items()
                if (azi - date.fromisoformat(d)).days <= ZILE_FARA_REPETARE}
    FISIER_ISTORIC.write_text("\n".join(f"{d}|{k}" for k, d in sorted(pastrate.items())) + "\n",
                              encoding="utf-8")


def caption(p):
    pret = f"{p['pret']:.0f} lei"
    if p["discount"] >= 10:
        oferta = f"Acum la {pret} (redus cu {p['discount']}% de la {p['pret_vechi']:.0f} lei)."
    else:
        oferta = f"Costă {pret}."
    deschideri = [
        "Nu știi ce să-i iei? 🎁",
        "Idee de cadou care chiar se folosește 👇",
        "Cadou sub radar, efect garantat ✨",
        "Pentru cine are deja tot 😄",
    ]
    return (f"{random.choice(deschideri)}\n\n{p['nume']}\n{oferta}\n\n"
            f"Link în bio 🔗\n\n#ideicadouri #cadouri #cadou #cadouperfect #romania")


def main():
    urls = [u.strip() for u in re.split(r"[,\n]", os.environ.get("FEED_URL", "")) if u.strip()]
    if not urls:
        sys.exit("Lipseste secretul FEED_URL.")

    produse = incarca_produse(urls)
    print(f"Total produse in feed: {len(produse)}")

    istoric = incarca_istoric()
    candidati = [
        p for p in produse
        if p["link"] and p["pret"] and PRET_MIN <= p["pret"] <= PRET_MAX
        and p["discount"] >= DISCOUNT_MIN
        and (p["cod"] or p["nume"]) not in istoric
        and not any(norm(w) in norm(p["nume"] + " " + p["categorie"]) for w in EXCLUDE)
    ]
    print(f"Candidati dupa filtre: {len(candidati)}")
    candidati.sort(key=scor, reverse=True)

    # maxim 4 produse de la acelasi magazin, ca sa fie variat
    alese, pe_magazin = [], {}
    for p in candidati:
        if pe_magazin.get(p["magazin"], 0) >= 4:
            continue
        alese.append(p)
        pe_magazin[p["magazin"]] = pe_magazin.get(p["magazin"], 0) + 1
        if len(alese) >= NR_IDEI:
            break

    if not alese:
        print("Niciun produs nou azi - pastrez fisierul existent.")
        return

    azi = date.today().isoformat()
    FOLDER_IESIRE.mkdir(exist_ok=True)
    linii = [f"# Idei de cadouri - {azi}\n",
             f"{len(alese)} produse alese din {len(produse)} (pret {PRET_MIN}-{PRET_MAX} lei).\n"]
    for i, p in enumerate(alese, 1):
        reducere = f" · **-{p['discount']}%**" if p["discount"] else ""
        linii += [
            f"\n---\n\n## {i}. {p['nume']}\n",
            f"**{p['pret']:.0f} lei**{reducere} · {p['magazin']} · {p['categorie']}\n",
            f"\n![poza]({p['imagine']})\n" if p["imagine"] else "",
            f"\n🔗 Link afiliat: {p['link']}\n",
            f"\n**Caption propus:**\n\n```\n{caption(p)}\n```\n",
        ]
        istoric[p["cod"] or p["nume"]] = azi

    (FOLDER_IESIRE / f"{azi}.md").write_text("".join(linii), encoding="utf-8")
    (FOLDER_IESIRE / "AZI.md").write_text("".join(linii), encoding="utf-8")
    salveaza_istoric(istoric)
    print(f"Scris: idei/{azi}.md")


if __name__ == "__main__":
    main()
