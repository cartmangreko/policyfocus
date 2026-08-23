import { FILES } from "./data";
import { getSiteSummary } from "./summaries";
import type { Measure } from "./types";

// schema.org structured data, computed from the same objects as everything
// else on the page.
//
// TYPE CHOICES, documented once here:
//
//   The site       schema:Dataset. The register is exactly that — a dataset
//                  of extracted provisions with a stated methodology — and
//                  Dataset is the type search engines index for data reuse.
//   A measure      schema:Legislation, with isPartOf pointing at a second
//                  Legislation node for the act it was read from. schema.org
//                  models a provision of a legal act as Legislation in its
//                  own right (that is what legislationIdentifier and
//                  isPartOf exist for). DefinedTerm was considered and
//                  rejected: a register row is a duty or an incentive, not a
//                  term definition; the delegated acts defining "low-carbon"
//                  would be DefinedTerm territory when they land.
//
// Nothing here invents a fact: names and codes come from FILES, counts from
// the site summary, and the verbatim source URL from the row itself.

export function datasetJsonLd(): string {
  const site = getSiteSummary();
  const doc = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "Eufabric — EU industrial-decarbonisation measures, decoded",
    description:
      `${site.measures} measures decoded from ${site.files} EU acts, ` +
      `each one a requirement, prohibition, support measure or right with its source ` +
      `sentence quoted verbatim, mapped to the ${site.sectors.total_reach} sectors it affects.`,
    keywords: Object.values(FILES).map((f) => f.name.split(" — ")[0]),
  };
  return JSON.stringify(doc);
}

export function measureJsonLd(measure: Measure): string {
  const fileMeta = FILES[measure.file];
  const doc = {
    "@context": "https://schema.org",
    "@type": "Legislation",
    name: `${measure.id} — ${measure.duty ?? measure.benefit ?? measure.id}`,
    legislationIdentifier: measure.id,
    text: measure.source_text,
    url: measure.source_url,
    isPartOf: {
      "@type": "Legislation",
      name: fileMeta?.name ?? measure.file,
      legislationIdentifier: fileMeta?.code ?? measure.file,
    },
  };
  return JSON.stringify(doc);
}
