// Analysis is the one part of the site with no counterpart in data/*.json —
// the prose is authored. What is NOT authored is the evidence: each piece
// carries a predicate that pulls its supporting measures straight out of the
// register, so an article can never cite a count that the data disagrees with.
// When a CMS or an editorial workflow lands, this module is what it replaces.
import { getAllMeasures } from "./data";
import type { Measure } from "./types";

export interface AnalysisPiece {
  slug: string;
  kicker: string;
  title: string;
  dek: string;
  readingTime: string;
  date: string;
  standfirst: string;
  body: string[];
  /** Which measures the piece is reading. Rendered as its evidence list. */
  evidence: (m: Measure) => boolean;
  evidenceNote: string;
}

export const ANALYSIS: AnalysisPiece[] = [
  {
    slug: "what-the-omnibus-removes",
    kicker: "Simplification",
    title: "What the Omnibus removes — and what it quietly adds",
    dek: "A relief package on its face, with a small number of new duties that survive the cut.",
    readingTime: "6 min",
    date: "Aug 2026",
    standfirst:
      "Omnibus I is presented as a simplification file. Read provision by provision, the direction of travel is less uniform than the framing suggests.",
    body: [
      "The headline claim is withdrawal: thresholds raised, scope narrowed, reporting duties merged or dropped outright. Measured against the register, that claim holds for the largest single block of provisions in the file — but it does not hold for the file as a whole.",
      "A simplification package still has to be implemented, and implementation is itself a duty. Provisions that hand the Commission a delegated act to draft, or a Member State an authority to designate, are additions in the register's terms even when their purpose is to remove burden downstream. They land on a different addressee than the one the relief is aimed at.",
      "The practical reading is that relief and requirement are not opposites distributed across a file; they are distributed across addressees within it. A provision that lifts a duty from mid-cap business frequently creates a corresponding one for the institution that has to administer the lift. The ledger on the homepage is the fastest way to see that asymmetry.",
      "What survives the cut matters more than what is dropped. The duties that remain after a simplification pass are, by construction, the ones the legislator judged load-bearing — and they are the ones worth reading closely.",
    ],
    evidence: (m) => m.file === "omnibus",
    evidenceNote: "Every provision extracted from Omnibus I, in register order.",
  },
  {
    slug: "the-450m-line",
    kicker: "Thresholds",
    title: "The €450m line: how new thresholds redraw who reports",
    dek: "Where the size tests move, and which mid-caps drop out of scope entirely.",
    readingTime: "5 min",
    date: "Aug 2026",
    standfirst:
      "Scope changes rarely read as dramatic in the text. A number moves. The population it describes can change by an order of magnitude.",
    body: [
      "A threshold is the cheapest instrument a legislator has. It does not alter what a duty requires, only who has to do it — which means a single amended figure can relieve a whole tier of companies without a word of the substantive obligation changing.",
      "That is why the register records the trigger separately from the obligation. Reading the two side by side on a measure page shows what actually moved: in most threshold amendments the obligation column is identical before and after, and the entire effect sits in the trigger.",
      "The complication is that thresholds compose. A company can sit above one test and below another, or above a turnover line while below an employee count, and the duties that reach it are the intersection rather than the union. The size-scope note on each measure records where that intersection is genuinely load-bearing.",
      "For anyone sizing exposure, the operative question is not whether you are in scope today but how far you sit from the nearest line — because that distance, not the current answer, is what determines whether the next amendment reaches you.",
    ],
    evidence: (m) => Boolean(m.size_scope_note) || /threshold|turnover|employee/i.test(m.trigger),
    evidenceNote: "Measures whose trigger turns on a size test, or that carry a size-scope note.",
  },
  {
    slug: "relief-for-whom",
    kicker: "Incidence",
    title: "Relief for whom? Reading the burden by addressee",
    dek: "Business gains the most; the Commission and Member States pick up new duties.",
    readingTime: "7 min",
    date: "Aug 2026",
    standfirst:
      "Aggregate counts of duties added and removed say almost nothing until you ask who is on the receiving end of each.",
    body: [
      "Incidence is the whole question. A file that removes forty duties and adds forty is neutral only if the same party carries both sides — and that is almost never the case. The register's addressee class exists precisely so the two sides can be told apart.",
      "Read by class, the corpus separates cleanly. Duties on business move in both directions and are the most contested. Duties on Member States and the Commission move overwhelmingly in one: they accumulate. Administrative capacity is the standing cost of every agenda, whichever direction that agenda pushes.",
      "This has a consequence for anyone forecasting compliance load. Relief granted to business in a file is frequently conditional on institutional machinery that does not exist yet — a standard to be published, a registry to be built, an authority to be designated. Until those land, the relief is drafted but not operative.",
      "The seven burden drivers refine this further. They record why a provision is costly, not merely that it is: whether it demands new data collection, external verification, or a contractual cascade into a supply chain. Two duties on the same addressee can differ by an order of magnitude in what they actually cost to satisfy.",
    ],
    evidence: (m) => m.class === "state" || m.class === "commission",
    evidenceNote:
      "Provisions addressed to Member States and the Commission — the institutional side of the ledger.",
  },
];

export function getAnalysis(slug: string): AnalysisPiece | undefined {
  return ANALYSIS.find((a) => a.slug === slug);
}

export function getAnalysisEvidence(slug: string, limit = 8): Measure[] {
  const piece = getAnalysis(slug);
  if (!piece) return [];
  return getAllMeasures().filter(piece.evidence).slice(0, limit);
}

export function getAnalysisEvidenceCount(slug: string): number {
  const piece = getAnalysis(slug);
  if (!piece) return 0;
  return getAllMeasures().filter(piece.evidence).length;
}
