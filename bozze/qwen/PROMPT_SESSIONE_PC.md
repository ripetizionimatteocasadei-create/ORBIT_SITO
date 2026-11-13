# PROMPT PER LA SESSIONE SUL PC DI MATTEO (Claude Code + Qwen locale)

Incolla tutto quello che sta sotto la linea nella sessione sul PC.

---

Ciao. **Questo prompt è per te (Claude Code), non per Qwen.** Qwen riceverà da te solo la scheda di stile e un compito alla volta. Ti affido un lavoro grosso e lungo: far scrivere **a Qwen (locale, modello MoE ~35B)** tutto il blog di **matematica** del sito di Matteo Casadei (ORBIT | RIPETIZIONI, orbitripetizioni.it), dalla 1ª alla 5ª superiore. Tu fai l'ingegnere e il revisore; **il lavoro pesante lo fa Qwen**. Obiettivo secondario, importante: **consumare il meno possibile i token di Claude**. Qwen è gratis e locale, tu no.

Non devi chiedere nulla a Matteo: dove manca un'informazione scegli il default sensato e annotalo in `DECISIONI.md`. Italiano, risposte brevi.

## 0. REGOLE NON NEGOZIABILI
1. **Nessun push, nessun deploy, niente Netlify. Mai.** Non pushare nemmeno su GitHub: la consegna è uno **zip** (sezione 8). Chi integra nel sito è un'altra sessione.
2. Non leggere né stampare file `.env`, chiavi, token. Non toccare nulla fuori dalla cartella di lavoro.
3. Nessun contenuto copiato da libri o siti. Nessun dato inventato (studenti, statistiche, recensioni, premi).
4. Mai scrivere "liceo scientifico": solo "1ª superiore", "2ª superiore", ecc.
5. Ogni numero che compare nei testi deve venire da codice (sympy). **Nessun conto a mente, né tuo né di Qwen.**
6. Se ti accorgi di consumare troppo (vedi §7), fermati, salva lo stato e scrivi cosa serve.

## 1. SETUP (una volta)
1. Clona il repo e prendi il branch con tutto il materiale (sola lettura: **non pushare**):
   `git clone https://github.com/ripetizionimatteocasadei-create/ORBIT_SITO orbit_lavoro && cd orbit_lavoro && git checkout claude/youthful-gates-kalan7`
2. Leggi, in quest'ordine (sono brevi, leggili una volta e riassumili in `lavoro/NOTE.md`, poi non rileggerli):
   - `bozze/qwen/SCHEDA_STILE_QWEN.md` (le regole che Qwen deve rispettare)
   - `bozze/REGOLE_APPRESE.md` (correzioni reali di Matteo: vincolanti)
   - `bozze/CONOSCENZE_BLOG_ORBIT.md` (metodo ORBIT, scheletro del post, SEO, controlli §9)
   - `bozze/indice/albero.txt` (area `# Matematica`: 40 guide, 230 lezioni) e `bozze/indice/mappa_url.csv` (URL e slug già decisi)
3. Studia il post modello già pronto: `blog/come-risolvere-equazioni-secondo-grado/index.html`, e gli strumenti che l'hanno prodotto: `bozze/strumenti/costruisci_post.py`, `controlli_post.py`, `katex_render.mjs`, `assets/js/equazione2.js` (+ `verifica_widget.py`), `assets/css/v2-blog-math.css`, `assets/vendor/katex/`. **Quel post è il "gold standard"**: stessa struttura, stesso stile, stessa qualità.
4. **Qwen lo sai già lanciare e usare** (script MoE ottimizzato che hai creato in precedenza): usa quello, non reinventarlo e non rifare prove inutili. Controlla solo tre cose e annotale in `lavoro/NOTE.md`: contesto reale per sessione (aspettati 32k), velocità (circa 200 t/s in lettura, 45 t/s in scrittura), e se esiste una modalità senza ragionamento lungo (usala se c'è). Da qui in poi "Qwen" significa quel server locale, chiamato da script che lancio **tu**: Qwen non vede mai questo prompt, riceve solo la scheda di stile e il compito del singolo pezzo.
5. Installa solo ciò che serve: `sympy`, `numpy`, `node` + `katex` (come in `bozze/strumenti/package.json`). **Manim** solo se si installa senza fatica (vedi §4.5); altrimenti niente.

## 2. COME SI LAVORA CON UN MODELLO CON POCA MEMORIA (32k token)
Qwen **non deve mai scrivere un post intero**. Un post si costruisce a **pezzi piccoli e indipendenti**, uno per chiamata:
- Ogni chiamata è **a freddo**: nessuna cronologia. Contiene: la SCHEDA DI STILE (identica, copiata da `bozze/qwen/SCHEDA_STILE_QWEN.md`) + il compito del pezzo + il minimo contesto (scaletta del post + ultime 3 righe del pezzo precedente) + **un solo esempio** del pezzo preso dal gold standard. **Tetto: 6.000 token di ingresso, 1.200 di uscita.** Se un pezzo ne richiede di più, spezzalo.
- Temperatura bassa (0,2–0,4). Formato di uscita **rigido** (blocchi con delimitatori, oppure JSON con schema), validato da codice. Se non valida: rimanda a Qwen **solo il pezzo sbagliato + il messaggio d'errore** (massimo 3 tentativi), poi segna il pezzo come "da rivedere".
- Qwen **non scrive HTML, CSS, JavaScript, né calcoli**. Scrive solo testo con markup minimo (§ scheda), formule LaTeX, segnaposto `{{nome}}` e **specifiche** dei componenti interattivi (§4).
- Salva ogni pezzo in un file (`lavoro/<slug>/pezzi/NN_nome.txt`) così un riavvio non rifà niente. Stato globale in `lavoro/stato.json` (post fatti, in corso, falliti).

### Pezzi di un post (lezione da 900–1.400 parole)
1. `scaletta` — JSON: keyword principale e secondarie, intento di ricerca, difficoltà, prerequisiti, 3 domande-guida, 3 errori tipici, l'esempio svolto scelto (testo del problema con segnaposto), tipo di interattività scelto (§4).
2. `risposta_breve` (60–90 parole, con la parola chiave nelle prime righe) · 3. `aggancio` (problema concreto + domande aperte + invito a provare) · 4. `bridging` · 5. `formalizzazione` (definizione/formula con significato di ogni parte e condizioni) · 6. `esempio_svolto` (ad alta voce: stima, passi, controllo) · 7. `prova_tu` (3 esercizi con indizio 1, indizio 2, soluzione) · 8. `errori` (3–4: cosa succede, perché, come accorgersene) · 9. `problema_nuovo` (transfer: non assomiglia agli esempi) · 10. `in_breve` + "se ti blocchi" · 11. `faq` (3–4) · 12. `meta` (title ≤60, description ≤155, slug dalla mappa).
Le **guide** (pagine pilastro, 1.500–2.000 parole) si scrivono **dopo** le loro lezioni: introduzione, "come si studia questo argomento", mappa delle lezioni (elenco con link **generato dal codice**), errori trasversali, FAQ. Qwen scrive solo i pezzi di testo; l'elenco lo fa il codice. URL guida: `/blog/guida-<slug-argomento>/`.

## 3. NUMERI E CALCOLI: IL CODICE, NON QWEN
- Per ogni post Qwen produce una sezione `calcoli`: poche righe Python/sympy che definiscono le variabili usate nei testi (es. `a,b,c=2,-5,-3` · `D=b**2-4*a*c` · `sol=solve(...)`). Il tuo builder le esegue in un ambiente ristretto (solo sympy, niente import liberi, niente I/O), e sostituisce i segnaposto `{{D}}`, `{{sol[0]}}` (in LaTeX nelle formule, in italiano con la virgola nel testo).
- **Coerenza**: il testo del problema si costruisce dalle **stesse variabili** che si usano per risolverlo. Ogni soluzione si **verifica per sostituzione** nel problema (check automatico). Se non coincide: il post non passa.
- **Audit dei numeri**: un controllo cerca numeri scritti a mano nel testo che non provengono dai segnaposto né dalle variabili dichiarate; li segnala per la revisione.
- Costruisci il builder **generalizzando** `costruisci_post.py` (che oggi è specifico del post sulle equazioni) in un builder che prende una cartella di pezzi e produce `out/<slug>/index.html` con lo stesso aspetto del gold standard (stesso `<head>`, JSON-LD BlogPosting + BreadcrumbList + FAQPage, canonical, og, link interni, formule KaTeX pre-renderizzate, **HTML completo senza contenuti caricati via JS**).
- Link interni (3–6 per lezione): guida di appartenenza, lezione precedente/successiva, 1–2 lezioni correlate, sito (`../../index.html#materie`). Usa **solo URL che esistono nella mappa**.

## 4. INTERATTIVITÀ: OGNI POST DEVE TRATTENERE LO STUDENTE SUL SITO
Costruisci **una sola volta** una piccola libreria di componenti (JS puro, senza dipendenze, funzionanti da telefono, tasti ≥44px, accessibili), ciascuno **verificato con sympy** come `verifica_widget.py` ha fatto per lo slider della parabola. Qwen **non scrive codice**: compila una **specifica JSON** che il builder trasforma in componente. Componenti minimi:
1. **grafico con slider** — funzione in un parametro/più parametri (espressione validata con un parser sicuro, niente `eval`), lettura numerica (zeri, vertice, ecc.), come `equazione2.js` ma generico.
2. **esercizio infinito** — modello di esercizio con parametri casuali (intervalli/liste), risposta attesa calcolata, campo di risposta, pulsante "Controlla", indizi a scalini, pulsante "Nuovo esercizio". È il componente che fa restare gli studenti: usalo in quasi ogni lezione.
3. **quiz a scelta** — domanda, 3–4 opzioni, per ogni opzione sbagliata la spiegazione dell'errore tipico che l'ha prodotta ("errore normalizzato").
4. **passo-passo** — svolgimento a rivelazione progressiva dei passi (i passi sono già calcolati dal codice).
5. **animazione** — Manim solo se installato bene **e** solo per le guide/lezioni segnate `M` nell'albero (clip 20–40 s, < 2 MB, con trascrizione nel testo). Altrimenti animazione CSS/SVG leggera, oppure niente: **non perdere tempo**.
Regole: ogni lezione ha **almeno un componente interattivo**; ogni guida ha **almeno due tipi diversi + un "test finale" di 5 domande generate** con punteggio. Tutti i componenti hanno un'alternativa testuale statica già nell'HTML (SEO e senza JS). Un test automatico confronta ciò che mostrano con sympy (come `verifica_widget.py`).

## 5. CONTROLLI AUTOMATICI (il tuo `controlli_post.py` esteso)
Ogni post, prima di arrivare a te, deve superare: frontmatter completo; un solo H1; title ≤60 e description ≤155; keyword nei punti giusti; parole nel range; link interni esistenti; `alt` su tutte le immagini; formule compilate da KaTeX in modalità strict; calcoli e soluzioni verificati; audit dei numeri; **parole vietate** (banale, ovvio, ovviamente, facile, "è semplice", "liceo scientifico"…); interiezioni solo whitelist e ≤1; ≤1 esclamativo; presenza delle sezioni chiave; **anti-copia** (sequenze di 8 parole uguali a fonti note e agli altri post); **anti-duplicato** tra post (stessa keyword → conflitto); almeno un componente interattivo. Se un controllo fallisce: il codice decide quale pezzo rifare e lo rimanda a Qwen con il motivo (max 3 giri), senza coinvolgerti.

## 6. IL TUO FILTRO DI REVISIONE (le 4 domande di Matteo)
Solo dopo che un post ha passato i controlli automatici, **tu** lo valuti, in **modalità compatta**: non leggere l'HTML. Leggi un **digest** generato dal codice (≈1.000–1.500 token): titolo, risposta breve, aggancio, formalizzazione, i passi dell'esempio, le domande di "prova tu", i titoli degli errori, il problema nuovo, l'elenco dei componenti interattivi con i loro numeri, e l'esito dei controlli. Dai un punteggio **0–2** a ciascuna domanda:
1. **È chiaro?** Uno studente di quella classe capisce ogni passaggio? Niente buchi logici, niente frasi vaghe, niente elenchi telegrafici.
2. **Matteo lo scriverebbe così?** Tono (tu, diretto, caldo), frasi corte, lessico preciso, nessuna parola vietata, rispetto di `REGOLE_APPRESE.md`, nessuna colpa data allo studente.
3. **Rispetta il Metodo ORBIT?** Prima il ragionamento poi la regola; domande aperte; stima prima e controllo dopo; l'errore come informazione; minima assistenza (indizi a scalini); chiusura con "spiegalo in tre frasi".
4. **Fa restare lo studente sul sito?** C'è almeno un componente interattivo che serve davvero (non decorativo)? Esercizio infinito/quiz/grafico con slider ben scelti per quel tema? C'è qualcosa da fare dopo la lettura?
**Esito:** pubblicabile se somma ≥ 7/8 e nessun 0. Altrimenti **non riscrivere tu**: scrivi una nota di correzione **breve e mirata** (pezzo → cosa cambiare → perché) e rimanda **quel pezzo** a Qwen. Riscrivi tu solo correzioni di poche parole. Se una stessa critica si ripete, **aggiungila alla SCHEDA DI STILE** (e a `lavoro/REGOLE_NUOVE.md`): così Qwen impara e tu consumi meno. Ogni 10 post, controlla a campione (1 su 5) un post "pubblicabile" leggendolo per intero, per accorgerti di derive.
Qualunque **errore matematico** è un blocco automatico: il post non esce.

## 7. BUDGET DEI TUOI TOKEN (regole ferree)
- Non rileggere file già letti: usa `lavoro/NOTE.md`. Non incollare HTML lunghi nella conversazione. Niente ragionamenti lunghi: decidi e annota.
- Lavora a **lotti**: lancia Qwen in background su tutta la coda (script a riga di comando) e tu intervieni solo quando c'è un digest da valutare o un errore ripetuto. Valuta i digest **in blocchi** (es. 5 post per volta, un solo messaggio).
- Tetto indicativo: ≤ 3.000 token tuoi per post (digest + giudizio + note). Se la media supera 5.000, fermati, scrivi in `lavoro/BUDGET.md` dove stai consumando e cambia strategia (più controlli automatici, meno giudizio a mano).
- Per i controlli ripetitivi usa **script**, non la tua attenzione.

## 8. ORDINE DI LAVORO E CONSEGNA
**Fase A — Ingegneria (una volta).** Setup, builder generico, libreria di componenti con i test sympy, harness per Qwen (coda, retry, stato, digest). Quando funziona, scrivi `lavoro/PRONTO.md` (3 righe).
**Fase B — Pilota di 3 post** (uno di algebra, uno di geometria analitica, uno di analisi). Per ognuno: tempo totale, token di ingresso/uscita di Qwen, numero di retry, punteggio delle 4 domande. Scrivi `lavoro/PILOTA.md`. Se la media è < 7/8 o servono troppi retry, correggi scheda e prompt dei pezzi (massimo 2 giri) **prima** di continuare.
**Fase C — Produzione.** Tutta l'area `# Matematica` di `bozze/indice/albero.txt` in ordine, dalla 1ª alla 5ª superiore: per ogni argomento prima le **lezioni**, poi la **guida**. Salta ciò che è già fatto (✓: "Come risolvere le equazioni di secondo grado"). Riprendi sempre da `stato.json`.
**Consegna a checkpoint, per livello** (1ª, 2ª, 3ª, 4ª, 5ª): uno zip `orbit_mat_<livello>.zip` con:
- `blog/<slug>/index.html` per ogni post pronto (percorsi relativi identici al gold standard);
- `assets/` **solo ciò che serve e non esiste già** (js dei componenti, css, immagini/video/manim);
- `MANIFEST.json`: per ogni post slug, titolo, description, keyword, livello, argomento, guida di appartenenza, link interni, punteggi, formati interattivi, data;
- `RAPPORTO_<livello>.md`: quanti post, quali scartati e perché, tempi, token Qwen e tuoi, regole nuove imparate, dubbi;
- `REGOLE_NUOVE.md` (da portare in `REGOLE_APPRESE.md` del repo).
**Non pushare.** Alla fine di ogni livello manda una notifica push a Matteo (se hai lo strumento), scrivi dove si trova lo zip e **continua** con il livello dopo senza aspettare risposta, a meno che il budget (§7) ti dica di fermarti.

## 9. CHE COSA CONSEGNO IO (la sessione cloud) DOPO
Matteo mi carica lo zip. Io: aggiorno `blog/index.html`, sitemap, robots, feed RSS, controllo link e canonical, faccio gli ultimi controlli, committo e pusho **solo su GitHub** (mai Netlify). Per questo ogni file nello zip deve essere **già nel formato definitivo**.

## 10. PRIMA DI INIZIARE
Riassumimi in **10 righe** cosa hai capito e come pensi di strutturare harness e componenti, poi parti senza aspettare risposta. Se qualcosa nel repo contraddice questo prompt, vince il repo per i fatti (file, percorsi), questo prompt per le regole.
