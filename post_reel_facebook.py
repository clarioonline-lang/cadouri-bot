"""
Posteaza Reel-ul zilei (imagini/reel.mp4, facut de reel.py) pe pagina de Facebook.

Pasii Graph API pentru Reels: start (primim video_id) -> urcam fisierul pe rupload -> finish (PUBLISHED).
Foloseste aceeasi cheie FB_PAGE_TOKEN ca post_facebook.py si acelasi jurnal idei/postat.txt:
daca Reel-ul a iesit, post_facebook.py vede ca s-a postat azi si nu mai pune si poza.
Daca ceva nu merge, iese cu eroare si workflow-ul posteaza poza, ca pana acum.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://graph.facebook.com/v26.0"
INFO = Path("idei/reel.json")
JURNAL = Path("idei/postat.txt")


def cerere(url, date_form=None, corp=None, antete=None):
    if corp is not None:
        req = urllib.request.Request(url, data=corp, method="POST", headers=antete or {})
    elif date_form is not None:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(date_form).encode(), method="POST")
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"EROARE Facebook ({e.code}): {e.read().decode(errors='replace')}")


def main():
    token = os.environ.get("FB_PAGE_TOKEN", "").strip()
    if not token:
        sys.exit("Lipseste FB_PAGE_TOKEN.")
    if not INFO.exists():
        sys.exit("Nu exista idei/reel.json - nu am Reel azi.")
    info = json.loads(INFO.read_text(encoding="utf-8"))
    azi = date.today().isoformat()
    if info.get("data") != azi:
        sys.exit(f"Reel-ul e din {info.get('data')}, nu de azi.")
    if JURNAL.exists() and azi in JURNAL.read_text(encoding="utf-8"):
        print("Am postat deja azi.")
        return
    fisier = Path(info["fisier"])
    if not fisier.exists():
        sys.exit("Lipseste fisierul Reel-ului.")

    page_id = cerere(f"{API}/me?" + urllib.parse.urlencode({"access_token": token}))["id"]

    start = cerere(f"{API}/{page_id}/video_reels", {"upload_phase": "start", "access_token": token})
    video_id = start["video_id"]
    date_video = fisier.read_bytes()
    urcare = cerere(start.get("upload_url") or f"https://rupload.facebook.com/video-upload/v26.0/{video_id}",
                    corp=date_video,
                    antete={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(date_video))})
    if not urcare.get("success"):
        sys.exit(f"Urcarea nu a mers: {urcare}")

    fin = cerere(f"{API}/{page_id}/video_reels", {
        "upload_phase": "finish", "video_id": video_id, "video_state": "PUBLISHED",
        "description": info["text_facebook"], "access_token": token})
    if not fin.get("success"):
        sys.exit(f"Publicarea nu a mers: {fin}")

    # Facebook proceseaza clipul cateva zeci de secunde; verificam starea (informativ)
    for _ in range(12):
        time.sleep(10)
        st = cerere(f"{API}/{video_id}?" + urllib.parse.urlencode({"fields": "status", "access_token": token}))
        faza = (st.get("status") or {}).get("video_status")
        print(f"Stare Reel: {faza}")
        if faza in ("ready", "published", "error"):
            break
    if faza == "error":
        sys.exit(f"Facebook a respins clipul: {st}")

    print(f"Reel postat: {video_id}")
    with JURNAL.open("a", encoding="utf-8") as f:
        f.write(f"{azi}|reel:{video_id}\n")


if __name__ == "__main__":
    main()
