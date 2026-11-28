"""
Verifica zilnic linkurile de afiliere (Profitshare + 2Performant) de pe:
  - ghiduri (produsele puse de mana, ex. Perfectbijoux, si cele din feed),
  - prima pagina (linkurile eMAG + cele 10 idei din idei/AZI.md),
  - listele de pe Systeme (cadouripebuget.systeme.io/cadouri), unde sunt linkurile 2Performant.

Ca sa NU umflam statisticile cu clickuri false, nu intram pe linkurile de afiliere:
verificam direct pagina magazinului (destinatia). Destinatia o luam din parametrul
redirect= / redirect_to= sau, pentru linkurile scurte l.profitshare.ro/l/ID, dintr-un cache
(idei/linkuri.json). Un link scurt nou e "deschis" o singura data, ca sa-i aflam destinatia.
Lunea verificam si ca linkurile scurte Profitshare sunt inca active.

Rezultat:
  idei/linkuri.json  - starea fiecarui link (folosita de ghiduri.py: ascunde produsele disparute,
                       actualizeaza pretul la produsele puse de mana)
  idei/linkuri.md    - raportul zilei
  idei/FACEBOOK.md   - primeste un avertisment sus, DOAR daca ceva e stricat

Rulare: python linkuri.py [--complet]   (in zilnic.yml, dupa generarea postarii)
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

STARE = Path("idei/linkuri.json")
RAPORT = Path("idei/linkuri.md")
FACEBOOK = Path("idei/FACEBOOK.md")
AZI_MD = Path("idei/AZI.md")
LISTE_SYSTEME = ["https://cadouripebuget.systeme.io/cadouri"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PAUZA = 0.7  # secunde intre cereri, ca sa nu incarcam magazinele

# destinatii aflate pe 28 nov. 2026 (ca sa nu deschidem linkurile scurte deloc)
DESTINATII_CUNOSCUTE = {
    "https://l.profitshare.ro/l/17309362": "https://www.perfectbijoux.ro/cumpara/inel-tennis-luciana-7750291",
    "https://l.profitshare.ro/l/17309366": "https://www.perfectbijoux.ro/cumpara/cercei-cu-perle-mira-7750304",
    "https://l.profitshare.ro/l/17519393": "https://www.perfectbijoux.ro/cumpara/cercei-in-forma-de-floare-cu-cristale-albe-floris-7750633",
    "https://l.profitshare.ro/l/17309368": "https://www.perfectbijoux.ro/cumpara/colier-albastru-vanessa-placat-cu-aur-roz-7754733",
    "https://l.profitshare.ro/l/17519396": "https://www.perfectbijoux.ro/cumpara/pandantiv-auriu-cu-cristale-multicolore-helena-cu-lantisor-7754767",
    "https://l.profitshare.ro/l/17519394": "https://www.perfectbijoux.ro/cumpara/cercei-lungi-cu-perle-marlene-7750346",
    "https://l.profitshare.ro/l/17519395": "https://www.perfectbijoux.ro/cumpara/inel-cu-piatra-albastra-ag925-elena-7750352",
    "https://l.profitshare.ro/l/17585454": "https://www.emag.ro/search/cadouri+pentru+ea",
    "https://l.profitshare.ro/l/17585458": "https://www.emag.ro/search/cadouri+pentru+el",
    "https://l.profitshare.ro/l/17585459": "https://www.emag.ro/search/cadouri+copii",
    "https://l.profitshare.ro/l/17585460": "https://www.emag.ro/search/cadouri+mos+nicolae",
    "https://l.profitshare.ro/l/17585461": "https://www.emag.ro/search/cadouri+secret+santa",
    "https://l.profitshare.ro/l/17585462": "https://www.emag.ro/pachete-cosuri-cadou/c",
}
PARAMETRI_DE_SCOS = ("click_code", "emag_click_id", "ref", "utm_source", "utm_medium", "utm_campaign",
                     "utm_content", "utm_term", "gclid", "fbclid")
PROBLEME = ("stricat", "stoc", "inactiv")


# ---------- retea ----------

ULTIMA_CERERE = {}   # domeniu -> momentul ultimei cereri (nu bombardam acelasi magazin)
PAUZA_DOMENIU = 3.0


def cere(url, timeout=25, reincercare=True):
    """Intoarce (cod_http, url_final, text). Nu arunca exceptii."""
    dom = urllib.parse.urlsplit(url).netloc
    asteapta = ULTIMA_CERERE.get(dom, 0) + PAUZA_DOMENIU - time.time()
    if asteapta > 0:
        time.sleep(asteapta)
    ULTIMA_CERERE[dom] = time.time()
    rez = _cere(url, timeout)
    if rez[0] == 429 and reincercare:   # "prea multe cereri": mai incercam o data, dupa o pauza
        time.sleep(20)
        return cere(url, timeout, False)
    return rez


def _cere(url, timeout):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read(3_000_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as ex:
        try:
            corp = ex.read(500_000).decode("utf-8", "ignore")
        except Exception:
            corp = ""
        return ex.code, url, corp
    except Exception as ex:
        return 0, url, type(ex).__name__


def curata(url):
    p = urllib.parse.urlsplit(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True) if k not in PARAMETRI_DE_SCOS]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(q), ""))


def retea(link):
    return "2Performant" if "2performant" in link else ("Profitshare" if "profitshare" in link else "altul")


def destinatie(link, cache):
    """Pagina magazinului spre care duce linkul de afiliere (fara sa inregistram un click, daca se poate)."""
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)
    for k in ("redirect", "redirect_to", "url"):
        if q.get(k):
            return curata(q[k][0])
    if link in cache:
        return cache[link]
    if re.match(r"https?://l\.profitshare\.ro/l/\d+", link):
        # link scurt nou: il deschidem o singura data ca sa aflam destinatia, apoi o tinem minte
        _, _, t = cere(link)
        m = re.search(r"https://l\.profitshare\.ro/lr/[0-9a-f]+", t)
        if m:
            time.sleep(PAUZA)
            _, _, t2 = cere(m.group(0) + "?a=0&t=-1")
            s_ = re.search(r"setup\(([^)]*)\)", t2)
            urls = re.findall(r'"(https?:[^"]+)"', s_.group(1)) if s_ else []
            if urls:
                d = curata(urls[-1].replace("\\/", "/"))
                cache[link] = d
                return d
    return None


def link_scurt_activ(link):
    """Prima treapta a unui link l.profitshare.ro/l/ID (fara redirectul care numara clickul)."""
    cod, _, t = cere(link)
    return cod == 200 and "/lr/" in t


def pret_din_pagina(t):
    """Pretul din datele structurate (JSON-LD) ale produsului principal."""
    i = t.find('"@type":"Product"')
    if i < 0:
        i = t.find('"@type": "Product"')
    bucata = t[i:i + 6000] if i >= 0 else t
    m = re.search(r'"price"\s*:\s*"?([0-9]+(?:[.,][0-9]+)?)', bucata)
    if m:
        try:
            return float(m.group(1).replace(",", "."))
        except ValueError:
            return None
    return None


def verifica_pagina(url):
    cod, final, t = cere(url)
    rez = {"cod": cod}
    if cod in (404, 410):
        return {**rez, "stare": "stricat", "motiv": f"pagina nu mai există ({cod})"}
    if cod in (401, 403, 429, 503, 511):
        return {**rez, "stare": "blocat", "motiv": f"magazinul nu lasă verificarea automată ({cod})"}
    if cod == 0:
        return {**rez, "stare": "eroare", "motiv": f"nu răspunde ({t})"}
    if cod >= 400:
        return {**rez, "stare": "eroare", "motiv": f"eroare {cod}"}
    cale_veche = urllib.parse.urlsplit(url).path.strip("/")
    cale_noua = urllib.parse.urlsplit(final).path.strip("/")
    if cale_veche and not cale_noua:
        return {**rez, "stare": "stricat", "motiv": "trimite la prima pagină a magazinului (produs șters)"}
    stoc = re.findall(r'"availability"\s*:\s*"[^"]*?(InStock|OutOfStock|SoldOut|Discontinued|PreOrder|BackOrder|LimitedAvailability)', t)
    if stoc and not any(s in ("InStock", "LimitedAvailability", "PreOrder", "BackOrder") for s in stoc):
        return {**rez, "stare": "stoc", "motiv": "stoc epuizat"}
    return {**rez, "stare": "ok", "motiv": "", "pret": pret_din_pagina(t)}


# ---------- de unde luam linkurile ----------

def linkuri_site():
    """(link, nume, unde) din ghiduri, eMAG si ideile zilei."""
    out = []
    try:
        from ghiduri_continut import GHIDURI
        feed_refs = set()
        for g in GHIDURI:
            for s in g["sectiuni"]:
                for ref in s["produse"]:
                    if "manual" in ref:
                        m = g["manual"][ref["manual"]]
                        out.append((m["link"], m["nume"], f"ghid {g['slug']}"))
                    else:
                        feed_refs.add((ref["feed"], ref.get("nume", ""), g["slug"]))
            if g.get("emag"):
                out.append((g["emag"][1], g["emag"][0], f"ghid {g['slug']}"))
    except Exception as ex:
        print("Nu am putut citi ghidurile:", type(ex).__name__, ex)
        feed_refs = set()
    try:
        from pagina import EMAG
        out += [(l, f"eMAG {n}", "prima pagină") for n, l in EMAG]
    except Exception as ex:
        print("Nu am putut citi lista eMAG:", type(ex).__name__)
    if AZI_MD.exists():
        text = AZI_MD.read_text(encoding="utf-8")
        for titlu, link in re.findall(r"^## \d+\. (.+?)$.*?Link afiliat: (\S+)", text, flags=re.M | re.S):
            out.append((link, titlu, "ideile de azi"))
    return out, feed_refs


def linkuri_systeme():
    out = []
    for url in LISTE_SYSTEME:
        cod, _, t = cere(url)
        if cod != 200:
            print(f"Lista Systeme nu a raspuns ({cod}): {url}")
            continue
        for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', t, flags=re.S):
            href = html.unescape(href)
            if "profitshare" in href or "2performant" in href:
                nume = re.sub(r"<[^>]+>", " ", html.unescape(text))
                nume = re.sub(r"\s+", " ", nume).strip()[:80]
                out.append((href, nume, "listele Systeme"))
    return out


def sanatate_feed():
    """Cate produse are fiecare magazin in feed-uri (ca sa vedem daca un feed a cazut)."""
    try:
        from idei_cadouri import incarca_produse
    except Exception:
        return {}
    surse = os.environ.get("FEED_URL", "") + "," + os.environ.get("FEED_URL_2", "")
    urls = [u.strip() for u in re.split(r"[,\n]", surse) if u.strip()]
    if not urls:
        return {}
    numar = {}
    for p in incarca_produse(urls):
        cheie = (p.get("magazin") or "?").strip()
        numar[cheie] = numar.get(cheie, 0) + 1
    return numar


# ---------- main ----------

def main():
    complet = "--complet" in sys.argv or date.today().weekday() == 0  # lunea: verificare completa
    vechi = json.loads(STARE.read_text(encoding="utf-8")) if STARE.exists() else {}
    cache = {**DESTINATII_CUNOSCUTE, **vechi.get("destinatii", {})}
    rez_vechi = vechi.get("rezultate", {})

    intrari, _ = linkuri_site()
    intrari += linkuri_systeme()
    # grupam pe link (acelasi link poate aparea in mai multe locuri)
    linkuri = {}
    for link, nume, unde in intrari:
        if not link.startswith("http"):
            continue
        d = linkuri.setdefault(link, {"nume": nume, "unde": []})
        if unde not in d["unde"]:
            d["unde"].append(unde)

    verificate = {}   # destinatie -> rezultat (ca sa nu verificam de doua ori aceeasi pagina)
    rezultate = {}
    for link, info in linkuri.items():
        dest = destinatie(link, cache)
        nume = info["nume"]
        if dest and (not nume or nume.lower().startswith(("vezi", "cumpără", "cumpara", "link"))):
            # pe listele Systeme textul linkului e butonul ("Vezi pe 3Gifts →"); luam numele din adresa
            felie = urllib.parse.unquote(urllib.parse.urlsplit(dest).path.rstrip("/").split("/")[-1])
            felie = re.sub(r"\.html?$|-\d{5,}$", "", felie).replace("-", " ").strip()
            nume = felie[:1].upper() + felie[1:] if felie else nume
        r = {"nume": nume, "unde": info["unde"], "retea": retea(link), "dest": dest}
        if complet and re.match(r"https?://l\.profitshare\.ro/l/\d+", link):
            time.sleep(PAUZA)
            if not link_scurt_activ(link):
                rezultate[link] = {**r, "stare": "inactiv", "motiv": "linkul Profitshare nu mai e activ"}
                continue
        if not dest:
            if "ideile de azi" in info["unde"]:   # produs din feed: se actualizeaza singur zilnic
                rezultate[link] = {**r, "stare": "feed", "motiv": "produs din feed (se reîmprospătează zilnic)"}
            else:
                rezultate[link] = {**r, "stare": "necunoscut", "motiv": "nu am putut afla pagina magazinului"}
            continue
        if dest not in verificate:
            verificate[dest] = verifica_pagina(dest)
        r.update(verificate[dest])
        # o eroare de retea nu e o problema decat daca se repeta 3 zile la rand
        zile = (rez_vechi.get(link, {}).get("zile_eroare", 0) + 1) if r["stare"] == "eroare" else 0
        r["zile_eroare"] = zile
        rezultate[link] = r

    feed = {}
    try:
        feed = sanatate_feed() or {}
    except Exception as ex:
        print("Nu am putut numara produsele din feed:", type(ex).__name__)
    feed_vechi = vechi.get("feed", {})
    probleme_feed = []
    for mag, n in feed_vechi.items():
        acum = feed.get(mag, 0)
        if feed and (acum == 0 or acum < n * 0.4):
            probleme_feed.append(f"{mag}: {n} → {acum} produse")

    azi = date.today().isoformat()
    STARE.write_text(json.dumps({"actualizat": azi, "destinatii": cache, "rezultate": rezultate,
                                 "feed": feed or feed_vechi}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- raport ----------
    probleme = [(l, r) for l, r in rezultate.items()
                if r["stare"] in PROBLEME or (r["stare"] == "eroare" and r.get("zile_eroare", 0) >= 3)]
    pe_stari = {}
    for r in rezultate.values():
        pe_stari[r["stare"]] = pe_stari.get(r["stare"], 0) + 1
    pe_retele = {}
    for r in rezultate.values():
        x = pe_retele.setdefault(r["retea"], [0, 0])
        x[0] += 1
        x[1] += r["stare"] in PROBLEME
    rand = [f"# Verificarea linkurilor de afiliere – {azi}", "",
            f"Verificate: **{len(rezultate)} linkuri** ({'complet, inclusiv linkurile scurte' if complet else 'paginile magazinelor'}).",
            "", "| Rețea | Linkuri | Cu probleme |", "|---|---|---|"]
    rand += [f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(pe_retele.items())]
    rand += ["", "Stări: " + ", ".join(f"{k} {v}" for k, v in sorted(pe_stari.items())), ""]
    if probleme:
        rand += [f"## ⚠️ De rezolvat ({len(probleme)})", ""]
        for l, r in probleme:
            rand.append(f"- **{r['nume'] or r.get('dest') or l}** ({r['retea']}, în: {', '.join(r['unde'])}) – {r['motiv']}  ")
            rand.append(f"  {r.get('dest') or l}")
        rand.append("")
        rand.append("Produsele puse de mână în ghiduri care au dispărut sau nu mai sunt pe stoc sunt ascunse automat. "
                    "Pe listele Systeme trebuie înlocuite de mână.")
    else:
        rand += ["## ✅ Toate linkurile verificate sunt în regulă", ""]
    if probleme_feed:
        rand += ["", "## ⚠️ Feed-uri care par căzute", ""] + [f"- {x}" for x in probleme_feed]
    if feed:
        rand += ["", "## Produse în feed-uri, pe magazine", ""] + [f"- {k}: {v}" for k, v in sorted(feed.items())]
    blocate = [r for r in rezultate.values() if r["stare"] in ("blocat", "necunoscut")]
    if blocate:
        domenii = sorted({urllib.parse.urlsplit(r.get("dest") or "").netloc.replace("www.", "") or "?" for r in blocate})
        rand += ["", f"_Nu s-au putut verifica automat {len(blocate)} linkuri ({', '.join(domenii)} blochează roboții). "
                 f"Pentru ele, lunea verific doar că linkul de afiliere e încă activ._"]
    RAPORT.write_text("\n".join(rand) + "\n", encoding="utf-8")
    print(f"Linkuri verificate: {len(rezultate)} | probleme: {len(probleme)} | feed-uri cazute: {len(probleme_feed)}")

    # ---------- avertisment in FACEBOOK.md (il vezi dimineata de pe telefon) ----------
    if (probleme or probleme_feed) and FACEBOOK.exists():
        fb = FACEBOOK.read_text(encoding="utf-8")
        if "## ⚠️ Linkuri de verificat" not in fb:
            avert = [f"## ⚠️ Linkuri de verificat ({len(probleme) + len(probleme_feed)})", ""]
            avert += [f"- {r['nume'] or r.get('dest')} – {r['motiv']} (în: {', '.join(r['unde'])})" for _, r in probleme[:10]]
            avert += [f"- Feed: {x}" for x in probleme_feed]
            avert += ["", "Detalii: idei/linkuri.md", "", "---", ""]
            linii = fb.split("\n", 1)
            fb = linii[0] + "\n\n" + "\n".join(avert) + (linii[1] if len(linii) > 1 else "")
            FACEBOOK.write_text(fb, encoding="utf-8")


if __name__ == "__main__":
    main()
