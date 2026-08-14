// Mirrors the fields actually present in data/*.json. Every field beyond the
// universal core is optional — different extraction passes populate different
// subsets (e.g. only omnibus.json currently carries the prior/new rule diff
// model; only ets.json/iaa.json carry the benefit-side incentive fields).

export type MeasureClass = "business" | "state" | "investor" | "commission" | "household";
export type Direction = "add" | "rem";
export type MeasureType = "obligation" | "incentive";
export type DDriver = "D1" | "D2" | "D3" | "D4" | "D5" | "D6" | "D7";
export type VDriver = "V1" | "V2" | "V3" | "V4";
export type FFriction = "F1" | "F2" | "F3" | "F4" | "F5";

export type SectorSlug =
  | "steel" | "cement" | "alu" | "chem" | "glass" | "power" | "waste"
  | "ship" | "air" | "auto" | "build" | "batsol" | "clean" | "ccs";

export interface RuleState {
  trigger: string;
  obligation: string;
  source_text?: string | null;
  status?: string;
  note?: string;
}

export type SizeScopeStatus = "in" | "out" | "na";
export interface SizeScope {
  A?: SizeScopeStatus;
  B?: SizeScopeStatus;
  C?: SizeScopeStatus;
  D?: SizeScopeStatus;
}

export interface Measure {
  id: string;
  file: string;

  // measure_type is absent on some older rows; treat missing as "obligation".
  measure_type?: MeasureType;
  duty?: string;
  benefit?: string;

  addressee: string;
  class: MeasureClass;
  trigger: string;
  frequency: string;
  verification: string;
  direction: Direction;
  article: string;
  when: string;
  source_text: string;
  source_url: string;

  drivers?: DDriver[];
  value_drivers?: VDriver[];
  access_frictions?: FFriction[];

  sectors_named: SectorSlug[];
  sectors_reached: SectorSlug[];

  pending?: string;
  provision_id?: string | null;

  // diff-model fields (currently omnibus.json only)
  nature?: string;
  new_rule?: RuleState;
  prior_rule?: RuleState | null;
  affected_delta?: string;
  weight?: string; // NOTE: contains a value literally called "Relief" — display as-is, do not confuse with valence.
  weight_intensity?: string;
  size_scope?: SizeScope;
  size_scope_note?: string;
}

export interface FileMeta {
  name: string;
  code: string;
}

// ---------------------------------------------------------------------------
// Supply-chain and country exposure — data/exposure/<slug>.json. A separate
// concern from the measures above: no field here feeds valence or the register.
// Kept in this (dependency-free) module so the client panel can import the
// shapes without pulling in the fs loader.
// ---------------------------------------------------------------------------

export interface ExposureRow {
  code: string;
  label: string;
  share: number;
}

export interface ExposureView {
  /** Share of this sector's inputs bought from outside the home area. */
  import_dependency_pct: number;
  /** Industries this sector buys from; last row is OTHER. */
  suppliers: ExposureRow[];
  /** Industries that buy from this sector; last row is OTHER. */
  customers: ExposureRow[];
  /** Countries the imported inputs come from; may include "rest of world". */
  foreign_input_origins: ExposureRow[];
}

export interface Exposure {
  slug: string;
  figaro_code: string;
  figaro_label: string;
  shares_basis: string;
  /** Set where two sectors share one FIGARO code, else null. */
  note: string | null;
  eu: ExposureView;
  /** Keyed by ISO 3166-1 alpha-2, the 27 EU members. */
  by_country: Record<string, ExposureView>;
}
