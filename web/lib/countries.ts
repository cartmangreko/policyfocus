// Country names for the exposure panel. FIGARO labels origin rows with the
// bare ISO code ("RU", "IT"), which reads as a code rather than a place; this
// map is presentation only — no share, order or figure is touched by it.
//
// Covers the EU 27 plus every non-EU origin appearing in data/exposure/*.json.
export const COUNTRY_NAMES: Record<string, string> = {
  AT: "Austria",
  BE: "Belgium",
  BG: "Bulgaria",
  CY: "Cyprus",
  CZ: "Czechia",
  DE: "Germany",
  DK: "Denmark",
  EE: "Estonia",
  ES: "Spain",
  FI: "Finland",
  FR: "France",
  GR: "Greece",
  HR: "Croatia",
  HU: "Hungary",
  IE: "Ireland",
  IT: "Italy",
  LT: "Lithuania",
  LU: "Luxembourg",
  LV: "Latvia",
  MT: "Malta",
  NL: "Netherlands",
  PL: "Poland",
  PT: "Portugal",
  RO: "Romania",
  SE: "Sweden",
  SI: "Slovenia",
  SK: "Slovakia",

  AR: "Argentina",
  BR: "Brazil",
  CA: "Canada",
  CH: "Switzerland",
  CN: "China",
  GB: "United Kingdom",
  ID: "Indonesia",
  IN: "India",
  JP: "Japan",
  KR: "South Korea",
  MK: "North Macedonia",
  MX: "Mexico",
  NO: "Norway",
  RS: "Serbia",
  RU: "Russia",
  SA: "Saudi Arabia",
  TR: "Türkiye",
  US: "United States",
  ZA: "South Africa",
};

// Falls back to the label the data carries — "rest of world" and "everything
// else" are already written out, and an unmapped code still renders.
export function countryName(code: string, fallback: string): string {
  return COUNTRY_NAMES[code] ?? fallback;
}
