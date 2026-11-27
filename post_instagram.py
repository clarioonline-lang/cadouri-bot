"""
Posteaza pe Instagram (@cadouripebuget) aceeasi imagine desenata ca pe Facebook.

Instagram nu accepta fisiere trimise direct: imaginea trebuie sa fie la o adresa publica.
Workflow-ul pagina.yml copiaza imaginile pe vitrina (GitHub Pages), apoi ruleaza scriptul asta.

Are nevoie de FB_PAGE_TOKEN cu permisiunile instagram_basic si instagram_content_publish,
iar contul de Instagram trebuie sa fie legat de pagina de Facebook.
Daca lipseste ceva, scrie de ce si nu face nimic (nu opreste restul).
Nu posteaza de doua ori in aceeasi zi (idei/postat_ig.txt).
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://graph.facebook.com/v26.0"
POSTARE = Path("idei/facebook_post.json")
JURNAL = Path("idei/postat_ig.txt")
SITE = "https://cadouripebuget.online/imagini/"


class EroareFacebook(Exception):
    pass


def cerere(cale, token, date_form=None, params=None):
    url = f"{API}/{cale}"
    if date_form is None:
        url += "?" + urllib.parse.urlencode({**(params or {}), "access_token": token})
        req = urllib.request.Request(url)
    else:
        body = urllib.parse.urlencode({**date_form, "access_token": token}).encode()
        req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise EroareFacebook(f"({e.code}) la {cale}: {e.read().decode(errors='replace')[:400]}")


def asteapta_gata(container, token, incercari=20):
    """Instagram proceseaza imaginea cateva secunde inainte sa poata fi publicata."""
    for _ in range(incercari):
        stare = cerere(container, token, params={"fields": "status_code"}).get("status_code")
        if stare == "FINISHED":
            return
        if stare in ("ERROR", "EXPIRED"):
            raise EroareFacebook(f"Instagram a respins imaginea (status {stare}).")
        time.sleep(5)
    raise EroareFacebook("Instagram nu a terminat procesarea imaginii la timp.")


def main():
    token = os.environ.get("FB_PAGE_TOKEN", "").strip()
    if not token:
        print("Lipseste FB_PAGE_TOKEN - nu postez pe Instagram.")
        return
    if not POSTARE.exists():
        print("Nu exista idei/facebook_post.json - nimic de postat.")
        return
    post = json.loads(POSTARE.read_text(encoding="utf-8"))
    azi = date.today().isoformat()
    if post.get("data") != azi:
        print(f"Postarea pregatita e din {post.get('data')}, nu de azi - nu postez.")
        return
    if JURNAL.exists() and azi in JURNAL.read_text(encoding="utf-8"):
        print("Am postat deja azi pe Instagram.")
        return
    imagini = [Path(f).name for f in (post.get("imagini") or [])]
    if not imagini:
        print("Nu exista imagini desenate azi - nu postez pe Instagram.")
        return
    text = post.get("text_instagram") or post["text"]

    try:
        pagina = cerere("me", token, params={"fields": "id,instagram_business_account{id,username}"})
        cont = pagina.get("instagram_business_account")
        if not cont:
            print("Pagina nu are cont de Instagram legat, sau cheia nu are permisiunile pentru "
                  "Instagram (instagram_basic, instagram_content_publish). Nu postez.")
            return
        ig = cont["id"]
        print(f"Postez pe Instagram: @{cont.get('username')}")

        urls = [SITE + n for n in imagini]
        if len(urls) == 1:
            container = cerere(f"{ig}/media", token, {"image_url": urls[0], "caption": text})["id"]
        else:   # carusel: fiecare imagine separat, apoi albumul
            copii = []
            for u in urls:
                c = cerere(f"{ig}/media", token, {"image_url": u, "is_carousel_item": "true"})["id"]
                asteapta_gata(c, token)
                copii.append(c)
            container = cerere(f"{ig}/media", token, {"media_type": "CAROUSEL",
                                                      "children": ",".join(copii), "caption": text})["id"]
        asteapta_gata(container, token)
        rez = cerere(f"{ig}/media_publish", token, {"creation_id": container})
    except EroareFacebook as e:
        print(f"EROARE Instagram {e}")
        return

    print(f"Postat pe Instagram: {rez.get('id')}")
    with JURNAL.open("a", encoding="utf-8") as f:
        f.write(f"{azi}|{rez.get('id')}\n")


if __name__ == "__main__":
    main()
