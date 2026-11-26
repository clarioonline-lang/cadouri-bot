"""
Pagina-vitrina Cadouri pe Buget: o pagina web simpla cu ideile zilei.

Citeste idei/AZI.md (cele 10 produse) si idei/facebook_post.json (ce s-a postat azi pe
Facebook) si scrie site/index.html. Workflow-ul pagina.yml o publica pe GitHub Pages:
https://clarioonline-lang.github.io/cadouri-bot/

Produsul postat azi pe Facebook apare primul, mare, ca cine vine de pe Messenger
sa-l gaseasca imediat.
"""

import html
import json
from datetime import date
from pathlib import Path

from facebook_post import citeste_idei

INTRARE = Path("idei/AZI.md")
POSTARE = Path("idei/facebook_post.json")
IESIRE = Path("site/index.html")

LUNI = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie",
        "august", "septembrie", "octombrie", "noiembrie", "decembrie"]


def e(text):
    return html.escape(str(text or ""), quote=True)


def card(p, mare=False):
    vechi = ""
    if p["discount"] >= 10:
        pret_vechi = round(p["pret"] / (1 - p["discount"] / 100))
        vechi = f'<span class="vechi">{pret_vechi} lei</span>'
    insigna = f'<span class="insigna">-{p["discount"]}%</span>' if p["discount"] >= 10 else ""
    poza = (f'<img src="{e(p["poza"])}" alt="{e(p["nume"])}" loading="lazy">'
            if p["poza"] else '<div class="fara-poza">🎁</div>')
    eticheta = '<div class="eticheta">⭐ Ideea zilei de pe Facebook</div>' if mare else ""
    return f"""
    <article class="card{' mare' if mare else ''}">
      {eticheta}
      <a class="poza" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">{poza}{insigna}</a>
      <div class="info">
        <h2>{e(p['nume'])}</h2>
        <p class="pret"><strong>{p['pret']} lei</strong> {vechi}</p>
        <p class="magazin">{e(p['magazin'])}</p>
        <a class="buton" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">Vezi produsul →</a>
      </div>
    </article>"""


def main():
    if not INTRARE.exists():
        print("Nu exista idei/AZI.md - nimic de facut.")
        return
    produse = citeste_idei(INTRARE.read_text(encoding="utf-8"))
    if not produse:
        print("Nu am gasit produse in AZI.md.")
        return

    # produsul postat azi pe Facebook, primul
    text_fb = ""
    if POSTARE.exists():
        text_fb = json.loads(POSTARE.read_text(encoding="utf-8")).get("text", "")
    vedete = [p for p in produse if p["nume"] and p["nume"] in text_fb]
    if len(vedete) == 1:
        produse = vedete + [p for p in produse if p is not vedete[0]]
        carduri = card(vedete[0], mare=True) + "".join(card(p) for p in produse[1:])
    else:   # duminica (album cu mai multe) sau fara postare: lista simpla
        carduri = "".join(card(p) for p in produse)

    azi = date.today()
    data = f"{azi.day} {LUNI[azi.month - 1]} {azi.year}"

    pagina = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cadouri pe Buget – ideile de azi</title>
<meta name="description" content="Idei de cadouri sub 400 lei, cu reduceri, alese în fiecare zi.">
<meta property="og:title" content="Cadouri pe Buget – ideile de azi">
<meta property="og:description" content="Idei de cadouri cu reduceri, alese în fiecare zi.">
<style>
  :root {{ --rosu:#d6336c; --rosu-inchis:#a61e4d; --fond:#fff8f3; --text:#2b2b2b; --gri:#6b6b6b; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
         background:var(--fond); color:var(--text); line-height:1.4; }}
  header {{ text-align:center; padding:28px 16px 12px; }}
  header h1 {{ margin:0; font-size:1.7rem; }}
  header p {{ margin:6px 0 0; color:var(--gri); }}
  main {{ max-width:980px; margin:0 auto; padding:12px 16px 32px;
         display:grid; gap:16px; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); }}
  .card {{ background:#fff; border-radius:16px; overflow:hidden;
          box-shadow:0 2px 10px rgba(0,0,0,.07); display:flex; flex-direction:column; }}
  .card.mare {{ grid-column:1/-1; border:2px solid var(--rosu); }}
  @media (min-width:640px) {{ .card.mare {{ flex-direction:row; }}
                               .card.mare .poza {{ flex:0 0 45%; }} }}
  .eticheta {{ background:var(--rosu); color:#fff; font-weight:600; font-size:.9rem;
              padding:6px 12px; }}
  @media (min-width:640px) {{ .card.mare .eticheta {{ display:none; }} }}
  .poza {{ position:relative; display:block; text-decoration:none; aspect-ratio:1/1; background:#f3ece6; }}
  .poza img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .fara-poza {{ height:100%; display:flex; align-items:center; justify-content:center; font-size:3rem; }}
  .insigna {{ position:absolute; top:10px; left:10px; background:var(--rosu); color:#fff;
             font-weight:700; padding:4px 8px; border-radius:8px; font-size:.9rem; }}
  .info {{ padding:14px; display:flex; flex-direction:column; gap:6px; flex:1; }}
  .card.mare .info {{ justify-content:center; padding:20px; }}
  .card.mare .buton {{ margin-top:12px; }}
  .card.mare .info::before {{ content:"⭐ Ideea zilei de pe Facebook"; color:var(--rosu);
                              font-weight:600; font-size:.9rem; }}
  @media (max-width:639px) {{ .card.mare .info::before {{ content:none; }} }}
  h2 {{ font-size:1rem; margin:0; }}
  .card.mare h2 {{ font-size:1.3rem; }}
  .pret {{ margin:0; font-size:1.15rem; }}
  .vechi {{ color:var(--gri); text-decoration:line-through; font-size:.9rem; margin-left:6px; }}
  .magazin {{ margin:0; color:var(--gri); font-size:.85rem; }}
  .buton {{ margin-top:auto; text-align:center; background:var(--rosu); color:#fff;
           text-decoration:none; font-weight:600; padding:11px; border-radius:10px; }}
  .buton:hover, .buton:focus {{ background:var(--rosu-inchis); }}
  footer {{ text-align:center; color:var(--gri); font-size:.8rem; padding:0 16px 32px; max-width:640px; margin:0 auto; }}
  footer a {{ color:var(--rosu-inchis); }}
</style>
</head>
<body>
<header>
  <h1>🎁 Cadouri pe Buget</h1>
  <p>Ideile de azi · {data} · prețuri verificate dimineața</p>
</header>
<main>{carduri}
</main>
<footer>
  <p>O idee nouă în fiecare zi pe pagina noastră de Facebook. Prețurile și stocul se pot schimba
  în timpul zilei, verifică pe site-ul magazinului.</p>
  <p>Link-urile sunt de afiliere: dacă cumperi, primim un mic comision, fără costuri în plus pentru tine.</p>
</footer>
</body>
</html>
"""
    IESIRE.parent.mkdir(exist_ok=True)
    IESIRE.write_text(pagina, encoding="utf-8")
    print(f"Scris: {IESIRE} ({len(produse)} produse)")


if __name__ == "__main__":
    main()
