# Regole apprese da Matteo (da leggere PRIMA di scrivere un post)

Questo file si aggiorna a ogni revisione. Vale insieme a `CONOSCENZE_BLOG_ORBIT.md`; se c'è un conflitto, vince questo (è più recente e viene da correzioni reali).
Fonte di ogni regola: correzioni e note fatte da Matteo nello strumento di revisione o scritte in chat. Esempi "prima → dopo" tratti dal post sulle equazioni di secondo grado (revisione r1, 13/11/2026).

## A. Scrittura: cosa Matteo corregge

1. **Mai frasi vaghe che non dicono cosa guardare.** Se una frase non si capisce, meglio toglierla che spiegarla.
   - ✗ «…e guarda com'è fatto:» → ✓ (tolta) «…Poi ci sono tre casi:»
2. **Ogni passaggio logico deve essere esplicito.** Quando si passa da "provo a tentativi" a "serve un metodo", dire in ordine: problema → perché i tentativi non bastano → cosa serve. Non lasciare il lettore a ricostruire la connessione (nota di Matteo: «non si capisce la connessione logica, cosa vuoi dire???»).
2b. **Non essere stringato dove il concetto è nuovo.** Un elenco telegrafico ("Due incontri, uno solo, nessuno") va sviluppato: un punto per caso, con la spiegazione e il collegamento (Δ>0, Δ=0, Δ<0).
3. **Parole del mondo dello studente, tra virgolette curve, per i termini tecnici.**
   - ✗ «in parole generali» → ✓ «in “matematichese”»
   - ✗ «(la lettera greca delta)» → ✓ «(la lettera greca “delta”)»
4. **Verbi diretti, niente "sta" come ausiliare vago.**
   - ✗ «l'incognita sta al quadrato» → ✓ «l'incognita è al quadrato»
5. **Nominare l'oggetto per intero la prima volta.**
   - ✗ «Si chiama di secondo grado» → ✓ «Si chiama equazione di secondo grado»
6. **Frasi più dirette e meno solenni.**
   - ✗ «Il metodo parte da una regola di ordine:» → ✓ «Il metodo parte da qui:»
   - ✗ «Ti scrivo anche cosa penso mentre lo faccio.» → ✓ «Ti scrivo anche il ragionamento che bisogna fare.» (preferire "il ragionamento che bisogna fare" a "cosa penso")
7. **Non ripetere ciò che è già detto vicino.** Tolto «con il loro segno» dove il segno è già stato detto; usare «(occhio al segno)» nella forma breve tra parentesi quando serve il richiamo.
8. **Lessico matematico preciso quando serve (anche se più tecnico).** Matteo preferisce termini corretti: «ordinata del punto di intersezione con l'asse y», «parabola rivolta verso l'alto», «intersezione in y negativa» invece di immagini approssimative («bocca verso l'alto», «per x=0 il valore è sotto lo zero»).
   - Conseguenza: usare il lessico preciso anche nei testi alternativi (alt) e nelle didascalie.
9. **Non dare la colpa al lettore.** Impersonale, non «il tuo errore».
   - ✗ «Con il tuo errore verrebbe…» → ✓ «Con questo errore verrebbe…»
10. **Rileggere la grammatica, anche dopo le sue modifiche.** Nelle correzioni di Matteo restano a volte piccoli refusi (verbo mancante, concordanza). Li sistemo e glielo dico in una riga, senza cambiare il senso.
    - es. «la parabola rivolta verso l'alto» → «la parabola è rivolta verso l'alto»; «un'abitudine sbagliato» → «un'abitudine sbagliata».

## B. Direzione dei contenuti (decisioni di Matteo)

- Il blog serve a **prolungare l'interazione sul sito** e a mostrare il metodo ORBIT: ogni post deve dare "qualcosa da fare" (grafici, slider, esercizi con aiuti).
- **Piano**: guide complete di **matematica e fisica dalla 1ª alla 5ª superiore**, con gli argomenti del programma più completo (quello dei licei scientifici) **senza scrivere mai "liceo scientifico"**; in parallelo **università**: Analisi 1, Algebra lineare, Fisica. Dettaglio in `bozze/PIANO_EDITORIALE.md`.
- **Simulazioni** con slider quando servono; **Manim** sì ma solo dove aiuta (1 post su 3 circa); **Remotion** per ora no.
- Strumento di lavoro: la **pagina di revisione** (modifica il testo, note «sviluppa di più…», pulsante Vai).

## C. Regole operative

- **Netlify: nessun push, nessun deploy**, mai, salvo ordine esplicito di Matteo. Deploy a lotti, decisi da lui (crediti limitati).
- **GitHub: sì**, commit e push solo sul branch assegnato alla sessione.
- Avvisare con **notifica push** sul telefono quando un lavoro lungo è finito.
- Risposte brevi, in italiano semplice; domande solo se non si può decidere da soli.
- Dati su Matteo (studenti, anni di esperienza) da verificare sul sito: oggi il sito dice 50+ studenti e 6 anni, le conoscenze dicono ~40 e 5.

## D. Registro delle revisioni

| Data | Post | Esito | Cosa ho imparato |
|---|---|---|---|
| 13/11/2026 | Equazioni di secondo grado (r1) | 9 modifiche + 4 note, applicate | regole A1–A10 |

Le correzioni originali (JSON) sono in `bozze/correzioni/`.

- 13/11/2026: Matteo si fida delle correzioni applicate e non rilegge il post. Quindi prima di dire "fatto" ricontrollo io ogni punto delle sue note (e le frasi vicine con lo stesso difetto).
