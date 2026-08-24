import Link from "next/link";
import SectorIcon from "./SectorIcon";
import { ecosystemHref, getEcosystems } from "@/lib/ecosystems";
import { getEcosystemDescription } from "@/lib/sitetext";

// The six, drawn from the node kind. One component on the front page and on
// /sectors, so the two cannot become two different lists.
//
// NO COUNTS, AND NO DESCRIPTION ON THE FACE. The tile carries the name and the
// icon. What each ecosystem contains — where chemicals stops and hydrogen
// starts, that batteries does not mean solar — is a paragraph, and a paragraph
// on a tile competes with the six names the grid exists to present. It is on
// the coverage page, and it is the tile's hover text, which is what `title` is
// for: available to a reader who asks, absent from the layout that does not.
//
// A tile with no reviewed description simply has no hover text. It never falls
// back to the scope sentence in the data, which is a note to whoever maintains
// the edges rather than a sentence written for a reader.
export default function EcosystemTiles() {
  return (
    <div className="hairline-grid tile-grid">
      {getEcosystems().map((e) => {
        const description = getEcosystemDescription(e.id);
        return (
          <Link
            key={e.id}
            href={ecosystemHref(e)}
            className="tile"
            title={description ?? undefined}
          >
            <SectorIcon slug={e.icon} size={26} />
            <span className="tile-name">{e.name}</span>
          </Link>
        );
      })}
    </div>
  );
}
