import Link from "next/link";
import type { HubBlock as Block } from "@/lib/hub";

// ONE BLOCK, RENDERED. Brief 15's four questions all render through this, which
// is the point of it: four blocks that look alike are four answers a reader
// reads the same way, and four bespoke sections are four things to learn.
//
// WHY THIS IS A NEW COMPONENT, since brief 15 asks for none. The block is the
// unit the brief invents — a framing line, capped rows, one link, in that fixed
// shape — and there is no existing component that is that shape. The
// alternative was the same forty lines of JSX written four times in
// SectorMap.tsx, which is how the nine sections it replaces came to differ from
// each other in the first place. The row inside it reuses the existing type and
// status label classes rather than inventing more.
//
// TYPOGRAPHIC, NOT A CARD. Heading, line, hairline-separated rows, one link. No
// panel, no box, no icon per row, no badge beyond the status and kind labels
// the design already has, no shadow, no rounded container.
export default function HubBlock({ block, heading }: { block: Block; heading: string }) {
  return (
    <section className="tmap-section hubblock" id={block.id}>
      <h2 className="sectionhead">{heading}</h2>
      {/* THE FRAMING LINE. Computed from this block's own gated source, with
          the as-of date, and its counts sum against the spoke page. A block
          with nothing on file renders this line saying so and stops — no
          placeholder row, no empty-state graphic, no invented item. */}
      <p className="hubblock-framing">{block.framing}</p>
      {block.items.length > 0 ? (
        <ul className="hubblock-rows">
          {block.items.map((item) => (
            <li key={item.key} className="hubblock-row">
              <span className="hubblock-name">
                {item.href ? <Link href={item.href}>{item.name}</Link> : item.name}
              </span>
              {item.kind ? <span className={`tkind ${item.kind}`}>{item.kind}</span> : null}
              {item.status ? (
                <span className={`tstatus ${item.status.cls}`}>{item.status.label}</span>
              ) : null}
              {/* ONE computed fact, one clause. A paragraph per item is the
                  thing this page stopped doing. */}
              <span className="hubblock-fact">{item.fact}</span>
              <span className="hubblock-date">{item.date ?? ""}</span>
            </li>
          ))}
        </ul>
      ) : null}
      {/* THE ONE LINK, in the fixed form. n is the spoke's count, and
          sources/check_hub_list_duplication.py fails the build where the two
          disagree. */}
      {block.link ? (
        <p className="hubblock-more">
          <Link href={block.link.href}>{block.link.label} →</Link>
        </p>
      ) : null}
    </section>
  );
}
