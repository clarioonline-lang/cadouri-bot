# Cadouri Bot

În fiecare dimineață descarcă feed-ul Profitshare, alege 10 produse bune de cadou (preț 30–400 lei, prioritate pe reduceri) și scrie ideile de postări, cu poză, link de afiliat și caption, în **`idei/AZI.md`**.

- Istoricul zilelor trecute este în folderul `idei/`.
- Produsele nu se repetă timp de 30 de zile.
- Setările (preț, număr de idei) sunt la începutul fișierului `idei_cadouri.py`.
- Link-ul feed-ului e în secretul `FEED_URL` (Settings → Secrets and variables → Actions). Poți pune mai multe link-uri, separate prin virgulă.
- Pentru rulare manuală: tab-ul **Actions**, apoi **Idei de cadouri zilnic**, apoi **Run workflow**.
