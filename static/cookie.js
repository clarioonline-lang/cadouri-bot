/* Banner de informare despre cookie-uri.
   Site-ul nu pune cookie-uri de statistici sau publicitate, deci nu e nimic de acceptat:
   bannerul doar informeaza. Alegerea „Am înțeles” se tine minte in localStorage (strict necesar,
   ca bannerul sa nu apara la fiecare pagina). Daca vom adauga vreodata statistici/pixeli,
   aici se adauga butoanele Accept / Refuz si incarcarea lor doar dupa acord. */
(function () {
  var CHEIE = "cpb-info-cookie-v1";
  try { if (localStorage.getItem(CHEIE)) return; } catch (e) {}

  var stil = document.createElement("style");
  stil.textContent =
    "#cpb-cookie{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:560px;margin:0 auto;" +
    "background:#fffdf9;color:#2a1a14;border:1px solid #d9c3a0;border-radius:16px;padding:18px 20px;" +
    "box-shadow:0 20px 50px -20px rgba(42,26,20,.45);font:15px/1.55 Inter,system-ui,sans-serif}" +
    "#cpb-cookie p{margin:0 0 12px}#cpb-cookie a{color:#611c15}" +
    "#cpb-cookie .rand{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}" +
    "#cpb-cookie button{background:#611c15;color:#f7f1e8;border:0;border-radius:999px;padding:11px 24px;" +
    "font:600 15px Inter,system-ui,sans-serif;cursor:pointer;min-height:44px}" +
    "#cpb-cookie button:focus-visible{outline:2px solid #611c15;outline-offset:3px}";
  document.head.appendChild(stil);

  var b = document.createElement("div");
  b.id = "cpb-cookie";
  b.setAttribute("role", "region");
  b.setAttribute("aria-label", "Informare despre cookie-uri");
  b.innerHTML =
    "<p><strong>Cookie-uri:</strong> site-ul nostru nu folosește cookie-uri de statistici sau de publicitate. " +
    "Când dai click pe un produs, magazinul și rețeaua de afiliere pot folosi propriile cookie-uri, pe site-urile lor.</p>" +
    "<div class='rand'><a href='/confidentialitate.html#cookie-uri'>Detalii în Politica de confidențialitate</a>" +
    "<button type='button'>Am înțeles</button></div>";
  b.querySelector("button").addEventListener("click", function () {
    try { localStorage.setItem(CHEIE, "1"); } catch (e) {}
    b.remove();
  });
  document.body.appendChild(b);
})();
