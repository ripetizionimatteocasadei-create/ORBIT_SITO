// Legge da stdin un JSON [{tex, display}], scrive su stdout un JSON di stringhe HTML (KaTeX pre-renderizzato).
// Cosi' le formule sono già nell'HTML della pagina: niente JavaScript per leggerle, ottimo per la SEO.
import katex from "katex";
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const items = JSON.parse(raw);
const out = items.map(({ tex, display }) =>
  katex.renderToString(tex, { displayMode: !!display, throwOnError: true, strict: "error", output: "htmlAndMathml" })
);
process.stdout.write(JSON.stringify(out));
