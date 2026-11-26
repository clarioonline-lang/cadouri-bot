"""
Posteaza automat pe pagina de Facebook postarea pregatita de facebook_post.py
(idei/facebook_post.json): text + 1 poza, sau album de mai multe poze duminica.

Are nevoie de secretul FB_PAGE_TOKEN (cheia paginii Cadouri pe Buget).
Fara cheie nu face nimic. Nu posteaza de doua ori in aceeasi zi (idei/postat.txt).
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://graph.facebook.com/v26.0"
POSTARE = Path("idei/facebook_post.json")
JURNAL = Path("idei/postat.txt")


def cerere(cale, token, date_form=None):
    """GET daca date_form e None, altfel POST. Intoarce raspunsul JSON."""
    url = f"{API}/{cale}"
    if date_form is None:
        url += "?" + urllib.parse.urlencode({"access_token": token})
        req = urllib.request.Request(url)
    else:
        body = urllib.parse.urlencode({**date_form, "access_token": token}).encode()
        req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detalii = e.read().decode(errors="replace")
        sys.exit(f"EROARE Facebook ({e.code}) la {cale}: {detalii}")


def main():
    token = os.environ.get("FB_PAGE_TOKEN", "").strip()
    if not token:
        print("Lipseste secretul FB_PAGE_TOKEN - nu postez nimic.")
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
        print("Am postat deja azi.")
        return

    pagina = cerere("me", token)          # cheia paginii -> id-ul paginii
    page_id = pagina["id"]
    print(f"Postez pe: {pagina.get('name')} ({page_id})")

    text, poze = post["text"], post.get("poze") or []
    if len(poze) == 1:
        rez = cerere(f"{page_id}/photos", token, {"url": poze[0], "caption": text})
    elif len(poze) > 1:
        ids = []
        for url in poze:   # urcam pozele nepublicate, apoi le punem intr-o singura postare
            ids.append(cerere(f"{page_id}/photos", token, {"url": url, "published": "false"})["id"])
        form = {"message": text}
        for i, fid in enumerate(ids):
            form[f"attached_media[{i}]"] = json.dumps({"media_fbid": fid})
        rez = cerere(f"{page_id}/feed", token, form)
    else:
        rez = cerere(f"{page_id}/feed", token, {"message": text})

    post_id = rez.get("post_id") or rez.get("id")
    print(f"Postat: {post_id}")
    with JURNAL.open("a", encoding="utf-8") as f:
        f.write(f"{azi}|{post_id}\n")


if __name__ == "__main__":
    main()
