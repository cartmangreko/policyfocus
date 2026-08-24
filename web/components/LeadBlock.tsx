import Link from "next/link";

// WHAT THIS COMPONENT NEEDS, which is less than any one of its callers has.
// A sector lead carries a fingerprint, an override flag and a `parts` block per
// fact; a measure lead carries none of them. The prop type is the intersection
// — the three things that are drawn — so the same block renders for a sector, a
// measure and a project without any of them having to pretend to be the others.
// §0.2 asks for one mechanism on every page type, and one mechanism means one
// component rather than three that look alike.
export interface LeadView {
  sentence: { text: string };
  why_it_matters: { text: string } | null;
  facts: {
    id: string;
    text: string;
    as_of: string;
    href: string | null;
    surface: boolean;
  }[];
}

// The first screen of a sector page: the sentence, why it matters, and the
// facts both rest on.
//
// IT DRAWS AND IT DOES NOT WRITE. Every string here comes out of
// data/transition/lead/<sector>.json, which sources/build_lead.py computes from
// the panels below and puts through a gate before writing: every number in the
// prose appears in a fact, every date is a fact's as-of date, two sentences
// maximum, no judgment adjectives. A component that composed its own sentence
// would be prose nobody gated, which is the thing sources/scope.md bans.
//
// UNSIGNED, DELIBERATELY. A reviewer's sentence and a generated one render
// identically. The distinction is real and it is a fact about the pipeline, not
// about the claim: both have passed the same gate, and a byline on one of them
// would invite a reader to trust it more.
//
// DATES ON EVERYTHING, LABELS ON NOTHING. Each fact carries the as-of date of
// the number in it, in monospace. No stale badge, no confidence chip — the
// staleness report is build-side and confidence lives inside the expanded
// source line on the panel itself. Since brief 4 §5 the labels are gone from
// the surface altogether: they are in the built artifact, where the report and
// anything downstream can name a fact, and a reader gets the sentence.
export default function LeadBlock({ lead }: { lead: LeadView }) {
  return (
    <div className="lead-block">
      <p className="lead-sentence">{lead.sentence.text}</p>

      {lead.why_it_matters ? (
        <div className="lead-why">
          <h2>Why it matters</h2>
          <p>{lead.why_it_matters.text}</p>
        </div>
      ) : null}

      {/* THE FACTS, AS SENTENCES (brief 4 §5). This was a definition list:
          a schema label — "Binding constraint", "Decisive exposure" — and a
          clause under it. The label was the schema introducing itself, and the
          clause under it had no subject of its own, so a reader met four
          fragments and had to assemble the sentence themselves.

          Each line is now one sentence with its own subject, and the date
          belongs to the number in it: an as-of on a figure is part of the
          claim, not provenance to be tucked away. Facts the builder did not
          surface are not here — see the `surface` flag. */}
      <ul className="lead-facts">
        {lead.facts
          .filter((f) => f.surface)
          .map((f) => (
            <li key={f.id} className="lead-fact">
              {f.href ? <Link href={f.href}>{f.text}</Link> : f.text}{" "}
              <span className="lead-asof">as of {f.as_of}</span>
            </li>
          ))}
      </ul>
    </div>
  );
}
