"""
Pagina-vitrina Cadouri pe Buget: o pagina web cu ideile zilei.

Citeste idei/AZI.md (cele 10 produse) si idei/facebook_post.json (ce s-a postat azi pe
Facebook) si scrie site/index.html. Workflow-ul pagina.yml o publica pe GitHub Pages:
https://cadouripebuget.online

Stil „boutique de lux” (ales pe 27 nov. 2026): fundal crem, visiniu si auriu ca accente,
titluri Playfair Display, text Inter. Culorile sunt cele ale paginii de Facebook, pe fundal deschis.

Produsul postat azi pe Facebook apare sus, in arcada, ca cine vine de pe Messenger
sa-l gaseasca imediat. Duminica (album) apare acolo cea mai mare reducere.

ATENTIE: eticheta <meta name='profitshareid'> valideaza site-ul in Profitshare - nu o sterge.
"""

import html
import shutil
import json
from datetime import date
from pathlib import Path

from facebook_post import citeste_idei

INTRARE = Path("idei/AZI.md")
POSTARE = Path("idei/facebook_post.json")
IESIRE = Path("site/index.html")
LISTE = "https://cadouripebuget.systeme.io/cadouri"
# eMAG: linkuri de afiliere Profitshare (generate pe 28 nov. 2026) catre cautari/categorii de cadouri
EMAG = [
    ("Pentru ea", "https://l.profitshare.ro/l/17585454"),
    ("Pentru el", "https://l.profitshare.ro/l/17585458"),
    ("Pentru copii", "https://l.profitshare.ro/l/17585459"),
    ("Moș Nicolae", "https://l.profitshare.ro/l/17585460"),
    ("Secret Santa", "https://l.profitshare.ro/l/17585461"),
    ("Coșuri cadou", "https://l.profitshare.ro/l/17585462"),
]   # listele pe bugete + abonarea (Systeme.io)

LUNI = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie",
        "august", "septembrie", "octombrie", "noiembrie", "decembrie"]


def e(text):
    return html.escape(str(text or ""), quote=True)


ZILE = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
INSTAGRAM = "https://www.instagram.com/cadouripebuget/"
FACEBOOK = "https://www.facebook.com/profile.php?id=61596931285889"


def pret_vechi(p):
    if p["discount"] >= 10:
        return round(p["pret"] / (1 - p["discount"] / 100))
    return None


def card(p):
    vechi = pret_vechi(p)
    insigna = f'<span class="insigna">−{p["discount"]}%</span>' if vechi else ""
    vechi_html = f'<span class="vechi">{vechi} lei</span>' if vechi else ""
    poza = (f'<img src="{e(p["poza"])}" alt="{e(p["nume"])}" loading="lazy">'
            if p["poza"] else '<span class="fara-poza">Cadou</span>')
    return f"""
      <a class="card" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">
        <span class="poza">{poza}{insigna}</span>
        <span class="info">
          <span class="magazin">{e(p['magazin'])}</span>
          <span class="nume">{e(p['nume'])}</span>
          <span class="rand"><span class="pret">{p['pret']} lei</span>{vechi_html}<span class="vezi">Vezi →</span></span>
        </span>
      </a>"""


def vedeta(p, de_pe_fb):
    vechi = pret_vechi(p)
    vechi_html = f'<span class="vechi">{vechi} lei</span>' if vechi else ""
    insigna = f'<span class="insigna mare">−{p["discount"]}%</span>' if vechi else ""
    poza = (f'<img src="{e(p["poza"])}" alt="{e(p["nume"])}" loading="eager">'
            if p["poza"] else '<span class="fara-poza">Cadou</span>')
    eticheta = "Ideea zilei de pe Facebook" if de_pe_fb else "Recomandarea zilei"
    return f"""
      <a class="arcada" href="{e(p['link'])}" target="_blank" rel="sponsored noopener">
        <span class="arcada-poza">{poza}</span>
        <span class="eticheta">{eticheta}</span>
        <span class="arcada-nume">{e(p['nume'])}</span>
        <span class="rand"><span class="pret mare">{p['pret']} lei</span>{vechi_html}{insigna}</span>
        <span class="buton plin lat">Vezi la {e(p['magazin'])}</span>
      </a>"""


def main():
    if not INTRARE.exists():
        print("Nu exista idei/AZI.md - nimic de facut.")
        return
    produse = citeste_idei(INTRARE.read_text(encoding="utf-8"))
    if not produse:
        print("Nu am gasit produse in AZI.md.")
        return

    # produsul postat azi pe Facebook sus, in arcada; altfel (duminica) cea mai mare reducere
    text_fb = ""
    if POSTARE.exists():
        text_fb = json.loads(POSTARE.read_text(encoding="utf-8")).get("text", "")
    vedete = [p for p in produse if p["nume"] and p["nume"] in text_fb]
    de_pe_fb = len(vedete) == 1
    sus = vedete[0] if de_pe_fb else max(produse, key=lambda p: p["discount"])
    restul = [p for p in produse if p is not sus]

    azi = date.today()
    data = f"{ZILE[azi.weekday()]}, {azi.day} {LUNI[azi.month - 1]}"
    carduri = "".join(card(p) for p in restul)
    emag_butoane = "".join(f'\n    <a href="{e(u)}" target="_blank" rel="sponsored noopener"><span>{e(t)}</span><span class="sageata">→</span></a>'
                           for t, u in EMAG)

    pagina = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name='profitshareid' content='22c6ef787053676c47d6e124210c3dd5' />
<meta name='profitshareid' content='92b8226f14e19abefdc952a064be6a1f' />
<title>Cadouri pe Buget – cadoul potrivit, la prețul potrivit</title>
<meta name="description" content="În fiecare dimineață, 10 cadouri reduse între 30 și 400 de lei, din magazine românești.">
<meta property="og:title" content="Cadouri pe Buget – ideile de azi">
<meta property="og:description" content="10 cadouri reduse, alese în fiecare dimineață.">
<meta name="theme-color" content="#f7f1e8">
<link rel="preload" href="fonturi/playfair.woff2" as="font" type="font/woff2" crossorigin>
<style>
  /* fonturile sunt gazduite pe site (nu de la Google), ca adresa IP a vizitatorilor sa nu ajunga la terti */
  @font-face {{ font-family:"Playfair Display"; src:url("fonturi/playfair.woff2") format("woff2"); font-weight:400 900; font-display:swap; }}
  @font-face {{ font-family:"Inter"; src:url("fonturi/inter.woff2") format("woff2"); font-weight:100 900; font-display:swap; }}
  :root {{
    --crem:#f7f1e8; --hartie:#fffdf9; --nisip:#efe4d3; --linie:#e4d6c1; --linie2:#d9c3a0;
    --visiniu:#611c15; --visiniu-inchis:#3f110c; --auriu:#8a6a2f; --auriu-cald:#dba666;
    --text:#2a1a14; --text2:#5a4538; --gri:#8c7a6c;
    --serif:"Playfair Display", Georgia, "Times New Roman", serif;
    --sans:Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:var(--crem); color:var(--text); font-family:var(--sans); line-height:1.5; }}
  a {{ color:var(--visiniu); text-decoration:none; }}
  .zona {{ max-width:1180px; margin:0 auto; padding-left:32px; padding-right:32px; }}
  .supra {{ margin:0 0 16px; font-size:13px; letter-spacing:3px; text-transform:uppercase; color:var(--auriu); font-weight:600; }}

  header {{ border-bottom:1px solid var(--linie); }}
  header .zona {{ padding-top:20px; padding-bottom:20px; display:flex; flex-wrap:wrap; gap:14px 28px; align-items:center; justify-content:space-between; }}
  .logo {{ font-family:var(--serif); font-size:26px; font-weight:700; color:var(--text); }}
  .logo i {{ font-weight:400; color:var(--visiniu); }}
  nav {{ display:flex; flex-wrap:wrap; gap:8px 26px; font-size:14px; font-weight:500; letter-spacing:.3px; }}
  nav a:hover {{ color:var(--visiniu-inchis); text-decoration:underline; text-underline-offset:4px; }}

  .erou {{ padding-top:72px; padding-bottom:72px; display:flex; flex-wrap:wrap; gap:56px; align-items:center; }}
  .erou-text {{ flex:1 1 440px; min-width:0; }}
  h1 {{ margin:0 0 22px; font-family:var(--serif); font-size:clamp(40px, 6vw, 60px); line-height:1.08; font-weight:600; }}
  h1 i {{ font-weight:400; color:var(--visiniu); }}
  .erou-text p.intro {{ margin:0 0 34px; font-size:18px; line-height:1.6; color:var(--text2); max-width:480px; }}
  .butoane {{ display:flex; flex-wrap:wrap; gap:14px; }}
  .buton {{ display:inline-block; padding:15px 28px; border-radius:999px; font-weight:600; font-size:15px; border:1px solid var(--visiniu); color:var(--visiniu); text-align:center; transition:background .2s, color .2s; }}
  .buton:hover {{ background:var(--visiniu); color:var(--crem); }}
  .buton.plin {{ background:var(--visiniu); color:var(--crem); }}
  .buton.plin:hover {{ background:var(--visiniu-inchis); }}
  .buton.lat {{ display:block; margin-top:22px; }}

  .erou-vedeta {{ flex:1 1 320px; min-width:0; display:flex; justify-content:center; }}
  .arcada {{ display:block; width:100%; max-width:390px; background:var(--hartie); border:1px solid var(--linie);
            border-radius:200px 200px 18px 18px; padding:26px 26px 28px; color:var(--text);
            box-shadow:0 30px 60px -30px rgba(97,28,21,.35); transition:transform .25s; }}
  .arcada:hover {{ transform:translateY(-4px); }}
  .arcada-poza {{ display:block; border-radius:170px 170px 10px 10px; overflow:hidden; border:1px solid #ead9b8; background:#fff; }}
  .arcada-poza img {{ width:100%; height:300px; object-fit:contain; display:block; }}
  .eticheta {{ display:block; margin:22px 0 6px; font-size:12px; letter-spacing:2.5px; text-transform:uppercase; color:var(--auriu); font-weight:600; }}
  .arcada-nume {{ display:block; margin:0 0 14px; font-family:var(--serif); font-size:24px; line-height:1.25; font-weight:600; }}

  .rand {{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; }}
  .pret {{ font-size:20px; font-weight:600; color:var(--visiniu); }}
  .pret.mare {{ font-family:var(--serif); font-size:34px; font-weight:700; }}
  .vechi {{ font-size:14px; color:var(--gri); text-decoration:line-through; }}
  .insigna {{ position:absolute; top:14px; left:14px; background:var(--visiniu); color:var(--crem); font-size:12px; font-weight:600; padding:4px 10px; border-radius:999px; }}
  .insigna.mare {{ position:static; margin-left:auto; font-size:13px; padding:5px 11px; }}
  .fara-poza {{ display:flex; align-items:center; justify-content:center; height:100%; min-height:200px; font-family:var(--serif); color:var(--gri); }}

  .banda {{ background:var(--visiniu); color:#f3e6d4; }}
  .banda .zona {{ padding-top:20px; padding-bottom:20px; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px 16px; font-size:14px; letter-spacing:.3px; }}
  .banda span::before {{ content:"✦"; color:var(--auriu-cald); margin-right:10px; }}

  .idei {{ padding-top:80px; padding-bottom:40px; }}
  .titlu-sectiune {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:12px; margin-bottom:36px; }}
  h2 {{ margin:0; font-family:var(--serif); font-size:clamp(30px, 4vw, 42px); font-weight:600; }}
  .titlu-sectiune p {{ margin:0; font-size:15px; color:var(--text2); }}
  .grila {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:28px; }}
  .card {{ display:flex; flex-direction:column; background:var(--hartie); border:1px solid #e9dcc8; border-radius:16px; overflow:hidden; color:var(--text); transition:transform .2s, box-shadow .2s; }}
  .card:hover {{ transform:translateY(-3px); box-shadow:0 18px 40px -24px rgba(97,28,21,.4); }}
  .poza {{ position:relative; display:block; background:#fff; aspect-ratio:1/1; }}
  .poza img {{ width:100%; height:100%; object-fit:contain; display:block; }}
  .info {{ display:flex; flex-direction:column; gap:6px; flex:1; padding:18px 20px 20px; border-top:1px solid #f0e6d6; }}
  .magazin {{ font-size:12px; letter-spacing:1.5px; text-transform:uppercase; color:var(--auriu); }}
  .nume {{ font-family:var(--serif); font-size:18px; line-height:1.3; font-weight:600; margin-bottom:8px; }}
  .card .rand {{ margin-top:auto; }}
  .vezi {{ margin-left:auto; font-size:13px; font-weight:600; color:var(--visiniu); }}

  .bugete {{ padding-top:60px; padding-bottom:60px; }}
  .cutie {{ background:var(--nisip); border-radius:24px; padding:56px 40px; text-align:center; }}
  .cutie p {{ margin:12px 0 30px; color:var(--text2); }}
  .sume {{ display:flex; flex-wrap:wrap; gap:16px; justify-content:center; }}
  .sume a {{ background:var(--hartie); border:1px solid var(--linie2); padding:18px 34px; border-radius:14px; font-family:var(--serif); font-size:22px; color:var(--text); transition:border-color .2s; }}
  .sume a:hover {{ border-color:var(--visiniu); }}
  .sume b {{ color:var(--visiniu); }}

  .ghiduri-acasa {{ padding-top:10px; padding-bottom:30px; }}
  .ghid-banda {{ display:block; background:var(--visiniu); color:var(--crem); border-radius:22px; padding:30px 34px; text-decoration:none; }}
  .ghid-banda .supra {{ color:var(--auriu-cald); }}
  .ghid-banda-titlu {{ display:block; font-family:var(--serif); font-size:clamp(26px,3.5vw,36px); line-height:1.2; margin-bottom:8px; }}
  .ghid-banda-text {{ display:block; color:#e9d6c2; font-size:16px; }}
  .ghid-banda:hover {{ background:var(--visiniu-inchis); }}
  .emag {{ padding-top:20px; padding-bottom:40px; }}
  .emag-grila {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:14px; }}
  .emag-grila a {{ display:flex; justify-content:space-between; align-items:center; background:var(--hartie); border:1px solid var(--linie2);
                  border-radius:14px; padding:18px 22px; font-family:var(--serif); font-size:20px; color:var(--text); transition:border-color .2s, transform .2s; }}
  .emag-grila a:hover {{ border-color:var(--visiniu); transform:translateY(-2px); }}
  .emag-grila .sageata {{ color:var(--visiniu); font-family:var(--sans); font-weight:600; }}
  .lista {{ max-width:760px; padding-top:40px; padding-bottom:90px; text-align:center; }}
  .lista p.mic {{ margin:14px 0 28px; color:var(--text2); }}

  footer {{ background:var(--text); color:#d9c8b4; }}
  footer .zona {{ padding-top:48px; padding-bottom:48px; display:flex; flex-wrap:wrap; gap:28px; justify-content:space-between; }}
  footer .logo {{ color:#f3e6d4; font-size:22px; display:block; margin-bottom:10px; }}
  footer p {{ margin:0; font-size:14px; line-height:1.7; max-width:460px; }}
  footer nav a {{ color:var(--auriu-cald); }}
  footer p.mic-jos {{ margin-top:14px; font-size:13px; color:#a8957f; }}

  a:focus-visible {{ outline:2px solid var(--visiniu); outline-offset:3px; }}

  @media (max-width:620px) {{
    .emag-grila {{ grid-template-columns:1fr 1fr; gap:10px; }}
    .emag-grila a {{ padding:14px 14px; font-size:16px; }}
    .zona {{ padding-left:16px; padding-right:16px; }}
    header .zona {{ justify-content:center; text-align:center; }}
    nav {{ justify-content:center; }}
    .erou {{ padding-top:40px; padding-bottom:48px; gap:36px; }}
    .arcada-poza img {{ height:240px; }}
    .idei {{ padding-top:56px; }}
    .grila {{ grid-template-columns:1fr 1fr; gap:12px; }}
    .info {{ padding:12px 12px 14px; }}
    .nume {{ font-size:15px; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
    .magazin {{ font-size:10px; letter-spacing:1px; }}
    .pret {{ font-size:17px; }}
    .vezi {{ display:none; }}
    .insigna {{ top:8px; left:8px; font-size:11px; padding:3px 8px; }}
    .cutie {{ padding:40px 20px; }}
    .sume a {{ padding:14px 22px; font-size:19px; }}
  }}
</style>
</head>
<body>
<header>
  <div class="zona">
    <a class="logo" href="#">Cadouri <i>pe</i> Buget</a>
    <nav>
      <a href="#idei">Ideile de azi</a>
      <a href="#bugete">Pe bugete</a>
      <a href="#emag">eMAG</a>
      <a href="ghiduri/">Ghiduri</a>
      <a href="#lista">Lista săptămânală</a>
      <a href="#despre">Despre</a>
    </nav>
  </div>
</header>

<section class="zona erou">
  <div class="erou-text">
    <p class="supra">{data} · ediția de azi</p>
    <h1>Cadoul potrivit,<br><i>la prețul potrivit.</i></h1>
    <p class="intro">În fiecare dimineață alegem 10 cadouri reduse, între 30 și 400 de lei, din magazine românești. Tu doar alegi.</p>
    <div class="butoane">
      <a class="buton plin" href="#idei">Vezi cele {len(produse)} idei</a>
      <a class="buton" href="#bugete">Alege după buget</a>
    </div>
  </div>
  <div class="erou-vedeta">{vedeta(sus, de_pe_fb)}
  </div>
</section>

<section class="banda">
  <div class="zona">
    <span>10 idei noi în fiecare dimineață</span>
    <span>Prețuri verificate zilnic</span>
    <span>Link direct la magazinul oficial</span>
  </div>
</section>

<section id="idei" class="zona idei">
  <div class="titlu-sectiune">
    <h2>Ideile de azi</h2>
    <p>Actualizat azi dimineață</p>
  </div>
  <div class="grila">{carduri}
  </div>
</section>

<section id="bugete" class="zona bugete">
  <div class="cutie">
    <h2>Ai un buget în minte?</h2>
    <p>Liste alese pe sume, cu cadouri verificate.</p>
    <div class="sume">
      <a href="{LISTE}" target="_blank" rel="noopener">Sub <b>50</b> lei</a>
      <a href="{LISTE}" target="_blank" rel="noopener">Sub <b>100</b> lei</a>
      <a href="{LISTE}" target="_blank" rel="noopener">Sub <b>200</b> lei</a>
    </div>
  </div>
</section>

<section class="zona ghiduri-acasa">
  <a class="ghid-banda" href="ghiduri/cadouri-craciun-sub-100-lei-pentru-ea.html">
    <span class="supra">Ghid nou</span>
    <span class="ghid-banda-titlu">Cadouri de Crăciun sub 100 lei pentru ea</span>
    <span class="ghid-banda-text">20 de idei pe tipuri de femei, plus cum afli mărimea inelului fără să te dai de gol →</span>
  </a>
</section>

<section id="emag" class="zona emag">
  <div class="titlu-sectiune">
    <h2>Caută direct pe eMAG</h2>
    <p>Mii de idei de cadouri, cu livrare rapidă</p>
  </div>
  <div class="emag-grila">{emag_butoane}
  </div>
</section>

<section id="lista" class="zona lista">
  <p class="supra">În fiecare joi, pe e-mail</p>
  <h2>5 cadouri sub 100 de lei</h2>
  <p class="mic">Fără spam. Te dezabonezi oricând, cu un click.</p>
  <a class="buton plin" href="{LISTE}#form-input-8976bb08" target="_blank" rel="noopener">Vreau lista pe e-mail</a>
</section>

<footer id="despre">
  <div class="zona">
    <div>
      <span class="logo">Cadouri pe Buget</span>
      <p>O idee nouă în fiecare zi și pe <a href="{FACEBOOK}" target="_blank" rel="noopener" style="color:#dba666">pagina noastră de Facebook</a>. Linkurile sunt de afiliere: dacă cumperi,
      primim un mic comision, fără niciun cost în plus pentru tine. Prețurile și stocul se pot schimba în timpul zilei,
      verifică pe site-ul magazinului.</p>
      <p class="mic-jos">© {azi.year} Lazar Eugen Grigore, Sibiu · <a href="mailto:cadouripebuget@gmail.com" style="color:#dba666">cadouripebuget@gmail.com</a></p>
    </div>
    <nav>
      <a href="informatii-legale.html">Informații legale</a>
      <a href="confidentialitate.html">Confidențialitate</a>
      <a href="{FACEBOOK}" target="_blank" rel="noopener">Facebook</a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a>
      <a href="{LISTE}" target="_blank" rel="noopener">Liste pe bugete</a>
    </nav>
  </div>
</footer>
<script src="cookie.js" defer></script>
</body>
</html>
"""
    IESIRE.parent.mkdir(exist_ok=True)
    IESIRE.write_text(pagina, encoding="utf-8")
    # paginile fixe (informatii legale, confidentialitate) si fonturile locale
    shutil.copytree(Path(__file__).resolve().parent / "static", IESIRE.parent, dirs_exist_ok=True)
    print(f"Scris: {IESIRE} ({len(produse)} produse)")


if __name__ == "__main__":
    main()
