"""
How long every unfinished project has been where it is.

    python3 report_status_age.py          # always exits 0; this reports

WHAT IT IS AND WHAT IT DELIBERATELY IS NOT
==========================================
A listing. Every project whose status is not terminal, ordered by how long it has
held that status, with the date it entered it. That is the whole output.

NO THRESHOLD AND NO VERDICT, and both absences are the design rather than an
unfinished edge. A threshold would invent a number nobody has ruled on -- there is
no month at which a project under construction becomes a project in trouble, and
picking one would put a judgement into a report and let it be read as a finding.
A verdict would be worse: "stalled" is a conclusion about a company's intentions,
and this file knows only dates. The reader who sorts by age can see what is old.
Deciding what old means is theirs.

WHY IT IS SEPARATE FROM THE STALENESS REPORT
============================================
They catch different failures and they disagree about the same project all the
time.

  STALENESS   asks when somebody last SAID anything -- an announcement that went
              quiet. It reads source dates. report_candidate_gaps.py's territory.

  THIS        asks when the project last MOVED. It reads status_history.

The AESC site at Navalmoral de la Mata is the case that forced the split: the
cornerstone was laid in July 2024, the regional government was still updating its
roadmap in June 2026, and the first cell is not expected until December 2028.
Nothing has gone quiet, so staleness finds nothing; four and a half years separate
the ceremony from the cell, which is what this listing shows. One report would
have had to choose which of those two facts to be about, and would have hidden the
other.

TIME IS COUNTED FROM THE TRANSITION, not from the last entry. A project whose
history carries a later event with the status unchanged -- a permit withdrawn, a
company changing hands -- has not moved, and dating it from that entry would reset
the clock on exactly the projects this listing exists to show. See
sector_map.entered.
"""

from __future__ import annotations

import datetime as dt

import sector_map as sm


def _days(date: str, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat(date)).days
    except ValueError:
        # A history date of "2023" rather than "2023-04-18" is legal in the
        # register and is honest about what the source gave. It cannot be
        # subtracted, so it is shown and not counted.
        return None


def main() -> int:
    today = dt.date.today()
    rows = []
    for p in sm.load("project"):
        if p["status"] in sm.TERMINAL_STATUSES:
            continue
        event = sm.entered(p)
        if not event:
            continue
        rows.append((_days(event["date"], today), event["date"], p))

    if not rows:
        print("report_status_age: no unfinished projects")
        return 0

    # Undatable entries sort last rather than first: an unparseable date is not
    # evidence of age in either direction, and putting it at the top of a list
    # ordered by age would read as the oldest thing on it.
    rows.sort(key=lambda r: (r[0] is None, -(r[0] or 0), r[2]["id"]))

    print(f"report_status_age: {len(rows)} unfinished project(s), longest in status first "
          f"(as of {today.isoformat()})")
    for days, date, p in rows:
        age = f"{days // 365}y {days % 365 // 30}m" if days is not None else "—"
        print(f"  {date}  {age:>8}  {p['sector']:8} {p['id']:30} {p['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
