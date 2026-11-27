"""
Pagina-vitrina Cadouri pe Buget: o pagina web cu ideile zilei.

Citeste idei/AZI.md (cele 10 produse) si idei/facebook_post.json (ce s-a postat azi pe
Facebook) si scrie site/index.html. Workflow-ul pagina.yml o publica pe GitHub Pages:
https://clarioonline-lang.github.io/cadouri-bot/

Stilul copiaza postarile de pe pagina de Facebook: fundal aproape negru, lumini
visinii si verzi, rame aurii subtiri, titluri serif aurii.

Produsul postat azi pe Facebook apare primul, mare, ca cine vine de pe Messenger
sa-l gaseasca imediat.

ATENTIE: eticheta <meta name='profitshareid'> valideaza site-ul in Profitshare - nu o sterge.
"""

import html
import json
from datetime import date
from pathlib import Path

from facebook_post import citeste_idei

INTRARE = Path("idei/AZI.md")
POSTARE = Path("idei/facebook_post.json")
IESIRE = Path("site/index.html")
LISTE = "https://cadouripebuget.systeme.io/cadouri"   # listele pe bugete + abonarea (Systeme.io)

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
    poza = (f'<img src="{e(p["poza"])}" alt="{e(p["nume"])}" loading="{"eager" if mare else "lazy"}">'
            if p["poza"] else '<span class="fara-poza">🎁</span>')
    eticheta = '<p class="eticheta">✦ Ideea zilei de pe Facebook ✦</p>' if mare else ""
    return f"""
    <article class="card{' mare' if mare else ''}">
      <a class="rama" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">
        <span class="panou">{poza}</span>{insigna}
      </a>
      <div class="info">
        {eticheta}
        <h2>{e(p['nume'])}</h2>
        <div class="linie"><span>✦</span></div>
        <p class="pret">{p['pret']} lei {vechi}</p>
        <p class="magazin">{e(p['magazin'])}</p>
        <a class="buton" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">Vezi produsul</a>
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
<meta name='profitshareid' content='22c6ef787053676c47d6e124210c3dd5' />
<title>Cadouri pe Buget – ideile de azi</title>
<meta name="description" content="Idei de cadouri sub 400 lei, cu reduceri, alese în fiecare zi.">
<meta property="og:title" content="Cadouri pe Buget – ideile de azi">
<meta property="og:description" content="Idei de cadouri cu reduceri, alese în fiecare zi.">
<meta name="theme-color" content="#0b0806">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --negru:#0b0806; --card:#140e0b; --visiniu:#611c15; --visiniu-inchis:#3a0f0c;
    --smarald:#183521; --auriu:#dba666; --auriu-deschis:#f0c896; --auriu-inchis:#a8763a;
    --crem:#f3e6d4; --gri:#b9a894;
    --serif:"Playfair Display", Georgia, "Times New Roman", serif;
    --sans:Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  html {{ background:var(--negru); }}
  body {{
    margin:0; min-height:100vh; font-family:var(--sans); color:var(--crem); line-height:1.45;
    background:
      radial-gradient(60vmax 45vmax at 0% 0%, rgba(97,28,21,.55), transparent 70%),
      radial-gradient(55vmax 45vmax at 100% 100%, rgba(24,53,33,.6), transparent 70%),
      radial-gradient(3px 3px at 12% 22%, rgba(240,200,150,.55), transparent),
      radial-gradient(2px 2px at 82% 14%, rgba(240,200,150,.45), transparent),
      radial-gradient(4px 4px at 70% 38%, rgba(219,166,102,.25), transparent),
      radial-gradient(2px 2px at 30% 68%, rgba(240,200,150,.35), transparent),
      radial-gradient(3px 3px at 90% 76%, rgba(219,166,102,.3), transparent),
      var(--negru);
    background-attachment:fixed;
  }}

  header {{ text-align:center; padding:44px 20px 18px; }}
  .fundita {{ font-size:1.9rem; filter:drop-shadow(0 0 12px rgba(219,166,102,.45)); }}
  header h1 {{
    font-family:var(--serif); font-weight:600; margin:6px 0 0; font-size:clamp(2rem, 7vw, 3rem);
    background:linear-gradient(180deg, var(--auriu-deschis), var(--auriu) 60%, var(--auriu-inchis));
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }}
  header .sub {{ margin:6px 0 0; font-family:var(--serif); font-style:italic; color:var(--auriu-deschis); font-size:1.05rem; }}
  header .data {{ margin:12px auto 0; display:inline-block; padding:6px 16px; border:1px solid rgba(219,166,102,.45);
                 border-radius:999px; color:var(--gri); font-size:.85rem; }}

  .linie {{ display:flex; align-items:center; gap:10px; color:var(--auriu); font-size:.7rem; }}
  .linie::before, .linie::after {{ content:""; flex:1; height:1px;
                                   background:linear-gradient(90deg, transparent, rgba(219,166,102,.7), transparent); }}

  main {{ max-width:1040px; margin:0 auto; padding:18px 16px 36px;
         display:grid; gap:20px; grid-template-columns:repeat(auto-fill, minmax(230px, 1fr)); }}

  .card {{
    position:relative; display:flex; flex-direction:column; border-radius:18px; overflow:hidden;
    background:linear-gradient(180deg, rgba(20,14,11,.92), rgba(14,10,8,.96));
    border:1px solid rgba(219,166,102,.35);
    box-shadow:0 10px 30px rgba(0,0,0,.45), inset 0 0 0 4px rgba(11,8,6,.9), inset 0 0 0 5px rgba(219,166,102,.18);
  }}
  .rama {{ position:relative; display:block; padding:14px 14px 0; text-decoration:none; }}
  .panou {{
    display:flex; align-items:center; justify-content:center; aspect-ratio:1/1; overflow:hidden;
    background:#fff; border-radius:14px; border:1px solid rgba(219,166,102,.6);
    box-shadow:0 0 0 4px rgba(97,28,21,.35), 0 0 22px rgba(219,166,102,.18);
  }}
  .panou img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .fara-poza {{ font-size:3rem; }}
  .insigna {{
    position:absolute; top:22px; left:22px; padding:4px 10px; border-radius:999px; font-weight:600; font-size:.85rem;
    background:linear-gradient(180deg, #7a241b, var(--visiniu)); color:var(--auriu-deschis);
    border:1px solid rgba(240,200,150,.55);
  }}
  .info {{ padding:14px 16px 18px; display:flex; flex-direction:column; gap:8px; flex:1; text-align:center; }}
  h2 {{ font-family:var(--serif); font-weight:500; font-size:1.08rem; margin:0; color:var(--crem); }}
  .pret {{ margin:0; font-family:var(--serif); font-size:1.6rem; color:var(--auriu-deschis); }}
  .vechi {{ font-family:var(--sans); color:var(--gri); text-decoration:line-through; font-size:.85rem; margin-left:6px; }}
  .magazin {{ margin:0; color:var(--gri); font-size:.8rem; letter-spacing:.04em; text-transform:uppercase; }}
  .buton {{
    margin-top:auto; display:block; padding:12px; border-radius:999px; text-decoration:none; font-weight:600;
    color:#2a1606; background:linear-gradient(180deg, var(--auriu-deschis), var(--auriu) 55%, var(--auriu-inchis));
    box-shadow:0 4px 16px rgba(219,166,102,.25);
  }}
  .buton:hover, .buton:focus-visible {{ filter:brightness(1.08); outline:2px solid var(--auriu-deschis); outline-offset:2px; }}

  /* ideea zilei: rama in arcada, ca in postari */
  .card.mare {{ grid-column:1/-1; border-color:rgba(219,166,102,.6);
               background:
                 radial-gradient(80% 60% at 0% 0%, rgba(97,28,21,.55), transparent 70%),
                 radial-gradient(70% 60% at 100% 100%, rgba(24,53,33,.55), transparent 70%),
                 rgba(14,10,8,.96); }}
  .card.mare .rama {{ padding:22px 22px 0; }}
  .card.mare .panou {{ border-radius:200px 200px 16px 16px; border-width:2px; aspect-ratio:4/5; }}
  .card.mare .info {{ padding:18px 22px 24px; justify-content:center; }}
  .card.mare h2 {{ font-size:1.5rem; }}
  .card.mare .pret {{ font-size:2.4rem; }}
  .eticheta {{ margin:0; color:var(--auriu); font-size:.8rem; letter-spacing:.12em; text-transform:uppercase; }}
  @media (min-width:700px) {{
    .card.mare {{ flex-direction:row; align-items:stretch; }}
    .card.mare .rama {{ flex:0 0 42%; padding:26px 0 26px 26px; }}
    .card.mare .info {{ padding:26px 40px; gap:12px; }}
    .card.mare .buton {{ margin-top:10px; align-self:center; padding:14px 40px; }}
  }}

  @media (max-width:560px) {{
    main {{ grid-template-columns:1fr 1fr; gap:12px; padding:12px 12px 28px; }}
    .card:not(.mare) .rama {{ padding:8px 8px 0; }}
    .card:not(.mare) .panou {{ border-radius:10px; box-shadow:0 0 0 3px rgba(97,28,21,.35); }}
    .card:not(.mare) .insigna {{ top:13px; left:13px; font-size:.75rem; padding:3px 8px; }}
    .card:not(.mare) .info {{ padding:10px 10px 12px; gap:6px; }}
    .card:not(.mare) h2 {{ font-size:.9rem; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
    .card:not(.mare) .pret {{ font-size:1.25rem; }}
    .card:not(.mare) .vechi {{ display:block; margin:0; }}
    .card:not(.mare) .magazin {{ font-size:.68rem; }}
    .card:not(.mare) .buton {{ padding:9px 6px; font-size:.85rem; }}
  }}

  .liste {{ max-width:1040px; margin:6px auto 30px; padding:0 16px; }}
  .liste-cutie {{
    border:1px solid rgba(219,166,102,.5); border-radius:18px; padding:26px 20px; text-align:center;
    background:
      radial-gradient(70% 90% at 0% 0%, rgba(97,28,21,.6), transparent 70%),
      radial-gradient(70% 90% at 100% 100%, rgba(24,53,33,.6), transparent 70%),
      rgba(14,10,8,.95);
  }}
  .liste h2 {{ font-size:1.5rem; color:var(--auriu-deschis); }}
  .liste p {{ color:var(--gri); margin:8px auto 16px; max-width:520px; }}
  .bugete {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-bottom:22px; }}
  .bugete a {{ padding:9px 18px; border-radius:999px; border:1px solid rgba(219,166,102,.6);
              color:var(--auriu-deschis); text-decoration:none; font-weight:500; }}
  .bugete a:hover {{ background:rgba(219,166,102,.12); }}
  .liste .buton {{ display:inline-block; padding:13px 30px; }}

  footer {{ max-width:640px; margin:0 auto; padding:0 20px 40px; text-align:center; color:var(--gri); font-size:.8rem; }}
  footer .linie {{ margin-bottom:14px; }}
</style>
</head>
<body>
<header>
  <div class="fundita">🎁</div>
  <h1>Cadouri pe Buget</h1>
  <p class="sub">Idei de cadouri sub 50, 100 și 200 de lei</p>
  <p class="data">Ideile de azi · {data} · prețuri verificate dimineața</p>
</header>
<main>{carduri}
</main>
<section class="liste">
  <div class="liste-cutie">
    <h2>Vrei mai multe idei?</h2>
    <p>Liste alese de mână, pe bugete clare, cu cadouri verificate.</p>
    <div class="bugete">
      <a href="{LISTE}" target="_blank" rel="noopener">Sub 50 lei</a>
      <a href="{LISTE}" target="_blank" rel="noopener">Sub 100 lei</a>
      <a href="{LISTE}" target="_blank" rel="noopener">Sub 200 lei</a>
    </div>
    <div class="linie"><span>✦</span></div>
    <p><strong style="color:var(--crem)">Primește în fiecare joi 5 cadouri bune sub 100 lei</strong>, direct pe e-mail.
    Te poți dezabona oricând.</p>
    <a class="buton" href="{LISTE}#form-input-8976bb08" target="_blank" rel="noopener">Vreau lista pe e-mail</a>
  </div>
</section>
<footer>
  <div class="linie"><span>✦</span></div>
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
