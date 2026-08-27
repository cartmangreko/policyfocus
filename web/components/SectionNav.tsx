"use client";

import { useEffect, useRef, useState } from "react";
import type { RenderedSection } from "@/lib/sectorSections";

// THE SECTION NAV, brief 5 §3. One anchor per rendered section, in the
// specified order, directly under the site header and sticky beneath it.
//
// JUMP LINKS, NOT TABS. Every section stays in the DOM and stays visible; this
// bar moves the page, it does not hide any of it. That is the whole difference
// between a reader who can scan the sequence and one who has to click nine
// times to find out what is on the page.
//
// THE LIST IS NOT ITS OWN. It is `renderedSections()` — the same array the page
// renders its sections from, handed down. §8's check_section_order asks that
// nav entries equal rendered sections, and the cheapest way to satisfy a gate
// is to make the property it checks impossible to break: there is one list.

/** Where the top of the viewport effectively is, once the header and this bar
 *  have taken their share. Read from the tokens rather than measured, so the
 *  scrollspy's idea of "at the top" is the same number the CSS gives the anchor
 *  targets as scroll-margin-top and the two cannot drift. */
function stickyOffset(): number {
  const styles = getComputedStyle(document.documentElement);
  const px = (name: string) => parseInt(styles.getPropertyValue(name), 10) || 0;
  return px("--header-h") + px("--sectionnav-h");
}

export default function SectionNav({ sections }: { sections: RenderedSection[] }) {
  const [active, setActive] = useState<string | null>(sections[0]?.id ?? null);
  const bar = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const targets = sections
      .map((s) => document.getElementById(s.id))
      .filter((el): el is HTMLElement => el !== null);
    if (targets.length === 0) return;

    // THE OBSERVER TRIGGERS THE DECISION; IT DOES NOT MAKE IT. An entries-based
    // rule ("the most intersecting one") flickers between two sections whose
    // boundary is crossing the fold, and reads as a bar that cannot make up its
    // mind. So a crossing only prompts a recount, and the recount is the plain
    // question a reader is actually asking: which section have I got to? — the
    // last one whose top has passed under the sticky bar.
    const recount = () => {
      const offset = stickyOffset() + 1;
      let current = targets[0];
      for (const el of targets) {
        if (el.getBoundingClientRect().top <= offset) current = el;
      }
      // The bottom of the document cannot be scrolled past, so the last section
      // may never reach the fold on a short final section. If the page is at
      // the end, it is the one being read.
      const atEnd =
        window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
      setActive(atEnd ? targets[targets.length - 1].id : current.id);
    };

    const observer = new IntersectionObserver(recount, {
      threshold: [0, 1],
      rootMargin: `-${stickyOffset()}px 0px 0px 0px`,
    });
    for (const el of targets) observer.observe(el);
    window.addEventListener("scroll", recount, { passive: true });
    window.addEventListener("resize", recount);
    recount();
    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", recount);
      window.removeEventListener("resize", recount);
    };
  }, [sections]);

  // On a phone the row scrolls sideways, so the active chip has to be brought
  // to where it can be seen — otherwise the one piece of information this bar
  // carries on a small screen is the piece that is off the edge of it.
  useEffect(() => {
    if (!active || !bar.current) return;
    const chip = bar.current.querySelector<HTMLElement>(`[data-section="${active}"]`);
    chip?.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
  }, [active]);

  return (
    <nav ref={bar} className="sectionnav" aria-label="Sections of this page">
      <ul className="sectionnav-list">
        {sections.map((s) => (
          <li key={s.id}>
            <a
              href={`#${s.id}`}
              data-section={s.id}
              className={`sectionnav-link${active === s.id ? " is-here" : ""}`}
              aria-current={active === s.id ? "true" : undefined}
            >
              {s.nav}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
