(function () {
  const allowed = /^https:\/\/www\.amiens\.fr\//;
  if (!allowed.test(window.location.href)) {
    return;
  }

  if (document.getElementById("amiens-assistant-overlay")) {
    return;
  }

  const STYLE = `
    :root {
      color-scheme: light dark;
      --assistant-bg: rgba(18, 18, 18, 0.92);
      --assistant-border: rgba(255, 255, 255, 0.12);
      --assistant-text: #f9fafb;
      --assistant-muted: rgba(249, 250, 251, 0.7);
      --assistant-accent: #3b82f6;
      --assistant-accent-hover: #2563eb;
    }

    #assistant-toggle {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2147483000;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      border-radius: 999px;
      border: 1px solid var(--assistant-border);
      background: var(--assistant-bg);
      color: var(--assistant-text);
      cursor: pointer;
      box-shadow: 0 12px 36px -16px rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(16px);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
        "Helvetica Neue", sans-serif;
    }

    #assistant-toggle:hover {
      transform: translateY(-2px);
      box-shadow: 0 16px 36px -16px rgba(37, 99, 235, 0.45);
    }

    #assistant-overlay {
      position: fixed;
      inset: 16px;
      max-width: min(520px, 92vw);
      margin-left: auto;
      z-index: 2147483646;
      display: none;
      flex-direction: column;
      border-radius: 18px;
      background: var(--assistant-bg);
      border: 1px solid var(--assistant-border);
      color: var(--assistant-text);
      box-shadow: 0 24px 64px -32px rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(20px);
      overflow: hidden;
      font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
        "Helvetica Neue", sans-serif;
    }

    #assistant-overlay.active {
      display: flex;
    }

    #assistant-overlay .assistant-header {
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--assistant-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    #assistant-overlay h1 {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    #assistant-overlay .assistant-close {
      border: none;
      background: transparent;
      color: var(--assistant-muted);
      font-size: 1.125rem;
      cursor: pointer;
      transition: color 0.2s ease;
    }

    #assistant-overlay .assistant-close:hover {
      color: var(--assistant-text);
    }

    #assistant-overlay .assistant-main {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 20px 24px 24px;
      height: 100%;
    }

    #assistant-overlay textarea {
      min-height: 96px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--assistant-border);
      background: rgba(255, 255, 255, 0.04);
      color: var(--assistant-text);
      resize: vertical;
      font: inherit;
    }

    #assistant-overlay textarea:focus {
      outline: 2px solid rgba(59, 130, 246, 0.35);
      outline-offset: 2px;
    }

    #assistant-overlay button[type="submit"] {
      align-self: flex-end;
      padding: 10px 18px;
      border-radius: 999px;
      background: var(--assistant-accent);
      color: #fff;
      border: none;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    #assistant-overlay button[type="submit"]:hover {
      background: var(--assistant-accent-hover);
    }

    #assistant-overlay button[type="submit"]:disabled {
      background: rgba(59, 130, 246, 0.4);
      cursor: not-allowed;
    }

    #assistant-overlay .assistant-output {
      display: none;
      border-radius: 12px;
      padding: 16px 18px;
      border: 1px solid var(--assistant-border);
      background: rgba(255, 255, 255, 0.04);
      line-height: 1.55;
      white-space: pre-wrap;
    }

    #assistant-overlay .assistant-output article {
      margin: 0;
    }

    #assistant-overlay .assistant-output article + hr {
      margin: 16px 0;
      border: 0;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    #assistant-overlay .assistant-output article.assistant-suggestion header,
    #assistant-overlay .assistant-output article.assistant-followup header,
    #assistant-overlay .assistant-output article.assistant-alternatives header {
      font-weight: 600;
      margin-bottom: 8px;
    }

    #assistant-overlay .assistant-output article.assistant-suggestion footer,
    #assistant-overlay .assistant-output article.assistant-alternatives footer {
      margin-top: 12px;
      color: var(--assistant-muted);
      font-style: italic;
    }

    #assistant-overlay .assistant-output article.assistant-followup {
      border-radius: 10px;
      padding: 14px;
      background: rgba(59, 130, 246, 0.08);
      border: 1px dashed rgba(59, 130, 246, 0.35);
    }

    #assistant-overlay .assistant-output article.assistant-alternatives ul {
      margin: 0;
      padding-left: 18px;
    }

    #assistant-overlay .assistant-output article.assistant-alternatives li + li {
      margin-top: 6px;
    }

    #assistant-overlay .assistant-output .source-link {
      font-weight: 600;
    }

    #assistant-overlay .assistant-output .assistant-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      font-size: 0.95rem;
      background: rgba(17, 94, 205, 0.08);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 10px;
      overflow: hidden;
    }

    #assistant-overlay .assistant-output .assistant-table th,
    #assistant-overlay .assistant-output .assistant-table td {
      padding: 8px 10px;
      border-bottom: 1px solid rgba(59, 130, 246, 0.18);
      text-align: left;
    }

    #assistant-overlay .assistant-output .assistant-table th {
      width: 45%;
      font-weight: 600;
      color: var(--assistant-accent);
    }

    #assistant-overlay .assistant-output .assistant-table tr:last-child th,
    #assistant-overlay .assistant-output .assistant-table tr:last-child td {
      border-bottom: none;
    }

    #assistant-overlay .assistant-output .assistant-bullet-list {
      margin: 8px 0 0;
      padding-left: 18px;
      display: grid;
      gap: 6px;
    }

    #assistant-overlay .assistant-output .assistant-snippet {
      margin-top: 6px;
    }

    #assistant-overlay .assistant-output .assistant-alignment {
      margin: 10px 0 0;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 0.88rem;
      line-height: 1.4;
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.2);
      color: var(--assistant-muted);
    }

    #assistant-overlay .assistant-output .assistant-alignment.assistant-alignment--info {
      background: rgba(234, 179, 8, 0.12);
      border-color: rgba(234, 179, 8, 0.3);
      color: #fbbf24;
    }

    #assistant-overlay .assistant-output .assistant-alignment.assistant-alignment--warn {
      background: rgba(220, 38, 38, 0.12);
      border-color: rgba(220, 38, 38, 0.35);
      color: #fca5a5;
    }

    #assistant-overlay .assistant-output .assistant-alignment.assistant-alignment--ok {
      background: rgba(34, 197, 94, 0.12);
      border-color: rgba(34, 197, 94, 0.3);
      color: #86efac;
    }

    #assistant-overlay .assistant-output .assistant-bullet-list li {
      line-height: 1.4;
    }

    #assistant-overlay a {
      color: var(--assistant-accent);
      text-decoration: none;
    }

    #assistant-overlay a:hover {
      text-decoration: underline;
    }

    #assistant-overlay .assistant-info {
      font-size: 0.78rem;
      color: var(--assistant-muted);
      text-align: center;
    }

    @media (max-width: 680px) {
      #assistant-overlay {
        inset: 0;
        border-radius: 0;
        max-width: none;
      }
    }
  `;

  const HTML = `
    <button id="assistant-toggle" type="button" aria-expanded="false">
      Assistant Enfance Amiens
    </button>
    <aside id="assistant-overlay" role="dialog" aria-modal="true">
      <header class="assistant-header">
        <h1>Assistant Enfance Amiens</h1>
        <button class="assistant-close" type="button" aria-label="Fermer">✕</button>
      </header>
      <main class="assistant-main">
        <label for="assistant-question">Pose une question :</label>
        <textarea
          id="assistant-question"
          placeholder="Exemple : Quel est le prix de la cantine pendant les vacances de Noël ?"
        ></textarea>
        <button id="assistant-submit" type="submit">Rechercher</button>

        <section id="assistant-answer" class="assistant-output" aria-live="polite"></section>
        <section id="assistant-sources" class="assistant-output">
          <strong>Sources :</strong>
          <ul id="assistant-sources-list"></ul>
        </section>

        <p class="assistant-info">
          Résultats calculés localement à partir d'un corpus exporté d'amiens.fr.
          Branche Cursor + CURSOR_API_KEY côté backend pour du RAG en direct.
        </p>
      </main>
    </aside>
  `;

  const styleEl = document.createElement("style");
  styleEl.textContent = STYLE;
  document.head.appendChild(styleEl);

  const wrapper = document.createElement("div");
  wrapper.innerHTML = HTML;
  document.body.appendChild(wrapper);

  const toggle = document.getElementById("assistant-toggle");
  const overlay = document.getElementById("assistant-overlay");
  const closeBtn = overlay.querySelector(".assistant-close");
  const questionInput = document.getElementById("assistant-question");
  const submitBtn = document.getElementById("assistant-submit");
  const answerEl = document.getElementById("assistant-answer");
  const sourcesEl = document.getElementById("assistant-sources");
  const sourcesList = document.getElementById("assistant-sources-list");

  let segments = [];
  const sourceUrlMap = new Map();

  const QUESTION_CORRECTIONS = [
    { pattern: /\bcentere\b/gi, replacement: "centre" },
    { pattern: /\bcentrre\b/gi, replacement: "centre" },
    { pattern: /\bcentre\s+de\s+lmoisir\b/gi, replacement: "centre de loisirs" },
    { pattern: /\blmoisirs?\b/gi, replacement: "loisirs" },
    { pattern: /\bmla\b/gi, replacement: "la" },
    { pattern: /\bferme de grace\b/gi, replacement: "Ferme de Grâce" },
    { pattern: /\bgrace\b/gi, replacement: "grâce" },
    { pattern: /\bhorraires\b/gi, replacement: "horaires" },
    { pattern: /\bhoraires?\s+d'ouverture\b/gi, replacement: "horaires d'ouverture" },
    { pattern: /\bcantine\b/gi, replacement: "cantine" },
    { pattern: /\bcentres?\s+de\s+loisirs?\b/gi, replacement: "centre de loisirs" },
  ];

  const PROPER_CASE_FIXES = [
    { pattern: /\bferme de grâce\b/gi, replacement: "Ferme de Grâce" },
    { pattern: /\bla ferme de grâce\b/gi, replacement: "la Ferme de Grâce" },
    { pattern: /\bde la ferme de grâce\b/gi, replacement: "de la Ferme de Grâce" },
    { pattern: /\bdu ferme de grâce\b/gi, replacement: "du centre de loisirs de la Ferme de Grâce" },
    { pattern: /\bd'amiens\b/gi, replacement: "d'Amiens" },
  ];

  function applyCorrections(value, corrections) {
    if (!value) return value;
    return corrections.reduce(
      (acc, { pattern, replacement }) => acc.replace(pattern, replacement),
      value
    );
  }

  toggle.addEventListener("click", () => {
    const isOpen = overlay.classList.toggle("active");
    toggle.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) {
      questionInput.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    overlay.classList.remove("active");
    toggle.setAttribute("aria-expanded", "false");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      overlay.classList.remove("active");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  const corpusUrl = chrome.runtime.getURL("data/corpus_segments.json");

  function normalizeSourceKey(value) {
    return (value || "")
      .toLowerCase()
      .trim()
      .replace(/\\/g, "/")
      .replace(/[#?].*$/, "")
      .replace(/\.[^.]+$/, "")
      .replace(/__.+$/, "")
      .replace(/[^a-z0-9]+/g, "-");
  }

  function indexSources(data) {
    sourceUrlMap.clear();
    for (const segment of data) {
      if (!segment) continue;
      const baseKeys = new Set();
      if (segment.source) baseKeys.add(normalizeSourceKey(segment.source));
      if (segment.label) baseKeys.add(normalizeSourceKey(segment.label));
      if (segment.url) {
        for (const key of baseKeys) {
          if (key) {
            sourceUrlMap.set(key, segment.url);
          }
        }
      }
    }
  }

  async function loadSegments() {
    const response = await fetch(corpusUrl);
    if (!response.ok) {
      throw new Error("Impossible de charger le corpus local");
    }
    segments = await response.json();
    indexSources(segments);
  }

  function tokenize(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .split(/\W+/)
      .filter((token) => token.length > 2);
  }

  function levenshtein(a, b) {
    const m = a.length;
    const n = b.length;
    if (m === 0) return n;
    if (n === 0) return m;

    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1));
    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,
          dp[i][j - 1] + 1,
          dp[i - 1][j - 1] + cost
        );
      }
    }
    return dp[m][n];
  }

  function tokenMatches(queryToken, candidateToken) {
    if (!queryToken || !candidateToken) return false;
    if (candidateToken === queryToken) return true;
    if (
      candidateToken.startsWith(queryToken) ||
      queryToken.startsWith(candidateToken) ||
      candidateToken.includes(queryToken) ||
      queryToken.includes(candidateToken)
    ) {
      return true;
    }
    if (Math.abs(candidateToken.length - queryToken.length) <= 3) {
      const distance = levenshtein(queryToken, candidateToken);
      if (distance <= 2) {
        return true;
      }
    }
    return false;
  }

  function scoreSegment(questionTokens, segment) {
    const { content } = segment;
    if (!content) return 0;

    const tokens = tokenize(content);
    if (!tokens.length) return 0;

    let matches = 0;
    for (const qt of questionTokens) {
      if (tokens.some((token) => tokenMatches(qt, token))) {
        matches += 1;
      }
    }

    if (!matches) return 0;

    const uniqueTokens = new Set(tokens);
    const ratio = matches / questionTokens.length;
    const density = matches / uniqueTokens.size;

    // bonus si des termes typiques (prix/tarif) sont présents
    const pricingTokens = [
      "tarif",
      "tarifs",
      "prix",
      "cout",
      "coût",
      "cantine",
      "loisir",
      "restauration",
      "repas",
      "inscription",
    ];
    const hasPricingKeyword = tokens.some((token) => pricingTokens.includes(token));
    let bonus = hasPricingKeyword ? 0.5 : 0;
    if (/€/.test(content) || /euros?/i.test(content)) {
      const questionHasPrice = questionTokens.some((token) =>
        ["prix", "tarif", "cout", "coût", "euros"].includes(token)
      );
      if (questionHasPrice) {
        bonus += 2.5;
      } else {
        bonus += 0.5;
      }
    }

    return matches + ratio + density + bonus;
  }

  function extractSnippet(content, questionTokens) {
    const normalized = content.replace(/\s+/g, " ").trim();
    if (normalized.length <= 420) {
      return normalized;
    }

    const sentences = normalized.split(/(?<=[.?!;])\s+/);
    let bestSentence = sentences[0] || normalized.slice(0, 420);
    let bestScore = -Infinity;

    for (const sentence of sentences) {
      const sentenceTokens = tokenize(sentence);
      if (!sentenceTokens.length) continue;
      let score = 0;
      for (const qt of questionTokens) {
        if (sentenceTokens.some((token) => tokenMatches(qt, token))) {
          score += 1;
        }
      }
      if (score > bestScore) {
        bestScore = score;
        bestSentence = sentence;
      }
    }

    let snippet = bestSentence.trim();
    const needsTable = questionTokens.some((qt) =>
      ["prix", "tarif", "cout", "cantine", "loisir", "tableau"].includes(qt)
    );
    if (needsTable && !snippet.includes("€")) {
      const lines = content.split(/\n+/).map((line) => line.trim());
      const priceLines = lines.filter((line) => /€/.test(line));
      if (priceLines.length) {
        snippet = priceLines.slice(0, 4).join("\n");
      }
    }

    if (snippet.length > 420) {
      snippet = snippet.slice(0, 417).trimEnd() + "…";
    }
    return snippet;
  }

  function escapeHtml(value) {
    if (!value && value !== 0) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function reformulateIntent(question) {
    if (!question) return "cette information";
    let cleaned = question.trim().replace(/\?+$/, "");
    if (!cleaned) return "cette information";

    cleaned = applyCorrections(cleaned, QUESTION_CORRECTIONS);
    cleaned = cleaned.replace(/\s+/g, " ").trim();
    if (!cleaned) return "cette information";

    const normalized = cleaned.toLowerCase();
    let reformulated = normalized;

    const hourMatch = normalized.match(/à quelle heure\s+ouvre(?:nt)?\s+(.*)/);
    if (hourMatch) {
      let subject = hourMatch[1].trim();
      subject = applyCorrections(subject, QUESTION_CORRECTIONS);
      subject = subject
        .replace(/\bcentre de loisir\b/gi, "centre de loisirs")
        .replace(/\bloisir\b/gi, "loisirs")
        .replace(/\s+/g, " ")
        .trim();

      if (subject.startsWith("le ")) {
        subject = subject.replace(/^le\s+/, "du ");
      } else if (subject.startsWith("la ")) {
        subject = subject.replace(/^la\s+/, "de la ");
      } else if (subject.startsWith("les ")) {
        subject = subject.replace(/^les\s+/, "des ");
      } else if (!/^d[eu]/.test(subject)) {
        subject = `du ${subject}`;
      }

      subject = subject
        .replace(/\bdu la\b/gi, "de la")
        .replace(/\bdu les\b/gi, "des")
        .replace(/\bde le\b/gi, "du")
        .replace(/\s+/g, " ")
        .trim();

      reformulated = `les horaires d'ouverture ${subject}`;
    } else {
      let base = normalized;
      base = base.replace(/^merci\s+de\s+/i, "");
      base = base.replace(/^svp\s+/i, "");
      base = base.replace(/^s'il te plaît\s+/i, "");
      base = base.replace(/^peux[-\s]?tu\s+/i, "");
      base = base.replace(/^pouvez[-\s]?vous\s+/i, "");
      base = base.replace(/^je\s+cherche\s+/i, "");
      base = base.replace(/^nous\s+cherchons\s+/i, "");
      base = base.replace(/^est-ce\s+que\s+/i, "");

      base = base.replace(/^(?:quel(le|s)?\s+)?est\s+/i, "");
      base = base.replace(/^quels?\s+?sont\s+/i, "");
      base = base.replace(/^quelles?\s+?sont\s+/i, "");
      base = base.replace(/^combien\s+(co[uû]te|vaut)\s+/i, "");
      base = base.replace(/^(comment|où|quand|pourquoi|combien)\s+/i, "");

      base = base.replace(/\s+/g, " ").trim();
      reformulated = base || normalized;
    }

    reformulated = applyCorrections(reformulated, QUESTION_CORRECTIONS);
    reformulated = applyCorrections(reformulated, PROPER_CASE_FIXES);

    reformulated = reformulated
      .replace(/\bferme de grace\b/gi, "Ferme de Grâce")
      .replace(/\bcentre de loisir\b/gi, "centre de loisirs")
      .replace(/\s+/g, " ")
      .trim();

    if (!reformulated) return "cette information";
    const lowerFirst = reformulated.charAt(0).toLowerCase() + reformulated.slice(1);
    return lowerFirst;
  }

  function buildGranularityPrompt(snippet, questionTokens) {
    const base = "Souhaitez-vous que je précise un point particulier ?";
    const haystack = `${snippet || ""} ${questionTokens.join(" ")}`.toLowerCase();

    if (/\bcat[eé]g/.test(haystack) || /\bquotient\b/.test(haystack) || /\btranche\b/.test(haystack)) {
      return "Si oui, à quelle catégorie appartenez-vous ?";
    }
    if (/\b(p[eé]riod|vacance|semaine|jour|mois)\b/.test(haystack)) {
      return "Si oui, quelle période ou quelle semaine souhaitez-vous explorer ?";
    }
    if (/\b(restaurant|cantine|repas|restauration)\b/.test(haystack)) {
      return "Si oui, souhaitez-vous que je détaille la formule (repas, demi-pension, fréquentation) ?";
    }
    if (/\b(structure|site|accueil|centre|école|ecole)\b/.test(haystack)) {
      return "Si oui, quelle structure ou quel site visez-vous ?";
    }
    return base;
  }

  function assessAlignment(questionTokens, snippet, segment) {
    if (!questionTokens || !questionTokens.length) {
      return { message: "", tone: "neutral" };
    }

    const keywords = questionTokens.filter((token) => token.length > 3);
    if (!keywords.length) {
      return { message: "", tone: "neutral" };
    }

    const snippetTokens = new Set(tokenize(snippet || ""));
    const segmentTokens = segment && segment.content ? tokenize(segment.content) : [];
    for (const token of segmentTokens) {
      snippetTokens.add(token);
    }

    if (!snippetTokens.size) {
      return { message: "", tone: "neutral" };
    }

    let overlap = 0;
    const matchedTokens = [];
    for (const token of keywords) {
      if (snippetTokens.has(token)) {
        overlap += 1;
        matchedTokens.push(token);
      }
    }

    const coverage = overlap / keywords.length;
    if (coverage >= 0.55) {
      const sample = matchedTokens.slice(0, 3).join(", ");
      const details = sample ? ` (${sample})` : "";
      return {
        message: `Analyse RAG : correspondance forte avec votre requête${details}.`,
        tone: "ok",
      };
    }
    if (coverage >= 0.35) {
      return {
        message: "L'extrait couvre partiellement votre demande. Souhaitez-vous que je vérifie un autre point ?",
        tone: "info",
      };
    }
    return {
      message: "Je ne vois pas vos mots clés dans cet extrait. Dois-je fouiller d'autres sources locales ?",
      tone: "warn",
    };
  }

  function resolveSegmentUrl(segment) {
    if (segment && segment.url) return segment.url;
    const keys = [];
    if (segment && segment.source) keys.push(normalizeSourceKey(segment.source));
    if (segment && segment.label) keys.push(normalizeSourceKey(segment.label));
    for (const key of keys) {
      if (key && sourceUrlMap.has(key)) {
        return sourceUrlMap.get(key);
      }
    }
    return "";
  }

  function buildAnchoredUrl(segment) {
    const baseUrl = resolveSegmentUrl(segment);
    if (!baseUrl) return "";
    const fragmentSeed = segment.anchor || segment.fragment || segment.id;
    const normalizedSection =
      fragmentSeed ||
      (typeof segment.section !== "undefined"
        ? `voir-plus-section-${segment.section}`
        : "voir-plus");
    const separator = baseUrl.includes("#") ? "" : "#";
    return `${baseUrl}${separator}${normalizedSection}`;
  }

  function formatSnippet(snippet) {
    if (!snippet) {
      return "";
    }
    const lines = snippet
      .split(/\n+/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (!lines.length) {
      return `<p>${escapeHtml(snippet.trim())}</p>`;
    }

    const maybeTableRows = lines
      .map((line) => {
        const parts = line.split(/\s*[:\-–]\s+/);
        if (parts.length >= 2) {
          const [label, ...rest] = parts;
          const value = rest.join(": ").trim();
          if (label && value && /€|euros?/i.test(line)) {
            return { label: label.trim(), value };
          }
        }
        return null;
      })
      .filter(Boolean);

    if (maybeTableRows.length >= Math.min(2, lines.length)) {
      const rowsHtml = maybeTableRows
        .map(
          (row) =>
            `<tr><th>${escapeHtml(row.label)}</th><td>${escapeHtml(row.value)}</td></tr>`
        )
        .join("");
      return `<table class="assistant-table"><tbody>${rowsHtml}</tbody></table>`;
    }

    if (lines.length > 1) {
      const items = lines
        .map((line) => `<li>${escapeHtml(line)}</li>`)
        .join("");
      return `<ul class="assistant-bullet-list">${items}</ul>`;
    }

    return `<p>${escapeHtml(lines[0])}</p>`;
  }

  function rankSegments(question) {
    const questionTokens = tokenize(question);
    if (!questionTokens.length) return [];

    const scored = segments
      .map((segment) => ({
        ...segment,
        score: scoreSegment(questionTokens, segment),
      }))
      .filter((segment) => segment.score > 0);

    scored.sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      const aUrl = resolveSegmentUrl(a) ? 1 : 0;
      const bUrl = resolveSegmentUrl(b) ? 1 : 0;
      if (bUrl !== aUrl) {
        return bUrl - aUrl;
      }
      return (b.section ?? 0) - (a.section ?? 0);
    });
    return scored.slice(0, 3);
  }

  async function handleSubmit() {
    const question = questionInput.value.trim();
    if (!question) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Recherche…";
    answerEl.style.display = "none";
    sourcesEl.style.display = "none";
    sourcesList.innerHTML = "";

    try {
      if (!segments.length) {
        await loadSegments();
      }

      const ranked = rankSegments(question);
      if (!ranked.length) {
        answerEl.innerHTML =
          "<p>Je n'ai pas trouvé de passage pertinent dans le corpus local.</p>";
        answerEl.style.display = "block";
        return;
      }

      const questionTokens = tokenize(question);
      const primary = ranked[0];
      const others = ranked.slice(1);
      const intent = reformulateIntent(question);
      const primarySnippet = extractSnippet(primary.content, questionTokens);
      const primarySnippetHtml = formatSnippet(primarySnippet);
      const primarySnippetBlock = primarySnippetHtml
        ? `<div class="assistant-snippet">${primarySnippetHtml}</div>`
        : "";
      const alignmentAssessment = assessAlignment(questionTokens, primarySnippet, primary);
      const alignmentBlock =
        alignmentAssessment.message && alignmentAssessment.tone !== "neutral"
          ? `<p class="assistant-alignment assistant-alignment--${alignmentAssessment.tone}">${escapeHtml(
              alignmentAssessment.message
            )}</p>`
          : "";
      const primaryLink = buildAnchoredUrl(primary) || resolveSegmentUrl(primary);
      const granularityQuestion = buildGranularityPrompt(primary.content, questionTokens);

      const suggestionArticle = `
        <article class="assistant-suggestion">
          <header>Suggestion locale — ${escapeHtml(primary.label)}</header>
          <p>Je suppose que vous recherchez ${escapeHtml(intent)}.</p>
          ${primarySnippetBlock}
          ${alignmentBlock}
          ${
            primaryLink
              ? `<p><a class="source-link" href="${primaryLink}" target="_blank" rel="noopener noreferrer">→ Ouvrir la source (section voir +)</a></p>`
              : ""
          }
          <footer>${escapeHtml(granularityQuestion)}</footer>
        </article>
      `;

      const secondaryList = others
        .map((segment) => {
          const snippet = extractSnippet(segment.content, questionTokens);
          const snippetHtml = formatSnippet(snippet);
          const url = buildAnchoredUrl(segment) || resolveSegmentUrl(segment);
          return `
            <li>
              <strong>${escapeHtml(segment.label)}</strong>
              <div class="assistant-snippet">${snippetHtml}</div>
              ${
                url
                  ? `<br><a class="source-link" href="${url}" target="_blank" rel="noopener noreferrer">→ Consulter la même page (section voir +)</a>`
                  : ""
              }
            </li>
          `;
        })
        .join("");

      const alternativesArticle = secondaryList
        ? `
            <article class="assistant-alternatives">
              <header>Autres pistes locales</header>
              <ul>${secondaryList}</ul>
              <footer>Ces extraits proviennent des autres meilleures correspondances RAG.</footer>
            </article>
          `
        : "";

      const assistantPlaceholder = `
        <article class="assistant-followup" data-role="assistant-followup">
          <header>Analyse du modèle Claude (à venir)</header>
          <p>Cette section se mettra à jour dès que le modèle cloud aura reformulé ou validé la réponse.</p>
        </article>
      `;

      answerEl.innerHTML = [suggestionArticle, alternativesArticle, assistantPlaceholder]
        .filter(Boolean)
        .join("<hr>");
      answerEl.style.display = "block";

      ranked.forEach((segment) => {
        const li = document.createElement("li");
        if (segment.url) {
          const anchor = document.createElement("a");
          anchor.href = buildAnchoredUrl(segment) || resolveSegmentUrl(segment) || segment.url;
          anchor.target = "_blank";
          anchor.rel = "noopener noreferrer";
          anchor.textContent = segment.label;
          li.appendChild(anchor);
        } else {
          li.textContent = segment.label;
        }
        sourcesList.appendChild(li);
      });

      sourcesEl.style.display = "block";
    } catch (error) {
      console.error(error);
      answerEl.innerHTML =
        "<p>Une erreur s'est produite. Vérifie la console navigateur pour plus de détails.</p>";
      answerEl.style.display = "block";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Rechercher";
    }
  }

  submitBtn.addEventListener("click", handleSubmit);
  questionInput.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      handleSubmit();
    }
  });
})();

