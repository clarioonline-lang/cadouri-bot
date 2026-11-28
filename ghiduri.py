"""
Genereaza blogul de ghiduri: site/ghiduri/<slug>.html, site/ghiduri/index.html,
site/sitemap.xml si site/robots.txt.

Textele sunt in ghiduri_continut.py. Pretul, poza si linkul produselor "feed" se iau zilnic din
feed-urile de afiliere (secretele FEED_URL si FEED_URL_2), deci ghidurile au mereu preturi la zi.
Un produs care nu mai apare in feed nu mai e afisat. Daca feed-urile nu se pot citi deloc,
ghidurile existente nu se suprascriu.

Rulare: python ghiduri.py   (in pagina.yml, dupa pagina.py)
"""

import html
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from ghiduri_continut import GHIDURI

SITE = "https://cadouripebuget.online"
IESIRE = Path("site")
LUNI = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august",
        "septembrie", "octombrie", "noiembrie", "decembrie"]


def e(t):
    return html.escape(str(t or ""), quote=True)


def data_ro(iso):
    a, l, z = (int(x) for x in iso.split("-"))
    return f"{z} {LUNI[l - 1]} {a}"


def incarca_feeduri():
    from idei_cadouri import incarca_produse
    surse = os.environ.get("FEED_URL", "") + "," + os.environ.get("FEED_URL_2", "")
    urls = [u.strip() for u in re.split(r"[,\n]", surse) if u.strip()]
    if not urls:
        return None
    produse = incarca_produse(urls)
    index = {}
    for p in produse:
        index[(p["magazin"].strip(), str(p["cod"]).strip())] = p
    return index


def _stare_linkuri():
    """Rezultatul verificarii de dimineata (linkuri.py): ce produse au disparut, preturi la zi."""
    try:
        return json.loads(Path("idei/linkuri.json").read_text(encoding="utf-8")).get("rezultate", {})
    except Exception:
        return {}


STARE_LINKURI = _stare_linkuri()


def produs_card(ref, ghid, feed, azi_txt):
    """Intoarce (html, date_pentru_schema) sau (None, None) daca produsul nu mai e disponibil."""
    if "feed" in ref:
        p = (feed or {}).get(ref["feed"])
        if not p or not p.get("link", "").startswith("http"):
            return None, None
        if ghid.get("pret_max") and p["pret"] > ghid["pret_max"]:
            return None, None  # s-a scumpit peste bugetul din titlu
        if STARE_LINKURI.get(p["link"], {}).get("stare") in ("stricat", "stoc", "inactiv"):
            return None, None  # pagina produsului a disparut sau nu mai e pe stoc
        nume, magazin = ref.get("nume") or p["nume"], p["magazin"].replace(".ro", "").replace(".com", "")
        pret, pret_vechi, link, poza = p["pret"], (p["pret_vechi"] if p["discount"] >= 5 else None), p["link"], p.get("imagine", "")
        nota = f"Preț actualizat azi, {azi_txt}"
    else:
        m = ghid["manual"][ref["manual"]]
        nume, magazin, pret, pret_vechi, link, poza = m["nume"], m["magazin"], m["pret"], m.get("pret_vechi"), m["link"], m["poza"]
        nota = f"Preț verificat pe {m['verificat']}"
        st = STARE_LINKURI.get(link, {})
        if st.get("stare") in ("stricat", "stoc", "inactiv"):
            return None, None  # produs pus de mana care a disparut / nu mai e pe stoc
        if st.get("stare") == "ok" and st.get("pret") and 0.3 * pret < st["pret"] < 3 * pret:
            pret = st["pret"]   # pretul citit azi-dimineata de pe pagina magazinului
            nota = f"Preț verificat azi, {azi_txt}"
            if pret_vechi and pret_vechi <= pret:
                pret_vechi = None
        if ghid.get("pret_max") and pret > ghid["pret_max"]:
            return None, None
    pret_txt = f"{pret:.0f}" if float(pret).is_integer() or pret >= 100 else f"{pret:.2f}".replace(".", ",")
    reducere = round((1 - pret / pret_vechi) * 100) if pret_vechi and pret_vechi > pret else 0
    insigna = f'<span class="insigna">−{reducere}%</span>' if reducere >= 5 else ""
    vechi = f'<span class="vechi">{pret_vechi:.0f} lei</span>' if reducere >= 5 else ""
    card = f"""
      <article class="produs">
        <a class="produs-poza" href="{e(link)}" target="_blank" rel="sponsored noopener">
          <img src="{e(poza)}" alt="{e(nume)}" loading="lazy">{insigna}
        </a>
        <div class="produs-text">
          <p class="magazin">{e(magazin)}</p>
          <h3>{e(nume)}</h3>
          <p>{ref['text']}</p>
          <div class="rand-pret"><span class="pret">{pret_txt} lei</span>{vechi}<span class="nota">{e(nota)}</span></div>
          <a class="buton" href="{e(link)}" target="_blank" rel="sponsored noopener">Vezi la {e(magazin)} →</a>
        </div>
      </article>"""
    return card, {"nume": nume, "link": link, "poza": poza, "pret": pret}


def pagina_ghid(g, feed, toate):
    azi = date.today()
    azi_txt = f"{azi.day} {LUNI[azi.month - 1]}"
    sectiuni_html, toc, schema_items, nr = [], [], [], 0
    for s in g["sectiuni"]:
        carduri = []
        for ref in s["produse"]:
            card, d = produs_card(ref, g, feed, azi_txt)
            if card:
                carduri.append(card)
                nr += 1
                schema_items.append(d)
        if not carduri:
            continue
        toc.append(f'<a href="#{s["id"]}">{e(s["titlu"])}</a>')
        sectiuni_html.append(f"""
    <section id="{s['id']}" class="sectiune">
      <h2>{e(s['titlu'])}</h2>
      <p class="subtitlu">{e(s['subtitlu'])}</p>
      {s['intro']}
      <div class="produse">{''.join(carduri)}
      </div>
    </section>""")

    utile = "".join(f"""
    <section id="{u['id']}" class="sectiune utila">
      <h2>{e(u['titlu'])}</h2>
      {u['html']}
    </section>""" for u in g["sectiuni_utile"])
    toc += [f'<a href="#{u["id"]}">{e(u["titlu"])}</a>' for u in g["sectiuni_utile"][:2]]

    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in g["faq"])
    biletele = json.dumps(g["biletele"], ensure_ascii=False)
    alte = [x for x in toate if x["slug"] != g["slug"]]
    alte_html = "".join(f'<a href="{x["slug"]}.html">{e(x["titlu_scurt"])} →</a>' for x in alte) or \
        '<p class="mic">Urmează: cadouri pentru el, Moș Nicolae sub 50 lei, Secret Santa și cadouri pentru copii.</p>'
    emag_txt, emag_link = g.get("emag", ("", ""))

    cuvinte = len(re.sub(r"<[^>]+>", " ", g["intro"] + "".join(s["intro"] + " ".join(p["text"] for p in s["produse"])
                                                               for s in g["sectiuni"]) + "".join(u["html"] for u in g["sectiuni_utile"])).split())
    minute = max(3, round(cuvinte / 200))
    url = f"{SITE}/ghiduri/{g['slug']}.html"
    poza_principala = schema_items[0]["poza"] if schema_items else ""
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": g["titlu"], "description": g["descriere"], "datePublished": g["publicat"],
             "dateModified": azi.isoformat(), "inLanguage": "ro", "mainEntityOfPage": url, "image": poza_principala,
             "author": {"@type": "Person", "name": "Lazar Eugen Grigore"},
             "publisher": {"@type": "Organization", "name": "Cadouri pe Buget", "url": SITE}},
            {"@type": "ItemList", "name": g["titlu_scurt"], "numberOfItems": len(schema_items),
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": d["nume"], "url": d["link"]}
                                 for i, d in enumerate(schema_items)]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                                                 "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Cadouri pe Buget", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Ghiduri", "item": SITE + "/ghiduri/"},
                {"@type": "ListItem", "position": 3, "name": g["titlu_scurt"], "item": url}]},
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(g['titlu_seo'])}</title>
<meta name="description" content="{e(g['descriere'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(g['titlu_seo'])}">
<meta property="og:description" content="{e(g['descriere'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{e(poza_principala)}">
<meta property="og:locale" content="ro_RO">
<meta name="theme-color" content="#f7f1e8">
<link rel="stylesheet" href="/ghid.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
<header class="sus"><div class="zona-lata">
  <a class="logo" href="/">Cadouri <i>pe</i> Buget</a>
  <nav><a href="/">Ideile de azi</a><a href="/ghiduri/">Ghiduri</a><a href="/#emag">eMAG</a></nav>
</div></header>

<main>
  <div class="zona cap">
    <p class="fir"><a href="/">Acasă</a> › <a href="/ghiduri/">Ghiduri</a> › {e(g['eticheta'])}</p>
    <p class="supra">{e(g['eticheta'])} · {minute} minute de citit · actualizat {azi_txt}</p>
    <h1>{e(g['titlu'])}</h1>
    <p class="marcaj">📢 #publicitate · Articolul conține linkuri de afiliere: dacă cumperi, primim un mic comision, fără cost în plus pentru tine. <a href="/informatii-legale.html#afiliere">Cum funcționează</a></p>
    <div class="intro">{g['intro']}</div>
  </div>

  <div class="zona">
    <nav class="test" aria-label="{e(g['test_titlu'])}">
      <p class="test-titlu">{e(g['test_titlu'])}</p>
      <div class="test-butoane">{''.join(toc[:len(sectiuni_html)])}</div>
      <p class="mic">Sau sari direct la: {' · '.join(toc[len(sectiuni_html):])}</p>
    </nav>
  </div>

  <div class="zona">{''.join(sectiuni_html)}

    <aside class="biletel" aria-live="polite">
      <p class="supra">Generatorul de bilețele</p>
      <h2>Nu știi ce să scrii pe bilet?</h2>
      <p id="biletel-text" class="biletel-text">„{e(g['biletele'][0])}”</p>
      <button type="button" id="biletel-buton">Dă-mi alt bilețel ✍️</button>
    </aside>
    {utile}

    <section class="sectiune emag-cutie">
      <h2>N-ai găsit ce căutai?</h2>
      <p>Mai sunt mii de idei pe eMAG, cu livrare rapidă și retur ușor.</p>
      <a class="buton mare" href="{e(emag_link)}" target="_blank" rel="sponsored noopener">{e(emag_txt)} →</a>
    </section>

    <section class="sectiune faq">
      <h2>Întrebări frecvente</h2>
      {faq}
    </section>

    <section class="sectiune final">
      <h2>Vrei idei noi în fiecare zi?</h2>
      <p>În fiecare dimineață alegem 10 cadouri reduse, verificate. Le găsești pe prima pagină și pe
      <a href="https://www.facebook.com/profile.php?id=61596931285889" target="_blank" rel="noopener">Facebook</a> și
      <a href="https://www.instagram.com/cadouripebuget/" target="_blank" rel="noopener">Instagram</a>.</p>
      <a class="buton mare" href="/">Vezi ideile de azi →</a>
      <div class="alte">{alte_html}</div>
    </section>
  </div>
</main>

<footer><div class="zona-lata">© {azi.year} Lazar Eugen Grigore, Sibiu · <a href="mailto:cadouripebuget@gmail.com">cadouripebuget@gmail.com</a> ·
<a href="/informatii-legale.html">Informații legale</a> · <a href="/confidentialitate.html">Confidențialitate</a></div></footer>
<script>
(function(){{
  var b = {biletele}, i = 0, t = document.getElementById("biletel-text");
  document.getElementById("biletel-buton").addEventListener("click", function(){{
    i = (i + 1 + Math.floor(Math.random() * (b.length - 1))) % b.length;
    t.textContent = "„" + b[i] + "”";
  }});
}})();
</script>
<script src="/cookie.js" defer></script>
</body>
</html>
""", nr


def pagina_index(ghiduri, carduri_info):
    carduri = "".join(f"""
    <a class="ghid-card" href="{g['slug']}.html">
      <img src="{e(carduri_info.get(g['slug'], ''))}" alt="" loading="lazy">
      <span class="supra">{e(g['eticheta'])}</span>
      <span class="ghid-titlu">{e(g['titlu_scurt'])}</span>
      <span class="ghid-desc">{e(g['descriere'])}</span>
    </a>""" for g in ghiduri)
    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ghiduri de cadouri pe buget – idei pe ocazii și persoane | Cadouri pe Buget</title>
<meta name="description" content="Ghiduri de cadouri pe buget: idei de Crăciun pentru ea, pentru el, pentru copii, Moș Nicolae și Secret Santa, cu prețuri actualizate zilnic.">
<link rel="canonical" href="{SITE}/ghiduri/">
<link rel="stylesheet" href="/ghid.css">
</head>
<body>
<header class="sus"><div class="zona-lata">
  <a class="logo" href="/">Cadouri <i>pe</i> Buget</a>
  <nav><a href="/">Ideile de azi</a><a href="/ghiduri/">Ghiduri</a><a href="/#emag">eMAG</a></nav>
</div></header>
<main class="zona cap">
  <p class="supra">Blog</p>
  <h1>Ghiduri de cadouri pe buget</h1>
  <p class="intro">Idei alese pe persoane și ocazii, cu sfaturi care chiar te ajută (și cu glume, ca să treacă timpul mai ușor).
  Prețurile se actualizează în fiecare zi.</p>
  <div class="ghiduri-lista">{carduri}
  </div>
</main>
<footer><div class="zona-lata">© {date.today().year} Lazar Eugen Grigore, Sibiu · <a href="/informatii-legale.html">Informații legale</a> · <a href="/confidentialitate.html">Confidențialitate</a></div></footer>
<script src="/cookie.js" defer></script>
</body>
</html>
"""


def sitemap(ghiduri):
    azi = date.today().isoformat()
    urls = [(f"{SITE}/", "daily", "1.0"), (f"{SITE}/ghiduri/", "weekly", "0.9")]
    urls += [(f"{SITE}/ghiduri/{g['slug']}.html", "daily", "0.8") for g in ghiduri]
    urls += [(f"{SITE}/informatii-legale.html", "yearly", "0.2"), (f"{SITE}/confidentialitate.html", "yearly", "0.2")]
    corp = "".join(f"<url><loc>{u}</loc><lastmod>{azi}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>"
                   for u, c, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{corp}</urlset>\n'


def main():
    feed = incarca_feeduri()
    if not feed:
        print("Feed-urile nu s-au putut citi - pastrez ghidurile existente.")
        if (IESIRE / "ghiduri").exists():
            return
    folder = IESIRE / "ghiduri"
    folder.mkdir(parents=True, exist_ok=True)
    poze = {}
    for g in GHIDURI:
        continut, nr = pagina_ghid(g, feed, GHIDURI)
        (folder / f"{g['slug']}.html").write_text(continut, encoding="utf-8")
        m = re.search(r'<meta property="og:image" content="([^"]*)"', continut)
        poze[g["slug"]] = html.unescape(m.group(1)) if m else ""
        print(f"Ghid: {g['slug']} ({nr} produse)")
    (folder / "index.html").write_text(pagina_index(GHIDURI, poze), encoding="utf-8")
    (IESIRE / "sitemap.xml").write_text(sitemap(GHIDURI), encoding="utf-8")
    (IESIRE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
