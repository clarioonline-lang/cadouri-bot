"""
Facebook - transforma ideile zilei (idei/AZI.md) intr-o postare de Facebook.

Scrie idei/FACEBOOK.md cu:
  - tema zilei + produsul ales (cu poza de descarcat)
  - textul postarii FARA link (Facebook limiteaza paginile la cateva link-uri pe luna)
  - mesajul de trimis pe Messenger celor care comenteaza "CADOU" (aici e link-ul)
  - duminica: album "Top 5 sub 100 lei"; in decembrie: serii de Mos Nicolae si Craciun
  - in unele zile: o intrebare pentru comunitate (postare fara produs)

Ruleaza dupa idei_cadouri.py. Nu are nevoie de setari sau secrete.
"""

import json
import random
import re
import unicodedata
from datetime import date
from pathlib import Path

FOLDER = Path("idei")
INTRARE = FOLDER / "AZI.md"
IESIRE = FOLDER / "FACEBOOK.md"
IESIRE_JSON = FOLDER / "facebook_post.json"  # citit de post_facebook.py
CUVANT_CHEIE = "CADOU"          # ce scriu oamenii in comentarii
ORA_POSTARE = "automat, ~06:00"  # botul posteaza singur

# Tema pe zile (0 = luni ... 6 = duminica)
TEME = {
    0: ("Cadouri sub 50 lei", None, 50),
    1: ("Pentru ea", ["ea", "femei", "dama", "bijuter", "bratara", "colier", "cercei",
                      "manichiura", "parfum", "cosmetic", "fata", "ten", "spa", "lumanare",
                      "cana", "beauty", "rujuri", "machiaj"], None),
    2: ("Pentru el", ["barbat", "el ", "tata", "whisky", "bere", "gadget", "carti de joc",
                      "portofel", "ceas", "brichet", "unelte", "cool", "black", "gentleman"], None),
    3: ("Gadgeturi și idei trăsnite", ["gadget", "led", "lampa", "proiector", "difuzor",
                                       "usb", "smart", "lumina", "mini", "aparat"], None),
    4: ("Cea mai mare reducere a săptămânii", None, None),
    5: ("Pentru copii", ["copii", "copil", "jucar", "joc", "puzzle", "lego", "plus", "plush",
                         "desen", "colorat", "baieti", "fete"], None),
    6: ("Top 5 sub 100 lei", None, 100),
}

INTREBARI = {
    2: "Care a fost cel mai ciudat cadou pe care l-ai primit vreodată? 😅 Scrie-ne mai jos!",
    5: "Buget de cadouri anul ăsta: 50, 100 sau 200 lei de persoană? Votează în comentarii 👇",
}


def norm(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def citeste_idei(text):
    """Extrage produsele din AZI.md (formatul scris de idei_cadouri.py)."""
    produse = []
    for bloc in re.split(r"\n---\n", text):
        titlu = re.search(r"^## \d+\. (.+)$", bloc, re.M)
        link = re.search(r"Link afiliat: (\S+)", bloc)
        pret = re.search(r"^\*\*(\d+) lei\*\*(.*)$", bloc, re.M)
        if not (titlu and link and pret):
            continue
        rest = pret.group(2)
        disc = re.search(r"-(\d+)%", rest)
        parti = [x.strip(" *") for x in rest.split("·") if x.strip(" *") and "%" not in x]
        poza = re.search(r"!\[[^\]]*\]\((\S+)\)", bloc)
        produse.append({
            "nume": titlu.group(1).strip(),
            "pret": int(pret.group(1)),
            "discount": int(disc.group(1)) if disc else 0,
            "magazin": parti[0] if parti else "",
            "categorie": parti[1] if len(parti) > 1 else "",
            "poza": poza.group(1) if poza else "",
            "link": link.group(1),
        })
    return produse


def alege(produse, cuvinte, pret_max):
    pool = [p for p in produse if pret_max is None or p["pret"] <= pret_max] or produse
    if cuvinte:
        potrivite = [p for p in pool
                     if any(norm(c) in " " + norm(p["nume"] + " " + p["categorie"]) + " "
                            for c in cuvinte)]
        pool = potrivite or pool
    # cu poza si cu reducere mare, primele
    return sorted(pool, key=lambda p: (bool(p["poza"]), p["discount"]), reverse=True)


def oferta(p):
    if p["discount"] >= 10:
        vechi = round(p["pret"] / (1 - p["discount"] / 100))
        return f"💸 {p['pret']} lei în loc de ~{vechi} lei (-{p['discount']}%)"
    return f"💸 {p['pret']} lei"


def tema_sezon(azi):
    if azi.month == 12 and 1 <= azi.day <= 5:
        return ("Cadouri pentru ghete 👢 (Moș Nicolae)", None, 100,
                f"Mai sunt {6 - azi.day} zile până vine Moș Nicolae! 👢")
    if azi.month == 12 and 10 <= azi.day <= 23:
        return ("Numărătoare inversă de Crăciun 🎄", None, None,
                f"🎄 Mai sunt {25 - azi.day} zile până la Crăciun!")
    return None


def postare_produs(p, intro):
    return (f"{intro}\n\n"
            f"🎁 {p['nume']}\n"
            f"{oferta(p)}\n\n"
            f"Vrei link-ul? Scrie {CUVANT_CHEIE} în comentarii și ți-l trimit pe Messenger 📩\n\n"
            f"Urmărește pagina pentru o idee nouă în fiecare zi 🔔\n\n"
            f"#cadouripebuget #ideicadouri #cadouri #afiliere")


def mesaj_messenger(lista):
    linii = ["Salut! 🎁 Uite link-ul:" if len(lista) == 1 else "Salut! 🎁 Uite link-urile:"]
    for p in lista:
        linii.append(f"• {p['nume']} – {p['pret']} lei: {p['link']}")
    linii.append("\n(Link de afiliere: dacă cumperi, primesc un mic comision, "
                 "fără costuri în plus pentru tine.)")
    return "\n".join(linii)


def main():
    if not INTRARE.exists():
        print("Nu exista idei/AZI.md - nimic de facut.")
        return
    produse = citeste_idei(INTRARE.read_text(encoding="utf-8"))
    if not produse:
        print("Nu am gasit produse in AZI.md.")
        return

    azi = date.today()
    zi = azi.weekday()
    sezon = tema_sezon(azi)
    if sezon:
        tema, cuvinte, pret_max, intro = sezon
    else:
        tema, cuvinte, pret_max = TEME[zi]
        intro = random.choice([
            f"Tema zilei: {tema} 👇",
            f"{tema}: ideea de azi ✨",
            f"Nu știi ce să cumperi? {tema} 🎁",
        ])
    ordonate = alege(produse, cuvinte, pret_max)

    out = [f"# Postare Facebook – {azi.isoformat()}\n",
           f"**Tema:** {tema} · **Postare:** {ORA_POSTARE}\n"]

    if zi == 6 and not sezon:
        top = ordonate[:5]
        text = ("🏆 Top 5 idei de cadouri sub 100 lei din săptămâna asta:\n\n"
                + "\n".join(f"{i}. {p['nume']} – {p['pret']} lei" for i, p in enumerate(top, 1))
                + f"\n\nCare îți place? Scrie numărul + {CUVANT_CHEIE} în comentarii și îți trimit"
                  " link-ul pe Messenger 📩\n\n#cadouripebuget #ideicadouri #top5 #afiliere")
        out += ["\n## Album cu 5 poze\n", "Salvează pozele de mai jos și pune-le într-o "
                "singură postare, în ordinea asta:\n"]
        for i, p in enumerate(top, 1):
            out.append(f"\n{i}. {p['nume']}" + (f"\n\n![poza {i}]({p['poza']})\n" if p["poza"]
                       else " – *fără poză în feed, fă o captură de pe site*\n"))
        de_postat = {"text": text, "poze": [p["poza"] for p in top if p["poza"]]}
        out += [f"\n## Textul postării (fără link)\n\n```\n{text}\n```\n",
                f"\n## Răspuns pe Messenger\n\n```\n{mesaj_messenger(top)}\n```\n"]
    else:
        p = ordonate[0]
        out += [f"\n## Produsul ales\n\n**{p['nume']}** · {p['pret']} lei"
                + (f" · -{p['discount']}%" if p["discount"] else "") + f" · {p['magazin']}\n"]
        out.append(f"\n![poza]({p['poza']})\n\nSalvează poza: apasă lung pe ea → Salvează.\n"
                   if p["poza"] else
                   "\n*Produsul nu are poză în feed: deschide link-ul și fă o captură de ecran.*\n")
        de_postat = {"text": postare_produs(p, intro), "poze": [p["poza"]] if p["poza"] else []}
        out += [f"\n## Textul postării (fără link)\n\n```\n{postare_produs(p, intro)}\n```\n",
                f"\n## Răspuns pe Messenger (celor care scriu {CUVANT_CHEIE})\n\n"
                f"```\n{mesaj_messenger([p])}\n```\n"]
        if len(ordonate) > 1:
            q = ordonate[1]
            out.append(f"\n## Rezervă (dacă primul nu-ți place)\n\n**{q['nume']}** · {q['pret']} lei"
                       + (f" · -{q['discount']}%" if q["discount"] else "")
                       + f"\n\n🔗 {q['link']}\n")

    if zi in INTREBARI:
        out.append(f"\n## Postare de interacțiune (opțional, seara, fără produs)\n\n"
                   f"```\n{INTREBARI[zi]}\n```\n")

    out.append("\n---\n*Nu pune link-ul în postare sau în comentarii: Facebook limitează "
               "paginile la câteva link-uri pe lună. Link-ul îl trimiți doar pe Messenger.*\n")

    de_postat["data"] = azi.isoformat()
    IESIRE_JSON.write_text(json.dumps(de_postat, ensure_ascii=False, indent=2), encoding="utf-8")
    IESIRE.write_text("".join(out), encoding="utf-8")
    print(f"Scris: {IESIRE}")


if __name__ == "__main__":
    main()
