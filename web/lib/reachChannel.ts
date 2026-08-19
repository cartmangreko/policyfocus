// The three reach channels (supply chain / procurement / regulatory
// dependency) are a rule the extraction pipeline followed when deciding
// whether to add a sector to sectors_reached — but the channel itself is
// not stored per entry in data/*.json (sectors_reached is a flat slug
// array). This module infers the channel from fields that ARE stored, for
// display purposes only. It does not add or change any data.
import type { Measure } from "./types";

export type ReachChannel = "supply chain" | "procurement" | "regulatory dependency";

// Display labels follow the display-vocabulary ruling (sources/scope.md):
// the regulatory-dependency channel reads "another act" to an audience. The
// internal channel names above are unchanged.
export const REACH_CHANNEL_LABEL: Record<ReachChannel, string> = {
  "supply chain": "Supply chain",
  procurement: "Procurement",
  "regulatory dependency": "Another act",
};

export function inferReachChannel(measure: Measure): ReachChannel {
  // A duty landing on a public buyer (class: state, procurement-flavoured
  // addressee/duty text) is definitionally the procurement channel.
  const text = `${measure.addressee} ${measure.duty ?? ""} ${measure.benefit ?? ""}`.toLowerCase();
  if (/procurement|contracting authorit|public buyer|tender|public support scheme/.test(text)) {
    return "procurement";
  }
  if (/suppl(y|ier|ies)|input|feedstock|value chain|upstream|downstream|component/.test(text)) {
    return "supply chain";
  }
  // Residual case: a horizontal duty (e.g. CSRD/CSDDD-style reporting) reaches
  // a sector because that sector is already subject to definitions/data from
  // another act this file depends on, not because of a trade or purchase link.
  return "regulatory dependency";
}
