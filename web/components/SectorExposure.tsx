"use client";

import { useState } from "react";
import { countryName } from "@/lib/countries";
import type { Exposure, ExposureRow } from "@/lib/types";

const EU = "EU";

// Provenance for every figure in this panel. Display vocabulary: the dataset
// is FIGARO internally, "Eurostat input-output data" to the audience.
const EXPOSURE_SOURCE =
  "Eurostat input-output data, 2026 edition, 2024 reference year (EU inter-country tables, industry by industry).";

// Above this share of output going to final use, the customers list is
// describing a minority of the sector's sales and saying so becomes necessary
// rather than merely informative. 25% is a judgement, not a statistic: it sits
// in the wide empty band between paper/chem (~18%) and waste (25.3%), so no
// sector sits marginally on either side of it. Nine of seventeen sectors are
// above it, hotels & restaurants highest at 79.6%.
const FINAL_DEMAND_NOTE_THRESHOLD = 25;

// The remainder row closing the suppliers and customers lists. It is a balance
// to 100, not an industry link, and is rendered as such.
const OTHER_CODE = "OTHER";

// One row of a list. The share is printed exactly as the data carries it; the
// bar is that same number as a width, so nothing is rescaled to fill the track.
function Row({ row, name }: { row: ExposureRow; name?: (row: ExposureRow) => string }) {
  const other = row.code === OTHER_CODE;
  return (
    <li className={other ? "exp-row is-other" : "exp-row"}>
      <span className="exp-row-label">{name ? name(row) : row.label}</span>
      <span className="exp-row-bar" aria-hidden="true">
        <span className="exp-row-fill" style={{ width: `${row.share}%` }} />
      </span>
      <span className="exp-row-share">{row.share}%</span>
    </li>
  );
}

function Block({
  eyebrow,
  heading,
  rows,
  name,
}: {
  eyebrow: string;
  heading: string;
  rows: ExposureRow[];
  name?: (row: ExposureRow) => string;
}) {
  return (
    <div className="exp-block">
      <p className="eyebrow">{eyebrow}</p>
      <h3 className="exp-block-head">{heading}</h3>
      <ul className="exp-list">
        {rows.map((r) => (
          <Row key={r.code} row={r} name={name} />
        ))}
      </ul>
    </div>
  );
}

export default function SectorExposure({
  exposure,
  sectorName,
}: {
  exposure: Exposure;
  sectorName: string;
}) {
  // The only client state. Both views are already in the payload — selecting a
  // country swaps which one is read, it does not fetch or derive anything.
  const [area, setArea] = useState<string>(EU);

  const view = area === EU ? exposure.eu : exposure.by_country[area];
  const areaName = area === EU ? "the EU" : countryName(area, area);
  const countries = Object.keys(exposure.by_country).sort((a, b) =>
    countryName(a, a).localeCompare(countryName(b, b))
  );

  return (
    // The findings layer links straight at this panel, so it carries an id.
    <section className="band band-ruled" id="exposure">
      <div className="wrap">
        <div className="exp-head">
          <div>
            <p className="eyebrow">Supply chain and country exposure</p>
            <h2>What {sectorName.toLowerCase()} buys, sells and imports</h2>
            {exposure.note && <p className="exp-note">{exposure.note}</p>}
          </div>
          <label className="exp-select">
            <span className="exp-select-label">View</span>
            <select value={area} onChange={(e) => setArea(e.target.value)}>
              <option value={EU}>European Union</option>
              {countries.map((cc) => (
                <option key={cc} value={cc}>
                  {countryName(cc, cc)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="exp-grid">
          <Block
            eyebrow="Inputs come from"
            heading="What this sector buys"
            rows={view.suppliers}
          />
          <div className="exp-block">
            <Block
              eyebrow="Goods go to"
              heading="Who buys from this sector"
              rows={view.customers}
            />
            {typeof view.final_demand_share_pct === "number" &&
              view.final_demand_share_pct >= FINAL_DEMAND_NOTE_THRESHOLD && (
                <p className="exp-caption">
                  This list covers sales to other industries only. A further{" "}
                  {view.final_demand_share_pct}% of what this sector sells goes straight to
                  final use — households, government and capital formation — and so appears
                  nowhere above.
                </p>
              )}
          </div>
          <div className="exp-block">
            <p className="eyebrow">Import exposure</p>
            <h3 className="exp-block-head">
              <span className="exp-headline">{view.import_dependency_pct}%</span> of inputs come
              from outside {areaName}
            </h3>
            {area !== EU && (
              <p className="exp-caption">
                Other EU countries count as foreign to {areaName}, so this can run above the EU
                figure of {exposure.eu.import_dependency_pct}%.
              </p>
            )}
            <ul className="exp-list">
              {view.foreign_input_origins.map((r) => (
                <Row key={r.code} row={r} name={(row) => countryName(row.code, row.label)} />
              ))}
            </ul>
          </div>
        </div>

        <p className="exp-source">
          {exposure.figaro_label} ({exposure.figaro_code}). {exposure.shares_basis}. Source:{" "}
          {EXPOSURE_SOURCE}
        </p>
      </div>
    </section>
  );
}
