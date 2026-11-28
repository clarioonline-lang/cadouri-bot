"""
Continutul ghidurilor de cadouri (blog-ul de pe cadouripebuget.online/ghiduri/).

Fiecare ghid = text scris de mana (amuzant + util) + produse.
Produsele sunt de doua feluri:
  - "feed": ("Magazin.ro", "cod produs") -> pretul, poza si linkul se iau ZILNIC din feed-urile
    de afiliere (daca produsul dispare sau nu mai e pe stoc, cardul nu mai apare);
  - "manual": magazine fara feed (ex. Perfectbijoux) -> pret verificat la data scrisa in "verificat".
Textul poate contine HTML simplu (<strong>, <em>, <a>).
"""

GHID_MOS_NICOLAE = {
        "slug": "cadouri-mos-nicolae-sub-50-lei",
        "titlu": "Cadouri de Moș Nicolae sub 50 de lei (care încap în ghetuță și nu par de la benzinărie)",
        "titlu_scurt": "Cadouri de Moș Nicolae sub 50 lei",
        "titlu_seo": "Cadouri de Moș Nicolae sub 50 lei – 23 de idei care încap în ghetuță",
        "descriere": "Idei de cadouri de Moș Nicolae sub 50 de lei pentru copii, iubită, iubit, colegi și părinți: "
                     "mici, haioase și utile, care chiar încap în ghetuță. Plus până când comanzi ca să ajungă pe 6 decembrie.",
        "publicat": "2026-11-28",
        "eticheta": "Moș Nicolae",
        "pret_max": 50,
        "intro": """
<p>Moș Nicolae e cel mai subestimat personaj al lui decembrie. Moș Crăciun are reni, sanie, reclame la Coca-Cola.
Moș Nicolae are… o ghetuță. Și o nuieluță. Și un buget care, sincer, rar trece de 50 de lei.</p>
<p>Dar exact asta e frumusețea lui: <strong>cadoul de Moș Nicolae nu trebuie să impresioneze, trebuie să surprindă.</strong>
Ceva mic, pus în ghetuță cu o seară înainte, care să-l facă pe cel care se trezește să zâmbească înainte de cafea.
Mai jos ai 23 de idei sub 50 de lei, împărțite pe cine ce găsește în ghetuță dimineață.</p>
""",
        "test_titlu": "Pentru cine pregătești ghetuța?",
        "sectiuni": [
            {
                "id": "copii",
                "titlu": "Pentru copilul care verifică ghetuța la 6 dimineața",
                "subtitlu": "Și care a lustruit ghetuța pentru prima și ultima dată anul ăsta.",
                "intro": "<p>Pentru copii, regula e simplă: <strong>să facă ceva</strong>. Să lumineze, să se rotească, "
                         "să se poată construi. O jucărie care doar „stă” pierde în fața ambalajului în maximum 4 minute.</p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "3681"), "nume": "Lună magică fosforescentă pentru camera copilului",
                     "text": "O lună care strălucește pe tavan. Ziua e decor, seara e motivul pentru care merge de bunăvoie la culcare. "
                     "(Rezultatele pot varia. Dar merită încercat.)"},
                    {"feed": ("Mindblower.ro", "3679"), "nume": "Cub magic infinit „Galaxii”, puzzle 3D",
                     "text": "Un cub care se pliază la nesfârșit. Ține mâinile ocupate în mașină, la bunici și la masa de Crăciun, "
                     "când adulții vorbesc despre prețul la gaze."},
                    {"feed": ("Giftspot.ro", "124128"), "nume": "Mini lampă în formă de cățel",
                     "text": "Pentru copilul care vrea un cățel. Nu e același lucru, dar nici nu trebuie plimbat la 7 dimineața."},
                    {"feed": ("Giftspot.ro", "16487"), "nume": "Set creativ origami",
                     "text": "Hârtie colorată și instrucțiuni: o după-amiază întreagă fără ecrane. Bonus: îți face și ție o broască."},
                ],
            },
            {
                "id": "pentru-ea",
                "titlu": "Pentru ea (și ghetuța ei cu toc)",
                "subtitlu": "Ți-a spus că „nu e nevoie”. Ai înțeles, sperăm, că e nevoie.",
                "intro": "<p>Moș Nicolae e repetiția generală pentru Crăciun. Un cadou mic și bine ales acum îți "
                         "cumpără puncte prețioase pentru 25 decembrie. <em>Strategie, nu romantism. Dar arată a romantism.</em></p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "4552.Pink"), "nume": "Încălzitor de mâini pufos, roz",
                     "text": "Pufos, cald și roz. Practic, i-ai dăruit o îmbrățișare portabilă pentru stația de autobuz."},
                    {"feed": ("Mindblower.ro", "4321"), "nume": "Mască de dormit „Somn de Diva”",
                     "text": "Pentru că orice divă are nevoie de 8 ore de somn. Sau de 10, duminica. Nu judecăm."},
                    {"feed": ("Mindblower.ro", "4559"), "nume": "Cutie muzicală „Merry Christmas”",
                     "text": "Învârți manivela, cântă colinda. E genul de obiect pe care îl păstrează 20 de ani "
                     "și îl scoate în fiecare decembrie."},
                    {"feed": ("Mindblower.ro", "4036"), "nume": "Suport bijuterii „Căprioara albă”",
                     "text": "O căprioară elegantă pe care atârnă inelele și cerceii. Decor de noptieră care, întâmplător, "
                     "pune ordine în bijuterii."},
                    {"feed": ("Mindblower.ro", "3631"), "nume": "Kit de broderie DIY, siluetă de fată",
                     "text": "Pentru cea care a descoperit că lucrul de mână e noul yoga. Totul e în cutie, inclusiv răbdarea (aproape)."},
                ],
            },
            {
                "id": "pentru-el",
                "titlu": "Pentru el, care „nu are nevoie de nimic”",
                "subtitlu": "Are portofelul din 2014 și o brichetă care merge din a treia încercare.",
                "intro": "<p>Bărbații spun că nu vor nimic, apoi folosesc zilnic, cu mândrie, cel mai mic gadget primit. "
                         "Alege <strong>ceva ce încape în buzunar</strong>: va fi cu el peste tot și te va pomeni de fiecare dată.</p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "706"), "nume": "Wallet Ninja – unealtă cu 18 funcții, cât un card",
                     "text": "Cât un card bancar, cu 18 funcții: șurubelniță, desfăcător, riglă. Va spune „n-o să-l folosesc”, "
                     "apoi îl va folosi a doua zi și se va lăuda."},
                    {"feed": ("Mindblower.ro", "4349"), "nume": "Portofel slim pentru carduri, maro",
                     "text": "Pentru portofelul gros cât o carte de bucate. Subțire, elegant, fără bonuri din 2019."},
                    {"feed": ("Mindblower.ro", "4148"), "nume": "Brichetă electrică cu plasmă",
                     "text": "Se încarcă la USB, nu are flacără, face un arc electric care arată SF. Pentru grătar, lumânări sau doar pentru efect."},
                    {"feed": ("Mindblower.ro", "4252"), "nume": "Pahar de whiskey „Luxury Layers”",
                     "text": "Un pahar frumos face orice băutură să pară mai scumpă. Inclusiv sucul de mere, dacă e duminică dimineața."},
                    {"feed": ("Mindblower.ro", "4597"), "nume": "Set 2 chei multifuncționale „Fulg de nea”",
                     "text": "Arată ca un fulg de nea, ascunde chei, desfăcător și șurubelniță. Cel mai festiv instrument de pe listă."},
                ],
            },
            {
                "id": "colegi",
                "titlu": "Pentru colegi și prieteni (categoria „să râdem un pic”)",
                "subtitlu": "Pentru biroul unde ghetuțele apar misterios pe pervaz.",
                "intro": "<p>La colegi, umorul bate valoarea. Un cadou de 20 de lei care provoacă râsete în open-space "
                         "e mai memorabil decât unul de 50 care pare „cumpărat din obligație”. "
                         "Regula de aur: <strong>glumește cu situația, nu cu persoana.</strong></p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "1388"), "nume": "Hârtie igienică „500 de euro”",
                     "text": "Primul lui milion. Sau, mă rog, primele 200 de foi. Cel mai sigur cadou-glumă din istoria birourilor."},
                    {"feed": ("Mindblower.ro", "4045"), "nume": "Șosete „If you love me, bring me coffee”",
                     "text": "Comunicare non-verbală eficientă. Le poartă la ședința de luni și nimeni nu mai trebuie să întrebe nimic."},
                    {"feed": ("Mindblower.ro", "4067"), "nume": "Pendul pentru indeciși „Alegeri trăsnite”",
                     "text": "Pentru colegul care durează 20 de minute să aleagă unde comandăm prânzul. Problema rezolvată în 3 secunde."},
                    {"feed": ("Mindblower.ro", "4386"), "nume": "Curățător pentru microunde „Angry Mom”",
                     "text": "O mamă furioasă care curăță microundele cu abur. Pentru bucătăria biroului, unde cineva încă încălzește pește."},
                    {"feed": ("Giftspot.ro", "M16079A"), "nume": "Notițe adezive „Câine în cutie”",
                     "text": "Post-it-uri care arată ca un cățel ce iese din cutie. Pentru colega cu 47 de taburi deschise și 12 liste."},
                ],
            },
            {
                "id": "pentru-toti",
                "titlu": "Pentru părinți, bunici și oricine iubește Crăciunul",
                "subtitlu": "Pentru cei care au bradul pregătit din noiembrie și nu-și cer scuze.",
                "intro": "<p>Pentru ei, cadoul de Moș Nicolae e <strong>startul oficial al sărbătorilor</strong>. "
                         "Ceva cald, ceva festiv, ceva care să stea la vedere până după Bobotează.</p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "4740"), "nume": "Cană termosensibilă „Renul vesel”",
                     "text": "Torni ceaiul fierbinte și apare renul. Magie de bucătărie, garantat să fie arătată tuturor musafirilor."},
                    {"feed": ("Mindblower.ro", "4535"), "nume": "Felicitare de Crăciun 3D „Oraș de poveste”",
                     "text": "O felicitare care se deschide într-un oraș întreg. Bunicile o pun pe bufet și o păstrează mai mult decât pe tine la telefon."},
                    {"feed": ("Mindblower.ro", "3584"), "nume": "Șosete Grinch de Crăciun",
                     "text": "Pentru cel care se plânge de colinde din 1 noiembrie. Ironia e cadoul. Șosetele sunt bonusul."},
                    {"feed": ("Mindblower.ro", "4149"), "nume": "Cană de cafea cu pereți dubli, 150 ml",
                     "text": "Pentru espressoul de dimineață: cafeaua pare că plutește, iar mâna nu se arde. Mică, elegantă, utilă zilnic."},
                ],
            },
        ],
        "sectiuni_utile": [
            {
                "id": "regula-ghetutei",
                "titlu": "Regula ghetuței: cum alegi un cadou care chiar încape",
                "html": """
<p>Pare evident, dar ghetuța are dimensiuni fixe și o lungă istorie de cadouri care „stăteau lângă ea”. Pe scurt:</p>
<ol>
  <li><strong>Lungime sub 25 cm</strong> pentru ghetuța de adult, sub 18 cm pentru copii. Ce depășește, stă rezemat, și se pierde efectul.</li>
  <li><strong>Fără sticlă direct în gheată.</strong> Cănile și paharele merg în cutia lor sau învelite într-un fular. Nimeni nu vrea cioburi la 7 dimineața.</li>
  <li><strong>Umple golurile cu clasicele:</strong> o mandarină, câteva nuci, o ciocolată. Costă 10 lei și transformă cadoul în tradiție.</li>
  <li><strong>Pune cadoul seara de 5 decembrie</strong>, după ce s-a culcat toată lumea. Dacă îl pui pe 6 dimineața, nu e Moș Nicolae, e curier.</li>
</ol>
""",
            },
            {
                "id": "cand-comanzi",
                "titlu": "Până când comanzi ca să ajungă pe 6 decembrie?",
                "html": """
<p>Moș Nicolae cade într-o <strong>duminică</strong> anul acesta, deci seara de 5 decembrie e sâmbătă. Ce înseamnă:</p>
<ul>
  <li><strong>Comandă până luni, 30 noiembrie.</strong> Marți, 1 Decembrie, e zi liberă, iar mulți curieri nu livrează. Plus că e vârful comenzilor de sărbători.</li>
  <li><strong>Miercuri, 2 decembrie</strong>, e ultima zi rezonabilă pentru livrare standard.</li>
  <li><strong>Joi și vineri</strong> alege doar produse „în stoc” cu livrare în 24 de ore și verifică dacă se livrează și sâmbăta.</li>
  <li><strong>Ultima soluție:</strong> ridicare personală sau easybox. Termenul exact e pe pagina fiecărui produs, la livrare.</li>
</ul>
<p>Dacă ai ratat termenul: pune în ghetuță o „scrisoare de la Moș Nicolae” care anunță că cadoul e „reținut la vamă la Polul Nord”. Funcționează la copiii sub 8 ani și la adulții cu simțul umorului.</p>
""",
            },
            {
                "id": "nuieluta",
                "titlu": "Și nuieluța? Ghid de bune maniere",
                "html": """
<p>Tradiția spune că cei care n-au fost cuminți primesc o nuieluță. Câteva reguli moderne:</p>
<ul>
  <li><strong>Copiilor:</strong> nuieluța vine <em>împreună</em> cu cadoul, ca o glumă și un mic „anul viitor mai bine”, niciodată în locul lui.</li>
  <li><strong>Adulților:</strong> o nuieluță cu fundă roșie, lângă cadou, e cea mai bună glumă de 0 lei a lui decembrie.</li>
  <li><strong>Colegilor:</strong> doar dacă știi sigur că râd. În caz de dubiu, mandarina e mereu o alegere neutră.</li>
</ul>
""",
            },
        ],
        "faq": [
            ("Ce se pune în ghetuță de Moș Nicolae?",
             "Tradițional: dulciuri, mandarine, nuci și un cadou mic. Pentru copii, o jucărie sau ceva luminos; pentru adulți, un obiect mic și util "
             "sau amuzant. Important e să încapă în ghetuță."),
            ("Cât costă, în medie, un cadou de Moș Nicolae?",
             "Cele mai multe cadouri de Moș Nicolae sunt simbolice, între 20 și 50 de lei. E un cadou-surpriză, nu un cadou mare: cel mare vine de Crăciun."),
            ("Ce cadou de Moș Nicolae le iau colegilor?",
             "Ceva amuzant și neutru: șosete cu mesaj, notițe adezive haioase, o cană sau hârtia igienică „de lux”. Evită cosmeticele și "
             "glumele despre persoană."),
            ("Până când comand ca să ajungă de Moș Nicolae?",
             "Ideal până pe 30 noiembrie (1 Decembrie e zi liberă), cel târziu pe 2 decembrie. După aceea, alege produse cu livrare în 24 de ore și verifică termenul pe pagina magazinului."),
        ],
        "biletele": [
            "Am verificat lista. Ai fost destul de cuminte. La limită, dar destul. — Moș Nicolae",
            "Ghetuța a fost lustruită? Nu. Primești totuși cadou. Asta e iubire. — M.N.",
            "Nuieluța am lăsat-o acasă anul ăsta. Nu te obișnui. — Moș Nicolae",
            "Pentru cel mai bun coleg: ca să ai ce face în ședințele care puteau fi un e-mail.",
            "Moș Nicolae a zis că meriți ceva mic. Eu am zis că meriți tot. Am negociat la ăsta.",
            "Mandarina e de la Moș Nicolae. Cadoul e de la mine. Pupicul e la cerere.",
            "Știu că ești mare de-acum. Dar Moș Nicolae nu verifică buletinul.",
            "Instrucțiuni: zâmbește, mănâncă mandarina, nu spune nimănui că ai primit înaintea lor.",
            "Pentru mama, care punea dulciuri în ghetuța mea și se prefăcea surprinsă. Acum e rândul meu.",
            "Avans pentru Crăciun. Restul vine pe 25, dacă te porți frumos până atunci.",
        ],
        "manual": {},
        "emag": ("Mai multe idei de Moș Nicolae pe eMAG", "https://l.profitshare.ro/l/17585460"),
}


GHIDURI = [
    GHID_MOS_NICOLAE,
    {
        "slug": "cadouri-craciun-sub-100-lei-pentru-ea",
        "titlu": "Cadouri de Crăciun sub 100 de lei pentru ea (care nu arată deloc a 100 de lei)",
        "titlu_scurt": "Cadouri de Crăciun sub 100 lei pentru ea",
        "titlu_seo": "Cadouri de Crăciun sub 100 lei pentru ea – 20 de idei care par scumpe",
        "descriere": "Idei de cadouri de Crăciun sub 100 de lei pentru iubită, soție, mamă sau colegă: bijuterii, "
                     "răsfăț și lucruri utile, alese pe tipuri de femei. Plus cum afli mărimea inelului fără să te dai de gol.",
        "publicat": "2026-11-28",
        "eticheta": "Pentru ea",
        "pret_max": 100,
        "poza_principala": ("manual", "pb-mira"),
        "intro": """
<p>Ai un buget de 100 de lei și o misiune: să cumperi ceva care să o facă să zâmbească, nu să spună politicos
„a, mersi, e… practic”. Vestea bună: 100 de lei e exact bugetul la care se ascund cele mai bune cadouri.
Destul cât să fie ceva frumos, destul de puțin cât să nu pară că încerci să-ți ceri scuze pentru ceva.</p>
<p>Am împărțit ideile pe <strong>tipuri de femei</strong>, pentru că „cadou pentru ea” e la fel de vag ca
„mâncare pentru cină”. Găsește-o pe a ta mai jos, alege, și ai rezolvat Crăciunul înainte de cafea.</p>
""",
        "test_titlu": "Testul de 10 secunde: ce fel de „ea” e?",
        "sectiuni": [
            {
                "id": "nu-vrea-nimic",
                "titlu": "Cea care spune „nu-mi lua nimic”",
                "subtitlu": "Traducere: „ia-mi ceva mic, frumos și care arată că ai fost atent”.",
                "intro": "<p>Nicio femeie din istorie n-a fost supărată pe o bijuterie mică și bine aleasă. "
                         "Regula de aur: <strong>simplu bate strălucitor</strong>. Un model discret o să-l poarte "
                         "zilnic; unul spectaculos o să stea în cutie „pentru o ocazie”.</p>",
                "produse": [
                    {"manual": "pb-luciana", "text": "Arată ca un inel de zece ori mai scump. Îl poate purta singur sau "
                     "lângă verighetă. Mărimea? Citește trucul de agent secret de mai jos, înainte să comanzi."},
                    {"manual": "pb-mira", "text": "Perlele sunt blugii bijuteriilor: merg cu orice, de la ședința de luni "
                     "la masa de Crăciun cu soacra. Imposibil să greșești cu ele."},
                    {"manual": "pb-floris", "text": "Pentru cea care zice că „nu poartă bijuterii”, dar se uită lung la "
                     "cerceii altora. Mici, luminoși, de purtat zilnic."},
                    {"feed": ("Mindblower.ro", "3501"), "nume": "Cutie pentru bijuterii „My love” + brățară 7 Chakre", "text": "Două cadouri la preț de unul: o cutiuță pentru bijuterii "
                     "(unde vor sta, sperăm, și cele de la tine) plus o brățară. Bun și ca „cadou de rezervă” pentru colega uitată."},
                ],
            },
            {
                "id": "regina-pledului",
                "titlu": "Regina pledului",
                "subtitlu": "Îi e frig din octombrie până în mai și consideră canapeaua un stil de viață.",
                "intro": "<p>Pentru ea, cadoul perfect nu impresionează pe Instagram, ci la 21:30, într-o marți. "
                         "Gândește-te: <em>ce ar face seara ei cu 10% mai bună?</em></p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "4486"), "nume": "Pătură fosforescentă cu fazele Lunii, roz", "text": "O pătură moale care strălucește în întuneric cu fazele Lunii. "
                     "Ziua: pătură. Noaptea: planetariu personal. Câștigă orice concurs de „cel mai comentat cadou”."},
                    {"feed": ("Mindblower.ro", "15033"), "nume": "Set 4 bombe de baie „Răsfăț de Crăciun”", "text": "Bombe de baie cu temă de iarnă. Dacă are cadă, ai câștigat; "
                     "dacă nu, i-ai dat un motiv excelent să-și ia una."},
                    {"feed": ("Mindblower.ro", "4323"), "nume": "Mască de dormit „Five more minutes”", "text": "Pe mască scrie „Five more minutes”. E, practic, un cadou "
                     "și o declarație de principii. Cel mai ieftin lux de pe listă."},
                    {"feed": ("Mindblower.ro", "14620"), "nume": "Infuzor de ceai din sticlă", "text": "Pentru cea care are 14 feluri de ceai și niciunul la plic. "
                     "Pune frunzele, toarnă apa, se uită cum se colorează: terapie gratuită."},
                    {"feed": ("Mindblower.ro", "4222"), "nume": "Cana Flower Blossom", "text": "O cană cu flori, pentru că dimineața are nevoie de ajutor. "
                     "Pune în ea un plic de ciocolată caldă și o fundă, și ai un cadou complet."},
                ],
            },
            {
                "id": "romantica",
                "titlu": "Romantica incurabilă",
                "subtitlu": "Plânge la reclamele de Crăciun și păstrează biletele de la cinema din 2017.",
                "intro": "<p>Aici contează <strong>gestul</strong> mai mult decât obiectul. Orice alegi de mai jos, "
                         "adaugă un bilet scris de mână. Nu ai inspirație? Ai generatorul de bilețele mai jos.</p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "3060"), "nume": "Buchet romantic cu 7 trandafiri de săpun", "text": "Trandafiri din săpun care nu se ofilesc în trei zile ca "
                     "cei adevărați. Romantici, dar practici. Ca tine, sperăm."},
                    {"feed": ("Mindblower.ro", "3889"), "nume": "Lampă glob de cristal cu inimă", "text": "O lumină mică de noptieră, cu o inimă în glob de cristal. "
                     "Cadou de „m-am gândit la tine” care stă la vedere tot anul."},
                    {"manual": "pb-vanessa", "text": "Placat cu aur roz, cu piatră albastră: arată a cadou ales cu grijă, "
                     "nu a cadou luat în drum spre casă. Exact impresia pe care o vrei."},
                    {"manual": "pb-helena", "text": "Un pandantiv colorat, vesel, cu lănțișor inclus. Perfect dacă stilul ei "
                     "e mai degrabă „artistă” decât „avocată”."},
                    {"manual": "pb-marlene", "text": "Cercei lungi cu perle pentru Revelion. Bonus: îi rezolvi și întrebarea "
                     "„ce port la petrecere?”, care, statistic, apare pe 30 decembrie."},
                ],
            },
            {
                "id": "agenda",
                "titlu": "Cea cu agendă pentru agende",
                "subtitlu": "Are liste pentru liste și un sertar special pentru pungi.",
                "intro": "<p>Pentru femeia organizată, cadoul ideal o ajută să fie <em>și mai</em> organizată. "
                         "Nu-i lua ceva decorativ fără rost: o să-l privească, o să-l catalogheze, o să-l „depoziteze”.</p>",
                "produse": [
                    {"feed": ("Mindblower.ro", "15041"), "nume": "Set cadou vintage: jurnal + pix, „Copacul vieții”", "text": "Jurnal vintage cu pix asortat. O să-l folosească pentru "
                     "rezoluțiile din 2027 și, probabil, pentru lista de cadouri de anul viitor (unde vei fi și tu)."},
                    {"feed": ("Mindblower.ro", "4393"), "nume": "Organizator de cosmetice pentru călătorie", "text": "Organizator de cosmetice pentru călătorii. Dacă are un "
                     "„neceser pentru neceserele mici”, ăsta e upgrade-ul."},
                    {"feed": ("Hotpick.ro", "CR 2169"), "nume": "Oglindă cosmetică cu LED și mărire 5x", "text": "Oglindă cu lumină LED și mărire. Pentru machiaj la ora 7 "
                     "dimineața, când lumina naturală nu s-a trezit încă."},
                ],
            },
            {
                "id": "pe-fuga",
                "titlu": "Cea mereu pe fugă",
                "subtitlu": "Bea cafeaua în mașină și răspunde la mailuri în coadă la supermarket.",
                "intro": "<p>Pentru ea, cel mai bun cadou e ceva care <strong>îi ușurează ziua</strong> și arată bine "
                         "în același timp. Practic, dar nu plictisitor.</p>",
                "produse": [
                    {"feed": ("Watch24.ro", "CEAS-10"), "nume": "Ceas de damă Geneva Crystal, auriu", "text": "Ceas auriu cu cristale, la jumătate de preț. Arată elegant "
                     "la birou și, mai important, o ajută să ajungă la timp la cina cu tine."},
                    {"feed": ("Mindblower.ro", "4152"), "nume": "Cană de cafea cu pereți dubli, 450 ml", "text": "Cană cu pereți dubli: cafeaua stă caldă, mâna stă rece, "
                     "iar ea arată de parcă își face cafeaua de specialitate acasă. Cel mai ieftin cadou bun de pe listă."},
                    {"manual": "pb-elena", "text": "Inel de argint cu piatră albastră: discret pentru birou, dar destul de "
                     "special încât colegele să întrebe „de unde e?”."},
                ],
            },
        ],
        "sectiuni_utile": [
            {
                "id": "marime-inel",
                "titlu": "Cum afli mărimea inelului fără să te dai de gol",
                "html": """
<p>Varianta ideală, demnă de un film cu spioni:</p>
<ol>
  <li><strong>„Împrumută” un inel</strong> pe care ea îl poartă pe <em>același deget</em> pentru care cumperi. Degetele de la cele două mâini pot avea mărimi diferite, deci contează.</li>
  <li>Măsoară cu o riglă <strong>diametrul interior</strong> (de la o margine interioară la cealaltă), în milimetri.</li>
  <li>Pune inelul la loc înainte să observe. Asta e partea grea.</li>
</ol>
<p>Mărimea europeană a inelului e circumferința interioară în milimetri. Orientativ:</p>
<table class="tabel">
  <thead><tr><th>Diametru interior</th><th>Mărime (EU)</th></tr></thead>
  <tbody>
    <tr><td>16 mm</td><td>50</td></tr><tr><td>16,5 mm</td><td>52</td></tr><tr><td>17 mm</td><td>53</td></tr>
    <tr><td>17,5 mm</td><td>55</td></tr><tr><td>18 mm</td><td>56–57</td></tr><tr><td>18,5 mm</td><td>58</td></tr><tr><td>19 mm</td><td>60</td></tr>
  </tbody>
</table>
<p><strong>Dacă ești între două mărimi, alege-o pe cea mai mare.</strong> Un inel puțin larg se poartă; unul strâmt
devine „inelul pe care îl țin în cutie”. Verifică și tabelul de mărimi al magazinului, pentru că modelele diferă.</p>
<p><em>Planul B:</em> cercei sau colier. Nu au mărimi, nu au riscuri, nu au interogatorii.</p>
""",
            },
            {
                "id": "greseli",
                "titlu": "5 greșeli de cadou pe care le vei evita de acum",
                "html": """
<ol class="greseli">
  <li><strong>Aparatul de bucătărie „ca să-i fie mai ușor”.</strong> Doar dacă ți l-a cerut explicit, cu link și model. Altfel, e un mesaj despre cine gătește.</li>
  <li><strong>Cântarul, crema anti-rid sau orice cu „slăbire” în nume.</strong> Nu. Pur și simplu nu.</li>
  <li><strong>Ce ți-ar plăcea ție.</strong> Dacă tu vrei căștile, cumpără-ți căștile. Separat.</li>
  <li><strong>Cumpărat pe 23 decembrie.</strong> Plătești mai mult, alegi din ce a rămas și riști să ajungă după Revelion.</li>
  <li><strong>Fără ambalaj și fără bilet.</strong> Un cadou de 60 de lei bine ambalat, cu trei rânduri scrise de mână, bate unul de 300 de lei dat în punga magazinului.</li>
</ol>
""",
            },
            {
                "id": "ambalaj",
                "titlu": "Ambalajul de 10 lei care arată de 100",
                "html": """
<ul>
  <li><strong>Hârtie kraft maro + sfoară</strong> (le găsești la orice papetărie). Arată „artizanal”, nu „ieftin”.</li>
  <li><strong>O crenguță de brad sau de cimbru</strong> prinsă sub sfoară. Miroase a Crăciun și pare că ai muncit la asta o oră.</li>
  <li><strong>O etichetă scrisă de mână</strong> cu numele ei. Scrisul tău e mai valoros decât orice fundă.</li>
  <li><strong>Pentru bijuterii:</strong> pune cutiuța într-o cutie mai mare, cu hârtie mototolită. Suspansul crește valoarea percepută cu cel puțin 40% (statistică inventată, efect real).</li>
</ul>
""",
            },
            {
                "id": "cand-comanzi",
                "titlu": "Până când comanzi ca să ajungă de Crăciun?",
                "html": """
<p>Fiecare magazin are propriile termene, scrise pe pagina produsului, la livrare. Ca regulă de bun-simț:
<strong>comandă până pe 15–18 decembrie</strong> pentru livrare prin curier, iar după 20 decembrie alege
produsele marcate „în stoc” cu livrare în 24–48 de ore. Pentru bijuterii și cadouri personalizate, mai devreme e mai bine.</p>
""",
            },
        ],
        "faq": [
            ("Ce cadou de Crăciun sub 100 de lei îi iau iubitei?",
             "Bijuteriile mici (cercei cu perle, un inel simplu) și cadourile de răsfăț (pătură, bombe de baie) sunt cele mai sigure. "
             "Alege după ce face ea seara, nu după ce e la reducere."),
            ("Ce îi iau mamei sub 100 de lei?",
             "Ceva practic și frumos: o cană bună, un ceas, o pătură caldă sau un jurnal. Mamele apreciază cadourile pe care le folosesc zilnic."),
            ("Ce cadou îi iau unei colege, fără să fie prea personal?",
             "Cana, infuzorul de ceai, organizatorul sau lampa decorativă sunt alegeri sigure. Bijuteriile și cosmeticele le lași pentru apropiați."),
            ("Ce fac dacă nu-i place cadoul?",
             "La cumpărăturile online ai, în general, 14 zile drept de retur pentru majoritatea produselor. Verifică condițiile magazinului "
             "înainte de comandă, mai ales la bijuterii și produse personalizate."),
        ],
        "biletele": [
            "Am vrut să-ți iau ceva la fel de frumos ca tine, dar n-aveau în stoc. Sper că merge și ăsta.",
            "Crăciunul ăsta, cel mai bun cadou ești tu. Dar am zis să-ți iau și ceva, ca să nu par zgârcit.",
            "Pentru femeia care mă suportă 365 de zile pe an. Asta e doar un avans.",
            "Știu că ai zis să nu-ți iau nimic. Te-am ignorat cu toată dragostea.",
            "Ți-am luat ceva mic, ca să ai loc pentru toate complimentele pe care ți le fac.",
            "Instrucțiuni: deschide, zâmbește, spune-mi că sunt cel mai bun. Ordinea contează.",
            "Dacă îl porți, înseamnă că ți-a plăcut. Dacă nu, eu oricum am dat dovadă de gust.",
            "Moș Crăciun mi-a cerut sfatul. I-am zis că meriți tot. A zis că bugetul e 100 de lei.",
            "Pentru mama mea, care m-a învățat să ofer cadouri. Uite, a funcționat.",
            "Pentru cea mai bună colegă: ca să ai cu ce să-ți bei cafeaua când ședința durează prea mult.",
        ],
        "manual": {
            "pb-luciana": {"nume": "Inel tennis Luciana", "magazin": "Perfectbijoux", "pret": 42, "pret_vechi": 60,
                           "link": "https://l.profitshare.ro/l/17309362",
                           "poza": "https://c.cdnmp.net/129530482/p/m/6/inel-tennis-luciana~8385246.webp", "verificat": "28 noiembrie"},
            "pb-mira": {"nume": "Cercei cu perle Mira", "magazin": "Perfectbijoux", "pret": 59, "pret_vechi": 85,
                        "link": "https://l.profitshare.ro/l/17309366",
                        "poza": "https://c.cdnmp.net/129530482/p/m/8/cercei-cu-perle-mira~8385348.webp", "verificat": "28 noiembrie"},
            "pb-floris": {"nume": "Cercei-floare cu cristale Floris", "magazin": "Perfectbijoux", "pret": 65, "pret_vechi": 95,
                          "link": "https://l.profitshare.ro/l/17519393",
                          "poza": "https://c.cdnmp.net/129530482/p/m/2/cercei-in-forma-de-floare-cu-cristale-albe-floris~8387112.webp", "verificat": "28 noiembrie"},
            "pb-vanessa": {"nume": "Colier Vanessa, placat cu aur roz", "magazin": "Perfectbijoux", "pret": 82, "pret_vechi": 110,
                           "link": "https://l.profitshare.ro/l/17309368",
                           "poza": "https://c.cdnmp.net/129530482/p/m/1/colier-albastru-vanessa-placat-cu-aur-roz~8397131.webp", "verificat": "28 noiembrie"},
            "pb-helena": {"nume": "Pandantiv Helena cu lănțișor", "magazin": "Perfectbijoux", "pret": 93, "pret_vechi": 110,
                          "link": "https://l.profitshare.ro/l/17519396",
                          "poza": "https://c.cdnmp.net/129530482/p/m/7/pandantiv-auriu-cu-cristale-multicolore-helena-cu-lantisor~8397247.webp", "verificat": "28 noiembrie"},
            "pb-marlene": {"nume": "Cercei lungi cu perle Marlene", "magazin": "Perfectbijoux", "pret": 80, "pret_vechi": 115,
                           "link": "https://l.profitshare.ro/l/17519394",
                           "poza": "https://c.cdnmp.net/129530482/p/m/5/cercei-lungi-cu-perle-marlene~8385565.webp", "verificat": "28 noiembrie"},
            "pb-elena": {"nume": "Inel de argint cu piatră albastră Elena", "magazin": "Perfectbijoux", "pret": 84, "pret_vechi": 120,
                         "link": "https://l.profitshare.ro/l/17519395",
                         "poza": "https://c.cdnmp.net/129530482/p/m/3/inel-cu-piatra-albastra-ag925-elena~8385603.webp", "verificat": "28 noiembrie"},
        },
        "emag": ("Mai multe idei pentru ea pe eMAG", "https://l.profitshare.ro/l/17585454"),
    },
]
