"""
The sector transition map: schema, vocabularies, and the loader every other
script on this layer reads through.

WHY THIS FILE EXISTS
====================
The register answers "what does this act require". It cannot answer "what
transition is this sector under, which measures decide whether it pays, who is
building what, and what is blocking it" -- because the objects that question is
about (technologies, bottlenecks, projects, and the numbers that quantify them)
are not legal provisions and have no place in a register row.

So they get their own node kinds, in their own files, under data/transition/.
The register is not replaced: it becomes the candidate pool that the measure
importance score ranks. Nothing here rewrites data/*.json.

THE FILES
=========
  data/transition/technologies.json   shared across sectors, never duplicated
  data/transition/bottlenecks.json    one sector + one transition each
  data/transition/parameters.json     every number that any surface states
  data/transition/projects.json       real installations, append-only history
  data/transition/materials.json      what a sector makes, consumes and throws off
  data/transition/funding.json        capital allocated, and what it was allocated under
  data/transition/measure_labels.json what a measure is CALLED on a diagram
  data/transition/corrections.json    dated notes on figures already printed

Each file is {"_comment": [...], "<kind>s": [ ... ]} -- the same arrangement
data/sectors.json uses, for the same reason: a data file that cannot say what
it is for gets misread by the next person to open it.

TRANSITION IS AN ATTRIBUTE, NOT A PRODUCT
=========================================
A sector can be under more than one transition at once. Cement has one
(decarbonisation); chemicals or automotive would carry several. Transition is
therefore a field on the technology, the bottleneck and the project -- never a
separate file, a separate route, or a separate build. The vocabulary is closed
(TRANSITIONS below) and a value outside it is a build failure, because the
sector page groups by it and an unrecognised value would render as a section
nobody wrote.

`digital` is in the vocabulary and is deliberately unused: a transition is
added to a sector only where a money component can be computed and a public
project pipeline exists, and digital regulation has neither yet.

EVERY NUMBER CARRIES ITS SOURCE
===============================
The rule from the register layer holds here without exception. A parameter is
{value, unit, scope, date_of_value, retrieved_date, source{url, publisher,
verbatim}, confidence}. There is no field for a number somebody remembered.
`verbatim` is the sentence the number was read from, not a paraphrase of it --
if the quote does not contain the number, the parameter is not sourced.

Staleness is recorded, not enforced: `stale_after` months past `date_of_value`
makes a parameter STALE, which the gate prints and does not fail on. A stale
carbon price is still the last carbon price anybody wrote down; failing the
build over it would take the whole site down for the age of one number.

CONFIDENCE
==========
  primary     the number is in the source document, stated by the body that
              produced it (a registry, a regulation, the company's own release)
  secondary   a third party reporting somebody else's number
  estimate    the source itself calls it an estimate, a range, or a forecast

The distinction is not decoration: the money model in build_importance.py
weights nothing by confidence, but a reviewer ranking a sector needs to see at
a glance whether the top measure rests on a registry figure or on a consultancy
projection.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import number_format as nf

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "transition"

# ---------------------------------------------------------------------------
# Closed vocabularies. Every one of these is closed on purpose: an open list
# here becomes a set of one-off values nobody can group by six months later.
# ---------------------------------------------------------------------------

TRANSITIONS = (
    "decarbonisation",
    "circularity",
    "supply_security",
    "digital",
    "defence",
)

READINESS = (
    "research",
    "pilot",
    "demonstration",
    "early-commercial",
    "commercial",
)

BOTTLENECK_TYPES = (
    "technical",
    "financial",
    "infrastructure",
    "market",
    "political",
)

# Append-only in spirit as well as in the data: a project moves forward through
# these, and `paused` / `cancelled` are terminal-ish states that the status
# strip has to be able to draw without pretending the project never existed.
PROJECT_STATUSES = (
    "announced",
    "funded",
    "fid",
    "construction",
    # BUILT AND NOT YET IN COMMERCIAL OPERATION, and it is a rung because a real
    # project sat between two others with nowhere to be. RWE's Lingen works was
    # making certified hydrogen in August 2026 while the company said in the same
    # release that it would "prepare the plants for commercial operation" over
    # the coming months. `construction` says nothing is being produced, which was
    # false; `operating` says the ladder has been climbed, which was also false.
    # The gap is not a hydrogen quirk: every large process plant has a
    # commissioning period, and cement and steel will reach it too.
    #
    # IT IS ALIVE AND IT IS NOT TERMINAL. A plant in commissioning is going
    # somewhere, so it joins PROJECT_ALIVE and the paper's `active` group; it has
    # not arrived, so TERMINAL_STATUSES is untouched and an attrition series can
    # still see a project that stalls in commissioning, which is a real way to
    # fail and one nothing here could previously record.
    "commissioning",
    "operating",
    "paused",
    "cancelled",
)


# WHAT A STATUS MEANS FOR A COUNT, in one place, because the attrition question
# is a count and a count that quietly spans these groups is the failure the
# vocabulary exists to prevent. Modelled on FUNDING_COMMITTED / FUNDING_ANNOUNCED
# / FUNDING_EXCLUDED below, and checked the same way: every project status is in
# exactly one group, and check_sector_schema.py fails if one is in none, so
# adding a status without deciding what it means for a count fails rather than
# defaulting into invisibility.
#
#   ALIVE      the project is supposed to be going somewhere, INCLUDING paused.
#              A paused project can resume, and one that has been paused for
#              three years is exactly what an attrition series is measuring; it
#              is a project that has stopped MOVING, not one that has stopped.
#   STOPPED    it will not be built. `cancelled` is the only project status that
#              says so.
#   COMPLETE   it climbed the whole ladder and has nowhere left to go.
#
# THIS IS A COUNTING GROUP AND NOT A DRAWING ONE. Nothing on the site reads these
# — no surface changed when they landed — so unlike the funding groups they are
# not mirrored into web/lib/transition.ts and the parity half of
# check_status_groups does not apply to them. When a surface does read them, the
# mirror and its check are what to add.
PROJECT_ALIVE = ("announced", "funded", "fid", "construction", "commissioning",
                 "paused")
PROJECT_STOPPED = ("cancelled",)
PROJECT_COMPLETE = ("operating",)


# THE STATUSES THAT STOP A PROJECT, named once because three files branch on
# them: the schema gate, which lets a stopped row stand without a coordinate;
# build_maps, which cannot draw one; and the ROADMAP entry that will eventually
# ask whether `paused` should age into `cancelled` on its own.
#
# WHY A STOPPED ROW MAY HAVE NO POSITION. The perimeter admits a site the company
# has confirmed and a citable source can place, and the second half is research
# that only pays for itself on a works somebody might visit. A project that will
# not be built has no works to place, and hunting the parcel of a factory that
# was cancelled two years ago buys a dot on a map nobody should read as a
# building. So location is sought for ACTIVE rows, and a stopped row says in its
# own note that it was not sought -- which is a decision on the record rather
# than a gap that looks like an oversight. See sources/scope.md, "A stopped row
# does not enter the location queue".
STOPPED_STATUSES = ("cancelled", "paused")


# AND `paused` READS THREE WAYS ON PURPOSE, which is why the two tuples above
# disagree about it in plain sight. It is ALIVE for the counting groups (a paused
# project can resume, and one paused for three years is exactly what an attrition
# series measures), STOPPED for the drawing rule (there is no works to place, so
# no coordinate is sought), and its OWN group in sources/export_status_history.py
# (it is what the attrition paper is about). The three are not a contradiction to
# be settled: they are three questions with three right answers, and each is
# declared where it is used rather than one being bent to serve all three.


# WHAT KIND OF EVENT AN ENTRY IN A STATUS HISTORY IS. A history is a record of
# what was published about a project, and not everything published about it
# moves it along the ladder: money can be committed and a site can change hands
# without the status changing at all. Naming the kind is what lets a count of
# status changes be a count of status changes.
#
#   status      the ordinary entry: a source reports where the project has got
#               to. Every entry that says nothing else is one of these, which is
#               why the backfill could set it without reading anything.
#   ownership   the project changed hands. The site is continuous and its OWNER
#               broke; a history that could not say so would have to choose
#               between a cancellation that did not happen and an acquisition
#               that never appears. Northvolt Ett is the case that forced it.
#   financing   money reached, or left, the project. Distinct from the `funded`
#               status, which is a rung on the ladder: a second grant to a
#               project already funded is a financing event and not a move.
#
# AN OWNERSHIP EVENT STILL CARRIES A STATUS, and it is the status the project was
# already in. Three things fall out of that and all three are wanted:
#
#   the append-only invariant survives -- the last entry's status still equals
#   the project's, so a header and a timeline cannot disagree;
#
#   is_transition already handles it -- the status is unchanged, so an ownership
#   event is not a transition, and the three sentence templates that render an
#   entry as "was paused on {date}" skip it without being told to;
#
#   and the feed, which wants the latest thing on file rather than the latest
#   MOVE, shows it with a true status chip beside it.
#
# ONE FACT PER ENTRY. An ownership event may not also change the status: the gate
# refuses one whose status differs from the entry before it, because a company
# changing hands on the same day a project is paused is two events and reads as
# one cause. For the same reason an ownership event may not be the first entry --
# there is nothing for its status to be unchanged FROM, and is_transition would
# have to call it a status change.
PROJECT_EVENT_KINDS = (
    "status",
    "ownership",
    "financing",
)


# WHO IS SPEAKING IN THE SOURCE BEHIND AN EVENT. `confidence` above says how
# close the speaker is to the fact; this says what kind of body they are, which
# is the cut an attrition series needs: a cancellation a company announces and a
# cancellation visible only because a permit was withdrawn are the same fact
# reaching the record by two different routes, and how often each route carries
# it is itself a finding.
#
#   company         the operator or its parent, speaking about its own project.
#   permit          a planning or environmental consent file, and the authority's
#                   own record of the procedure.
#   regulator       a supervisory or competition authority acting on the project.
#   grant_register  a public register of awards — the Innovation Fund's, a state
#                   aid decision, a national programme's list.
#   wire_release    a company release carried by a wire service. It is the
#                   company speaking, through a distributor that keeps the page
#                   alive after the company's own site has dropped it.
#   official_register
#                   official public records: gazettes, insolvency notices,
#                   company registries. ADDED BECAUSE `regulator` WAS DOING TWO
#                   JOBS. A supervisory authority ACTING on a project and a
#                   statutory register RECORDING that something happened to the
#                   company are not the same route into the record, and an
#                   attrition series cares about the difference: the first is
#                   somebody intervening, the second is the state writing down a
#                   fact that already occurred. The London Gazette's appointment
#                   of administrators is the case — the Gazette did not act on
#                   Britishvolt, it published the notice.
#   press           anyone reporting on the project rather than acting in it.
PROJECT_SOURCE_TYPES = (
    "company",
    "permit",
    "regulator",
    "grant_register",
    "official_register",
    "wire_release",
    "press",
)


# WHETHER THE RECORD WATCHED THE EVENT OR RECONSTRUCTED IT. An event dated before
# the day its project row first entered this repository was written up from the
# archive; one dated after was seen as it happened. The distinction is not a
# quality judgement — a retrospective entry can rest on a better source than a
# live one — but a dataset built backwards has a survivorship problem a dataset
# built forwards does not, and an attrition rate computed over the two without
# separating them is two different measurements added together.
EVIDENCE_MODES = (
    "retrospective",
    "live",
)


# WHAT A PROJECT SAID IT WOULD DO, AND WHEN IT SAID IT. `stated_schedule` is a
# second history beside `status_history`, and the two answer different questions.
# status_history records what HAPPENED: the project moved, and here is the source.
# stated_schedule records what was PROMISED: on this date, from this source, the
# operator said the plant would start producing in that year.
#
# WHY IT CANNOT BE A FIELD ON THE ROW. A single `target_date` would be overwritten
# every time a company restated it, and the overwrite is the finding. A project
# that has said 2026, then 2027, then 2028 is not a project with a 2028 target; it
# is a project that has slipped twice, and the only way to see that is to keep
# every statement. So EVERY REVISION IS A NEW EVENT and the original is never
# edited -- the same append-only discipline status_history already has, for the
# same reason.
#
# A SLIP IS NOT A STATUS CHANGE, which is why this could not live in the other
# history. A plant whose start date moves from 2026 to 2028 has not changed status
# and never appears in the transition matrix. It is the commonest way a project
# fails without any event recording it, and before this list there was nowhere in
# the register to put it.
SCHEDULE_MILESTONES = (
    "production_start",     # the plant makes its first saleable output
    "commissioning",        # the works is handed over and starts up
    "fid_target",           # a final investment decision is expected by then
    "construction_start",   # ground is to be broken
)

# WHO MADE THE PROMISE, which is a different question from how it reached us.
# `source_type` says the route -- a company release, a permit file, a wire, the
# press. `speaker` says whose statement it is. The two come apart constantly and
# the gap is where the meaning lives: the Junta de Extremadura telling its own
# Assembly that cells come in December 2028 is a HOST GOVERNMENT statement that
# reached this register through a newspaper, and recording it as "press" would
# lose the fact that a government said it.
#
# AND IT DECIDES WHAT COUNTS AS A SLIP. A revision is one speaker changing its own
# mind, and only that. Two speakers giving different dates for the same milestone
# have not revised anything -- they disagree, which is a fact about the evidence
# and not about the project. Counting a disagreement as a slip would manufacture
# delay out of a government and a company being asked on the same day, and it
# would do so in the direction that makes the register look more informative than
# it is. So a slip is measured within a speaker and a disagreement is reported
# beside it, never inside it. See sources/scope.md, "A slip is one speaker
# changing its mind".
#
#   company           the operator or its parent, about its own project.
#   host_government   the state, region or municipality hosting the works, or an
#                     agency of it. It is the speaker whether it speaks in a
#                     release, a permit or an answer to its own parliament.
#   eu                the Commission or an EU body -- a state aid decision, an
#                     Innovation Fund award.
#   other             anyone else who states a date: trade press, a consultant, a
#                     customer. Named rather than excluded, so that a date from
#                     one of them is visible as such rather than absent.
SCHEDULE_SPEAKERS = (
    "company",
    "host_government",
    "eu",
    "other",
)


# HOW EXACTLY THE TARGET WAS STATED, because a company that says "2028" and a
# company that says "December 2028" have not made the same promise, and flattening
# both to a date would invent precision the source does not carry. The value is
# stored in the shape the source used -- YYYY, YYYY-Hn, YYYY-Qn, YYYY-MM,
# YYYY-MM-DD -- and this says which.
#
# `half` IS HERE BECAUSE THE DATA REQUIRED IT. Lyten said "the second half of
# 2026" about Northvolt Ett, which is neither a year nor a quarter; rounding it to
# either would be this register choosing a number the company did not.
#
# A TARGET IS READ AT THE END OF ITS PERIOD, everywhere it is compared. "2029" is
# not missed until 31 December 2029, and treating it as 1 January would report a
# project as late for a year in which it is still on time. This is the opposite
# convention from a history DATE, which is padded to the first of its period
# because that is the earliest the event can have happened -- both choices are the
# reading that does not overstate.
# HOW EXACTLY AN EVENT WAS DATED, which is a different question from how exactly
# a TARGET was stated and needed its own field once the answer stopped always
# being "to the day".
#
# Most events on this file come from a dated release and are known to the day.
# Some are not: a company page says a grant arrived "in 2023"; a filing says a
# project went bankrupt "in January 2024"; a quarterly result reports something
# that happened in a quarter. Those events are real, they belong on the history,
# and the register has been storing them as a padded date with the padding
# explained in prose — which no count can read.
#
# SO THE DATE IS ALWAYS A FULL YYYY-MM-DD AND THE PRECISION SAYS WHAT IT MEANS.
# A month-precision event is padded to the FIRST of its month and a
# year-precision event to 1 January, because that is the earliest the event can
# have happened and it is the reading that does not overstate. This is the
# opposite convention from a stated TARGET, which is read at the END of its
# period for the same reason: neither may claim more than the source did.
#
# A DATE THAT IS PADDED AND DOES NOT SAY SO IS THE FAILURE THIS CLOSES. Before
# this field, "2024-01-31" on the Italvolt row meant "sometime in January 2024,
# and I have put it at the end so as not to claim precision" — a convention that
# was written in a note, that contradicted the padding rule in scope.md, and that
# a series computing how long a project took would have read as the 31st.
EVENT_DATE_PRECISIONS = (
    "day",
    "month",
    "year",
)

# AND IT IS NOT ONLY EVENTS. Ruled 9 September 2026, one ruling after the events
# got it: `capacity_as_of` and a parameter's `date_of_value` are dates of the same
# kind, answering the same question — when was this true, and how exactly does the
# source say so — and they were left without a precision for exactly one day. The
# cost of that day is on the Galp row, whose capacity had to stay on its lender's
# sentence rather than the company's, because the company's sentence is dated to a
# year and the field could not say so.
#
# The vocabulary and the padding are the same, deliberately: one convention for
# every date on this layer that records when something WAS, and the opposite one
# for a target, which records when something WILL BE and is read at the end of its
# period. Two rules, pointing in opposite directions, each the reading that does
# not overstate.
VALUE_DATE_PRECISIONS = EVENT_DATE_PRECISIONS


# AND A SOURCE'S DATE HAS A FOURTH STATE THE OTHER THREE CANNOT SAY. Ruled 11
# September 2026, with the archive fallback.
#
# `not_after` MEANS THE DOCUMENT CARRIES NO DATELINE AND THIS IS THE LATEST IT CAN
# BE. It is used where a source survives only as an Internet Archive capture and
# the publisher never dated the page: the capture proves the text existed on that
# day and says nothing about when it was written. Ørsted's Skovgaard release is
# the case — no meta date, no date in the body, and a URL path saying 2022/12
# which is the publisher's filing and not the document's dateline.
#
# IT IS NOT `day`. A day says the publisher published on that day. An upper bound
# says nobody knows, and the difference matters to anything that reads a date as
# evidence of when a thing was said: the register's own slip and disagreement
# arithmetic would otherwise treat a capture date as a statement date and compute
# delays out of when somebody happened to crawl a page.
#
# WHERE THE DOCUMENT DOES CARRY A DATELINE, THE DATELINE WINS AND THE CAPTURE GOES
# TO `captured_at`. IGNIS's page is the case on the other side: its own metadata
# says 23 September 2024, which is the date, while the capture of 16 April 2026 is
# only how this register reached it.
SOURCE_DATE_PRECISIONS = EVENT_DATE_PRECISIONS + ("not_after",)


TARGET_PRECISIONS = (
    "year",
    "half",
    "quarter",
    "month",
    "day",
)


# CAPACITY, AND WHY IT IS NOT THE `capacity` BLOCK ALREADY ON THE ROW. That block
# holds whatever figure a project is best known by, and across these sectors it
# is not one quantity: for the cement rows it is CO2 captured per year, for the
# steel rows it is tonnes of three different products, and for a battery row it
# is GWh. A denominator has to be one quantity, so the capacity_* fields are the
# PRODUCT the plant makes, in two units and nothing else, and a row whose known
# figure is not that leaves them empty rather than bending it to fit.
#
# HYDROGEN ADDED FOUR UNITS AND A RULE ABOUT NOT ADDING THEM. An electrolysis
# project is quoted three ways by three different kinds of source -- the
# electrical rating of the electrolyser (MW input), the hydrogen it makes stated
# as a power or a flow (MW output, Nm3/h), and the tonnes a year it is expected
# to produce -- and the three are related only through an efficiency and a
# capacity factor that the source does not state. Converting between them here
# would put a number on the page that nobody published, computed from an
# assumption nobody wrote down; the IEA's own database does convert, calls the
# result "normalised capacity", and its definitions sheet describes that column
# once as MW electrical and once as "MW H2 output (LHV)" -- which is exactly the
# ambiguity this register refuses to inherit. See sources/scope.md, "Three units
# for one electrolyser, and no conversion between them".
#
# SO A ROW RECORDS THE FIGURE IN THE UNIT ITS SOURCE USED, and where a source
# states the same phase in two units both are kept, in `capacity_alternates`,
# with the row's own capacity_value being the one the export prefers.
CAPACITY_UNITS = (
    "t_per_year",
    "GWh_per_year",
    "t_co2_per_year",
    "MW_input",         # the electrolyser's electrical rating
    "MW_output",        # the hydrogen, stated as a power
    "Nm3_h",            # the hydrogen, stated as a flow
    "t_h2_per_year",    # the hydrogen, stated as an annual mass
    "t_nh3_per_year",   # ammonia, where the source states ammonia only
)

# WHICH UNIT THE EXPORT PREFERS WHEN A ROW STATES TWO. MW input is the figure the
# perimeter's threshold is measured on and the figure every other source in this
# sector can be compared against, so it wins where it is present; the order below
# is the fallback chain and nothing outside it is ever chosen automatically.
CAPACITY_UNIT_PREFERENCE = (
    "MW_input",
    "MW_output",
    "Nm3_h",
    "t_h2_per_year",
    "t_nh3_per_year",
)

# HOW FIRM THE FIGURE IS. The same number means different things at these
# stages, and attrition measured against announced capacity is a different
# series from attrition measured against capacity somebody committed money to.
#
#   announced  the company states it is building towards this figure.
#   fid        the figure was fixed at a final investment decision.
#   operating  the figure describes a works that is running.
#   official   THE FIGURE COMES FROM AN OFFICIAL RECORD NAMING THE SITE rather
#              than from the company: a permit, a state aid decision, a
#              host-state grant decision. It is a separate basis and not a
#              flavour of `announced` because the speaker is different and the
#              failure modes are different — an applicant's filed plan is a
#              number the company gave an authority, and a grant decision is a
#              number an authority was willing to pay against. Both are checkable
#              in a way a press figure is not, and neither is the company saying
#              what it is building towards today. See sources/scope.md,
#              "Admission and capacity are separate questions".
CAPACITY_BASES = (
    "announced",
    "fid",
    "operating",
    "official",
)

# WHAT THE PLANT MAKES, in the source's own word. Closed, because "steel" and
# "crude steel" and "directly reduced iron" are three different tonnes and a free
# text field would let them be added up.
CAPACITY_PRODUCTS = (
    "clinker",
    "cement",
    "crude_steel",
    "dri",
    "steel",
    "co2_reduced_steel",
    "battery_cells",
    # WHAT AN ELECTROLYSIS SITE MAKES. `hydrogen` is the molecule; `ammonia` is
    # here because a synthesis plant fed by its own electrolyser is sometimes the
    # only thing its source quotes a tonnage for, and a register that could only
    # record hydrogen would have to leave the figure out or invent one. The two
    # are kept apart by their units -- t_nh3_per_year is the only annual mass
    # `ammonia` ever takes -- so a tonne of ammonia can never be added to a tonne
    # of hydrogen.
    "hydrogen",
    "ammonia",
    # NOT A PRODUCT THE PLANT SELLS, and it is in this list anyway. A capture
    # retrofit's output is the tonne it stops: the cement rows' known figure is
    # CO2 captured per year, the works makes the same clinker it always did, and
    # a register that could only record saleable product would have to leave
    # every one of them empty. It is kept apart from the rest by its unit --
    # t_co2_per_year is the only unit it ever takes -- so nothing can add a tonne
    # of captured CO2 to a tonne of crude steel.
    "CO2 captured",
)

# THE SECTORS A CAPACITY FIGURE IS SOUGHT FOR. Not every sector in the file has a
# product capacity that means anything — a CO2 store's capacity is a different
# quantity in a different unit — so the gate asks for these three and is silent
# about the rest.
CAPACITY_SECTORS = ("cement", "steel", "batsol", "ccs", "clean")


# WHICH PRODUCT EACH UNIT CAN BE A UNIT OF. A closed vocabulary of units and a
# closed vocabulary of products still lets a row say "45,000 t_nh3_per_year of
# hydrogen", which is a sentence nobody can act on and which a later total would
# add to the hydrogen column. The pairing is therefore declared, and a unit that
# is not in this table is a unit no product constrains -- the three original
# units stay unconstrained because their sectors have one product each and the
# `capacity_product` field already carries it.
UNIT_PRODUCTS = {
    "MW_input": ("hydrogen",),
    "MW_output": ("hydrogen",),
    "Nm3_h": ("hydrogen",),
    "t_h2_per_year": ("hydrogen",),
    "t_nh3_per_year": ("ammonia",),
}


# WHY A SITE IS NOT MOVING, IN THE SOURCE'S OWN TERMS. Every pause and every
# cancellation carries one of these, and it is read off what the source says
# rather than inferred from what happened around it. `unstated` is the ordinary
# answer and is not a failure: a company that stops a project without saying why
# has told us something, and recording a guess in that space would turn the
# commonest fact in this dataset -- that reasons are not given -- into a
# distribution of reasons somebody made up.
#
# The vocabulary is the one the hydrogen brief names, and it is deliberately
# about the WORLD rather than about the company: `finance` is money not arriving,
# `offtake` is nobody contracting to buy, `policy` is a rule or a subsidy moving,
# `infrastructure` is a pipeline, a grid connection or a store not being there,
# `cost` is the build costing more than the plan, `ownership` is the owner
# changing or failing.
STOP_REASONS = (
    "finance",
    "offtake",
    "policy",
    "infrastructure",
    "cost",
    "ownership",
    # TWO VALUES THE FIRST RE-READ FORCED, added 9 September 2026. Fifteen
    # stopping transitions were read against their own sources and two of them
    # stated a cause the original seven could not hold:
    #
    #   strategy  the owner changed the business it is in. FREYR did not fail and
    #             did not change hands; it pivoted to solar in the United States
    #             and classified its European battery assets as held for sale.
    #             Filed as `ownership` for one day, which said the owner changed
    #             when the owner's MIND changed.
    #   partner   a party the project cannot proceed without withdrew or failed,
    #             and it is not the owner and not the customer. NOVO Energy lost
    #             its technology partner; the plant has money, a site and a
    #             customer, and no technology.
    "strategy",
    "partner",
    # AND `maturity` IS THE THIRD THE RE-READS FORCED, added 9 September 2026.
    # The owner cites its own readiness — the technology is not ready, or the
    # supply chain that would build it is not — rather than a fact about money,
    # a customer, a rule or an owner. Gigastack is the case: Phillips 66, Ørsted,
    # ITM Power and Element Energy paused a 100 MW electrolyser at a working
    # refinery saying "further project maturation and supply chain development is
    # needed", which none of the eight other values could hold. It was filed at
    # `policy` for part of a day, read from the fact that they had withdrawn from
    # the revenue-support round, which described what they DID and not what they
    # SAID.
    #
    # IT IS NOT A POLITE `unstated`. A reason is given and it is specific: the
    # thing that is not ready is the project itself. An attrition series that can
    # separate "nobody would pay for it" from "it could not be built yet" is
    # answering a different question from one that cannot.
    "maturity",
    "unstated",
)

# STOP REASONS ARE AN ORDERED LIST, FIRST ENTRY PRIMARY. Sources give more than
# one: SVOLT names threatened tariffs, unevenly distributed subsidies AND a lost
# customer project in a single sentence; ArcelorMittal names energy costs and
# then weak demand and high imports. A single-valued field made the register
# choose one and drop the rest into prose, where nothing can count them.
#
# THE FIRST ENTRY IS THE ONE THAT CHANGED — what stopped the project now, as
# against the conditions it was already living with — and it is what a
# single-reason series should be built on. The rest are the conditions, in the
# order the source gives them. `unstated` may only appear alone: a source that
# gives no reason cannot also give a secondary one.

# The statuses that owe a stop_reason. Read from the same place the drawing rule
# reads, so the two cannot drift.
STOP_REASON_STATUSES = STOPPED_STATUSES


# WHO OWNS THE OPERATOR, AS A LIST, because a project company is usually more
# than one party and a single label loses the thing the paper is asking about.
# `owners` is [{name, share, listing}] — share is the percentage where a source
# states one and null where it does not, and listing is one of OWNER_LISTINGS
# below, for that party.
#
# `owner_listing` IS DERIVED FROM IT AND STILL STORED, because the comparison the
# paper makes is per row and a reader should not have to compute it: it is the
# listing of the party holding more than half, and `mixed` where nobody does. The
# gate checks the derivation rather than trusting it, so a row cannot say
# `listed` over a list that does not support it.
#
# WHETHER THE OWNER PUBLISHES. The paper this dataset feeds compares how much a
# project discloses against who owns it, and that comparison needs the owner type
# on the row rather than in somebody's head: a listed company files, a state-owned
# one answers to a parliament, and a private one need do neither. It is about the
# party that OPERATES the site -- for a joint venture, the lead named on the row.
OWNER_LISTINGS = (
    "listed",
    "private",
    "state-owned",
    # NOBODY HOLDS A MAJORITY, so nothing about the operating company's
    # disclosure follows from who owns it. Ruled 9 September 2026 after Hamburg
    # Green Hydrogen Hub — 74.9 per cent a private asset manager, 25.1 per cent a
    # city utility — showed that the single-value field only worked because that
    # split happened to have a majority. A 50:50 venture had no honest answer.
    "mixed",
    # AND `unknown` IS THE FOURTH, ADDED THE SAME DAY. `mixed` is a statement
    # about a split between named parties; this is the state where the split
    # itself is not on file. EWE AG is the case: not listed on any exchange, held
    # by East Frisian and Oldenburg municipal associations together with a
    # private infrastructure investor, and no source read here says in what
    # proportion. `private` and `state-owned` would each be an assertion.
    #
    # IT IS NOT THE SAME AS AN EMPTY FIELD and that is the whole of why it
    # exists: an empty field cannot tell "the sources do not say" from "nobody
    # asked", and a comparison of disclosure by owner type needs the difference.
    # A row that carries it still carries the note saying what was looked at.
    "unknown",
)


# DEPENDENCY EDGES, AND THE ONE CLASS THIS STEP CODES
# ===================================================
# A hydrogen site is defined by what it is attached to. It needs power, water and
# a grid connection; it reaches its customer through a pipeline or a truck; and
# the customer is usually a works that already exists and is in this register
# under another sector. None of that is visible on a row that only says how many
# megawatts it is.
#
# TWO CLASSES OF EDGE, AND ONLY ONE OF THEM IS DATA. An ASSERTED edge is one the
# project's own source names: "the hydrogen will be delivered to the refinery in
# Gonfreville", "connected directly to the hydrogen core network". It is evidence,
# it carries the sentence it was read from, and it is what this step codes. A
# STRUCTURAL edge is one that follows from the technology -- every electrolyser
# needs a grid connection whether or not anybody said so -- and it is NOT coded
# here: it belongs to a technology rule, applied once, in a later step. Writing
# structural edges by hand now would produce a graph in which the two kinds look
# identical and only the author knows which is which.
EDGE_CLASSES = (
    "asserted",
    "structural",   # declared, and not written by hand -- see above
)

# WHICH WAY THE EDGE POINTS. `supplies` is the project sending something out;
# `depends_on` is the project waiting for something. Both are recorded from the
# project's own end, so a reader of one row sees both halves of its position.
EDGE_KINDS = (
    "supplies",
    "depends_on",
)

# WHAT KIND OF THING IS ON THE OTHER END. The brief's four, unchanged:
#   infrastructure  a pipeline, a store, a terminal, a grid or a water connection
#   material        a molecule or a tonne moving between two works
#   regulatory      a consent, a designation or a rule the project waits on
#   funding         money the project is waiting for or standing on
EDGE_TYPES = (
    "infrastructure",
    "material",
    "regulatory",
    "funding",
)


# THE OUTSIDE LISTS THIS REGISTER IS MEASURED AGAINST. Named here rather than in
# the export, because the ids live on the rows and a row carrying an id under a
# key nothing recognises is an id nobody can resolve.
#
#   odenweller_ueckerdt_2025
#       The project list behind Odenweller and Ueckerdt, "The green hydrogen
#       ambition and implementation gap", Nature Energy (2025). It is the IEA's
#       October 2023 database after their own quality check, and the id is that
#       file's `Ref` column.
#   iea_hydrogen_production_projects
#       The IEA's own live Hydrogen Production Projects database, read through
#       its public project endpoint. The id is `projectReference`.
#
# THE TWO ARE NOT INDEPENDENT and the benchmark file says so: the first is a
# quality-checked snapshot of the second, two years older. Matching against both
# measures two different things -- whether this register holds what the published
# academic list held, and whether it holds what the IEA holds today.
BENCHMARKS = (
    "odenweller_ueckerdt_2025",
    "iea_hydrogen_production_projects",
)



# NOT EVERY ENTRY IN A STATUS HISTORY IS A STATUS CHANGE, and the difference has
# to be named because three sentence templates on this site render an entry as
# one: "{project} was paused on {date}".
#
# A history is a list of EVENTS, in date order. Most are transitions -- the
# project moved from one status to the next, and the entry's date is the date it
# moved. Some are not: a later source reports on a project whose status it does
# not change. Slite is the case that forced this. It was paused on 19 November
# 2025 when the Swedish Energy Agency declined to co-fund it; on 1 January 2026
# Heidelberg Materials withdrew the permit application, which is a fact about a
# paused project rather than a project becoming paused. Both belong in the
# history -- the second is the evidence that the register has read the later
# news and still says paused -- and rendering the second as a transition would
# put "Slite CCS was paused on 1 January 2026" on three pages, which no source
# says.
#
# THE RULE IS POSITIONAL, not a flag on the row. An entry is a transition if its
# status differs from the entry before it; the first entry always is. That
# cannot fall out of step with the data the way a hand-set `transition: false`
# would, and it needs nothing added to any row.
#
# IT IS WRITTEN TWICE, AND HELD BY A GATE. web/lib/transition.ts
# statusTransitions is the same rule for the page, and check_transition_parity.py
# runs both readings over every history up to four entries long -- 4,681 of them
# -- and fails the build on any disagreement. The two sides used to be held by a
# comment on each saying "edit both", which is what the reach-channel inference
# is still held by and is not a mechanism.

# WHERE A PROJECT HAS STOPPED MOVING, and it is a different question from where
# it has stopped being reported. Two statuses are TERMINAL for that question:
# `operating` has climbed the whole ladder and has nowhere left to go, and
# `cancelled` will not move again. Everything else is a project that is supposed
# to be going somewhere, including `paused` -- a paused project can resume, and
# one that has been paused for three years is exactly what a stalling listing is
# for.
TERMINAL_STATUSES = frozenset({"operating", "cancelled"})


def is_transition(history: list[dict], i: int) -> bool:
    """Whether entry `i` is the moment the project's status changed."""
    return i == 0 or history[i]["status"] != history[i - 1]["status"]


def transitions(project: dict) -> list[dict]:
    """Only the entries that changed the status. What a feed of "what moved"
    should be built from, and what a sentence saying a project MOVED may use."""
    history = project.get("status_history") or []
    return [h for i, h in enumerate(history) if is_transition(history, i)]


def entered(project: dict) -> dict | None:
    """The entry that put the project into the status it is in now -- the first
    of the trailing run, not the last entry.

    This is the date "was paused on" means. `status_history[-1]` is the latest
    thing ON FILE about the project, which is a different question and is the
    right answer for a feed, a "last change" column or an "as of" date.
    """
    changes = transitions(project)
    return changes[-1] if changes else None

# WHAT KIND OF PLACE A PROJECT ROW IS. `plant` is the default and is left off the
# row; a row that says nothing is a works. `storage` is a permitted or proposed
# geological store -- the place a captured tonne ends, which the graph referred
# to as a technology long before it named one. Closed, and short on purpose: a
# role is a mark on a map, and a vocabulary with eight of them would be eight
# marks nobody can tell apart.
PROJECT_ROLES = (
    "plant",
    "storage",
)

# WHERE A COORDINATE CAME FROM, and it is recorded per site rather than assumed.
#
# The rule this vocabulary enforces has not changed and is the one the register
# has always had: a coordinate must come from a citable source that identifies
# THE WORKS SPECIFICALLY. What changed is that the basemap is no longer the only
# thing that can do that. Batteries made the old reading untenable -- ACC's
# Kaiserslautern site is real, company-confirmed and carries no OpenStreetMap
# feature at all, and a rule that admits a works only when a volunteer has
# already drawn it is a rule about OpenStreetMap's coverage rather than about
# evidence.
#
# So four kinds of source may put a works on the paper:
#
#   basemap     an OpenStreetMap feature, with its tags quoted, so a reader can
#               see that the polygon is the works and not the industrial estate
#               around it. Still the best of the three, because the geometry and
#               the identification are the same object.
#   company     the operator's own materials naming a street address or a land
#               parcel. The company knows where its works is; what this costs is
#               that the coordinate is then derived from an address rather than
#               read off a shape, so the address itself is quoted alongside. AND
#               THE ADDRESS HAS TO BE THE WORKS'. A registered office or a filing
#               address is an address for serving papers; see the corollary in
#               sources/scope.md and the pair it is written from.
#   permit      a state permitting, planning or zoning filing that states a
#               position itself: a grid reference, a coordinate pair, an address.
#               Often the most precise of these -- and it is a public document
#               that outlives a press release.
#   plan_parcels
#               a plan that names its PARCELS but no position, resolved through
#               the state cadastre that holds their geometry. Two documents doing
#               one job: the plan says which parcels, and neither of them alone
#               places anything -- the cadastre knows where parcel 121/4 is and
#               nothing about what was to be built on it, and the plan knows what
#               was to be built and gives no coordinate. It is recorded as its own
#               type rather than folded into `permit` because the reader has a
#               different question to ask of it: not "do you trust this filing"
#               but "did the right parcels get selected, and did the cadastre
#               answer for all of them". A row on this type therefore carries the
#               parcel list, the register it was resolved against, the date it was
#               read, and how many of the named parcels were found.
#
# WHAT IS STILL REFUSED, and this is the whole point of naming them. A town
# name run through a geocoder is not a source about a works, it is a source about
# a town, and `precision: "town"` already fails by name. A position read off a
# picture in a news story is not citable: nobody can check it and the next reader
# gets a different number. Neither has a value in this vocabulary, so neither can
# be recorded without inventing one, which is the point of a closed list.
#
# AND WE DO NOT DRAW THE POLYGON OURSELVES. Where the basemap has no feature for a
# works, the answer is a permit, a published address, or the row staying off file
# -- never an edit to OpenStreetMap made in order to cite it. The temptation is
# real and the reasoning is easy: we know where the works is, OSM is editable, and
# `basemap` would then be true of the row. It would also be circular. The
# coordinate's whole claim is that somebody independent put the works there, and
# an edit made to be cited LAUNDERS AN ASSERTION INTO A SOURCE TYPE -- it converts
# "we believe this is the site" into "the basemap says so", which is a stronger
# claim than we hold and one no reader could unpick.
#
# This says nothing against improving OpenStreetMap. It says that a coordinate
# this repository publishes may not rest on an edit this repository made for the
# purpose, and that the two must not be done in the same breath.
LOCATION_SOURCE_TYPES = (
    "basemap",
    "company",
    "permit",
    "plan_parcels",
)


# HOW A SITE IS CONFIRMED, WHEN ONE SOURCE CANNOT DO IT ALONE
# ===========================================================
# The perimeter's site rule is company-only: a project whose specific site the
# company has not confirmed is not held. That rule is right and it has already
# refused a candidate outright -- InoBat's Spanish site, where the only company
# statement was conditional and nothing followed it.
#
# Sunwoda is the case it could not decide. The company confirms the project and
# the country and never names the town: its newsroom release says "Hungary", its
# 2025 Shenzhen-filed interim report lists "Hungary Sunwoda Power Technology Co.,
# Ltd" with Hungary as its place of business, and neither says Nyíregyháza. The
# Hungarian government's own briefing room does say it, and the basemap carries a
# works whose name is the operator's own subsidiary at an address in that town.
#
# Read strictly, company-only refuses a site that three independent sources agree
# on. Read loosely, it stops meaning anything. So it is neither stretched nor
# abandoned: a SECOND, NAMED standard is defined, and a row says which one it
# stands on.
#
# THE COMPOSITE STANDARD HAS THREE LEGS AND ALL THREE ARE REQUIRED:
#
#   company    the operator's own materials confirming the project and the
#              country. Not the town -- if the company named the town, the
#              ordinary standard is met and this one is not needed.
#   state      a primary of the host state naming the site. A government's own
#              publication, not an agency's summary of it and not press relaying
#              either.
#   basemap    a feature carrying the operator's name, corroborating that
#              something of theirs stands where the state says it does.
#
# WHY THIS IS NOT A WEAKENING. Each leg is weak where the others are strong. The
# company knows what it is building and will not always say where; the state
# knows where because it permitted and subsidised it; the basemap knows what is
# physically there and nothing about who intends what. One source doing all three
# jobs is the ordinary case; three sources doing one job each is not a lower bar,
# it is a different one, and it is only available when no single source clears
# the first.
#
# EVERY LEG IS CITED ON THE ROW, and the note says plainly that the company
# source names no city. A reader who disagrees with the standard can see exactly
# what it was applied to.
SITE_EVIDENCE_KINDS = (
    "company",      # the ordinary standard: the operator names its own site
    "composite",    # the three legs above, all cited
)


# HOW EXACT A COORDINATE IS. `plant` is the works itself; `site` is a store, a
# field or a receiving terminal, which has a position but not a street. `town`
# is listed and is not allowed on a project: the gate refuses it by name, so the
# refusal reads as a rule rather than as a missing value. A town centroid drawn
# as a plant is a wrong fact rendered confidently, which is worse than no map.
LOCATION_PRECISIONS = (
    "plant",
    "site",
    "town",
)

# The precisions a project or a plant may actually carry. See the note above.
LOCATION_PRECISIONS_ALLOWED = ("plant", "site")


# HOW THE POSITION WAS RESOLVED, WHICH IS A DIFFERENT QUESTION FROM HOW EXACT IT IS
# =================================================================================
# `precision` above says what KIND of place the point is — a works or a site — and
# it has said so since the geo layer landed. It cannot say how the point was
# arrived at, and after the hydrogen ruling of 9 September 2026 that is the
# question a reader has to be able to ask.
#
# The ruling admits a site whose position is the HOST WORKS it stands on: an
# electrolyser being built inside a refinery is placed on the refinery, because
# that is where it is and because waiting for a volunteer to draw a building that
# does not exist yet is a rule about OpenStreetMap's coverage rather than about
# evidence. That is right, and it costs something: a mark on the paper now means
# one of three different things, and nothing on the row said which.
#
#   works   the coordinate is a WORKS POLYGON somebody drew — the installation
#           itself where the basemap has it, the works it stands on where it does
#           not. `host_works` names the second case, so the two are never
#           confused, and the sentence over the picture says how many of its marks
#           are which.
#   parcel  the coordinate was computed from named cadastral parcels: a plan says
#           which parcels, a state register holds their geometry, and neither
#           alone places anything.
#   point   the coordinate is a POSITION SOMEBODY STATED — a grid reference in a
#           permit, an address the operator published, a coordinate pair in a
#           technical source. The most precise of the three where the source is
#           good, and the one that rests on the fewest shapes.
#
# IT IS RECORDED PER SITE AND NOT PER ROW, because a row is not always at one
# place: ArcelorMittal covers Bremen and Eisenhüttenstadt, and one field on the
# row would have to pick between two answers or average them. Every row carries it
# in the only place it can be true — on each of its sites.
# WHETHER THE ROW HAS A POSITION AT ALL, AT ROW LEVEL, AS ITS OWN QUESTION.
# Split from location_precision on 9 September 2026, and the reason is that one
# name was doing two jobs at two scopes: `none` could only ever be a row and
# `works`/`parcel`/`point` could only ever be a site, which is coherent and is
# not readable. Two fields, two scopes, and neither has to be explained.
#
#   yes   the row has at least one site, each with a coordinate and a precision.
#   no    it has none, it is admitted anyway, and its `location_note` says where
#         a polygon was looked for and what was found instead.
LOCATED = (
    "yes",
    "no",
)

# HOW THE POSITION WAS RESOLVED, PER SITE, and only on a row that has one.
#
#   works   the coordinate is a WORKS POLYGON somebody drew — the installation
#           itself where the basemap has it, the works it stands on where it does
#           not. `host_works` names the second case, so the two are never
#           confused, and the sentence over the picture says how many are which.
#   parcel  the coordinate was computed from named cadastral parcels: a plan says
#           which parcels, a state register holds their geometry, and neither
#           alone places anything.
#   point   the coordinate is a POSITION SOMEBODY STATED — a grid reference in a
#           permit, an address the operator published, a coordinate pair in a
#           technical source.
#
# IT IS RECORDED PER SITE AND NOT PER ROW, because a row is not always at one
# place: ArcelorMittal covers Bremen and Eisenhüttenstadt, and one field on the
# row would have to pick between two answers or average them.
LOCATION_PRECISION_VALUES = (
    "works",
    "parcel",
    "point",
)

# WHICH PRECISION EACH KIND OF SOURCE CAN SUPPORT. Declared rather than left to
# judgement, and gated, because the whole value of the field is that it is read
# off the evidence: a basemap feature is a shape, a plan-and-cadastre pair is a
# parcel list, and an address or a grid reference is a stated point. A row that
# claimed `point` on a basemap polygon would be claiming a precision the source
# does not have.
LOCATION_PRECISION_BY_SOURCE = {
    "basemap": "works",
    "plan_parcels": "parcel",
    "company": "point",
    "permit": "point",
}

# The legal device a measure acts with, as a diagram says it. Closed for the
# usual reason and one extra: these words are the only part of a measure label
# that repeats across sectors, so an open list would give every sector its own
# word for the same device and quietly break the comparison the labels exist to
# make. `None` is a legitimate value -- see data/transition/measure_labels.json.
INSTRUMENTS = (
    "obligation",
    "prohibition",
    "requirements",
    "phase-out",
    "grants",
    "levy",
    "target",
    "threshold",
    "access rule",
)

# A diagram node is 236 units wide and the label sits at 12px. Past this it is
# an ellipsis, and an ellipsis on the one word that says what the measure does
# is worse than no label at all.
MAX_SHORT_LABEL = 26

# What a material IS in the chain, which is the only thing that decides where it
# is drawn. `by_product` and `waste_stream` are kept apart on purpose: a
# by-product has a buyer (granulated slag is sold into cement), a waste stream
# does not yet (captured CO2 has to be paid to take away), and a sector page
# that grouped them would be asserting a market that may not exist.
MATERIAL_TYPES = (
    "feedstock",
    "intermediate",
    "energy_carrier",
    "by_product",
    "waste_stream",
)

# How the money arrives. Capital allocation is a first-class object here rather
# than a field on a project, because the same decision often finances several
# projects, and a field on one of them cannot say so.
FUNDING_INSTRUMENTS = (
    "grant",
    "state_aid",
    "eib_financing",
    "ipcei",
    "auction_support",
    "equity",
    "project_finance",
    "guarantee",
)

# Where the money has got to. A press release announcing a grant, a Commission
# decision approving it, a signed agreement and a disbursement are four
# different facts, and a page that showed them as one would let an announcement
# read as money in the ground.
FUNDING_STATUSES = (
    "announced",
    "approved",
    "signed",
    "disbursed",
    "withdrawn",
)

# WHICH STATUSES A TOTAL MAY ADD UP. The vocabulary above records where the
# money has got to; these three groups record what that means for arithmetic,
# in one place, because a total that quietly spans them is the failure the
# vocabulary exists to prevent.
#
#   COMMITTED   a decision has been taken and the money is attached to a
#               project: approved, signed, disbursed. This is what a figure
#               labelled "awarded" may contain and nothing else.
#   ANNOUNCED   said out loud and not yet decided. Shown as its own figure,
#               never folded into the committed one.
#   EXCLUDED    withdrawn. Out of every total, shown as its own line, because a
#               withdrawal that vanishes silently reads as money that was never
#               promised.
#
# Every status is in exactly one group; the gate checks that, so adding a
# status to FUNDING_STATUSES without deciding what it means for a sum fails
# rather than defaulting into invisibility.
FUNDING_COMMITTED = ("approved", "signed", "disbursed")
FUNDING_ANNOUNCED = ("announced",)
FUNDING_EXCLUDED = ("withdrawn",)

CONFIDENCE = ("primary", "secondary", "estimate")

# Scope of a parameter value. `country:XX` and `plant:<id>` are checked by
# prefix rather than listed, because the tail is data.
SCOPE_LITERALS = ("eu", "global")
SCOPE_PREFIXES = ("country:", "plant:")

DEFAULT_STALE_AFTER_MONTHS = 12


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

# WHICH PRINTED FIGURES A CORRECTION MAY BE PINNED TO. Closed, because the
# whole value of a correction note is that it appears beside the figure it
# corrects: an entry naming a figure no surface renders is a correction nobody
# is told about, and a typo would produce exactly that in silence. Each entry is
# `<section>.<figure>` and names something a page actually prints.
CORRECTABLE_FIGURES = (
    "opportunity.money_in",
)


_FILES = {
    "technology": ("technologies.json", "technologies"),
    "bottleneck": ("bottlenecks.json", "bottlenecks"),
    "parameter": ("parameters.json", "parameters"),
    "project": ("projects.json", "projects"),
    "material": ("materials.json", "materials"),
    "funding": ("funding.json", "funding"),
    "ecosystem": ("ecosystems.json", "ecosystems"),
    "correction": ("corrections.json", "corrections"),
}


def load(kind: str) -> list[dict]:
    """Read one kind's file and return its rows. Raises if the file is absent:
    an empty layer is a state this project has never been in, and a silently
    empty list would make every downstream count read as zero rather than as
    broken."""
    filename, key = _FILES[kind]
    path = DATA / filename
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc[key]
    if not isinstance(rows, list):
        raise TypeError(f"{path}: '{key}' must be a list")
    return rows


def load_all() -> dict[str, list[dict]]:
    return {kind: load(kind) for kind in _FILES}


def index(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def mapped_sectors() -> list[str]:
    """The sectors that have a transition map, which is the set every builder
    on this layer runs over by default.

    A sector has a map when something names a constraint in it -- the same
    condition web/lib/transition.ts `hasMap` reads and the sector route
    branches on. It was a literal ["cement"] in four builders' argument
    parsers, which meant the second sector had to be remembered in four places
    and would be silently absent from --check in any one of them that was
    missed. Derived here so the third sector arrives by having data.
    """
    return sorted({b["sector"] for b in load("bottleneck")})


# The technology every capture route eventually leans on. Named once here rather
# than matched on the `ccs-` prefix in three places: the prefix is a naming
# habit, the dependency is the fact.
CO2_STORAGE_TECHNOLOGY = "co2-transport-storage"


def captures_co2(project: dict, technologies: dict[str, dict]) -> bool:
    """Whether this project puts a captured tonne on the road, and therefore owes
    an answer about where the tonne goes.

    Read off the dependency graph, not off the row: a project deploys a capture
    technology, and that technology declares it cannot run without CO2 transport
    and storage. A project that deploys transport and storage ITSELF is the far
    end of that chain and owes nothing -- it is the answer, not the question.
    """
    tech_ids = project.get("technology") or []
    if CO2_STORAGE_TECHNOLOGY in tech_ids and project.get("role") == "storage":
        return False
    for tid in tech_ids:
        row = technologies.get(tid) or {}
        if CO2_STORAGE_TECHNOLOGY in (row.get("dependency") or []):
            return True
    return False


def sectors() -> dict[str, dict]:
    """The sector spine, read from the same file build_graph.py and
    web/lib/data.ts read, so this layer cannot invent a sector."""
    doc = json.loads((ROOT / "data" / "sectors.json").read_text(encoding="utf-8"))
    return doc["sectors"]


def register_measure_ids() -> set[str]:
    """Every measure id in the register, as `<file>:<id>` -- the form the
    transition layer references a measure by, and the tail of the graph node id
    `measure:<file>:<id>`."""
    ids: set[str] = set()
    files = json.loads((ROOT / "sources" / "register_files.json").read_text(encoding="utf-8"))
    for slug in files["files"]:
        path = ROOT / "data" / f"{slug}.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            ids.add(f"{slug}:{row['id']}")
    return ids


def measure_labels() -> dict[str, dict]:
    """The {object, instrument} pair per register measure id."""
    doc = json.loads((DATA / "measure_labels.json").read_text(encoding="utf-8"))
    return doc["labels"]


def short_label(entry: dict) -> str:
    """The template. One line, one place, so twenty sectors read alike.

    Kept deliberately dumb: the judgement is in the two authored fields, and a
    template with a branch per measure would be the free labels this replaced.
    """
    obj = entry["object"].strip()
    instrument = entry.get("instrument")
    return obj if not instrument else f"{obj} {instrument.strip()}"


# The figures an authored key-measure sentence may ask for, and nothing else.
# Closed, because a sentence that could name any field would be a template over
# the whole money block and would break silently the day one of those fields
# changed shape. See the plain block in data/transition/measure_labels.json.
MEASURE_SLOTS = ("money_per_tonne", "money_annual", "money_awarded")

_SLOT_RE = re.compile(r"\{([a-z_]+)\}")


def slots_named(text: str) -> list[str]:
    """Every {slot} in an authored sentence, in the order it appears."""
    return _SLOT_RE.findall(text or "")


def money_slots(money: dict) -> dict[str, str]:
    """The slot values a measure's own money block can answer for.

    Only what is computable: a measure with no per-tonne figure has no
    `money_per_tonne`, and a sentence that asks for one fails rather than
    printing an empty string where a euro figure was promised.

    Rounding is by scale, not by taste, and the scale is not chosen here: a rate
    goes through nf.money_rate and a stock through nf.money_long, both of which
    read data/number_format.json. This function used to write its own euro
    strings, which is how the site came to render one total two ways.
    """
    out: dict[str, str] = {}
    if not money or not money.get("computable"):
        return out
    if money.get("per_tonne") is not None:
        out["money_per_tonne"] = nf.money_rate(money["per_tonne"])
    if money.get("annual_total"):
        out["money_annual"] = f"{nf.money_long(money['annual_total'])} a year"
    if money.get("value") and money.get("scale") == "eur_awarded":
        out["money_awarded"] = nf.money_long(money["value"])
    return out


# WHAT A SECTOR'S PRODUCT IS CALLED, per sector, and the reason this list is
# here rather than in the gate: it is the vocabulary that makes a plain block
# sector-specific, and both the resolver and the gate have to agree about it.
#
# A shared plain block may contain none of these words, because a shared block
# is rendered on every sector a measure reaches and a product word in one is a
# sentence about the wrong industry. A per-sector block may contain its own
# sector's words and no other's. Adding a sector to the platform means adding
# its nouns here, and a sector with no entry has no product vocabulary to
# violate -- which is correct for the instances that are not industries.
SECTOR_PRODUCT_WORDS = {
    "cement": ("clinker", "cement", "concrete", "kiln"),
    "steel": ("steel", "hot metal", "crude steel", "directly reduced iron", "DRI",
              "blast furnace", "scrap", "electric arc furnace", "EAF", "iron ore"),
    # Both spellings of the plural are listed because the check matches a word
    # plus an optional "s", and "batteries" is not "batterys".
    "batsol": ("battery", "batteries", "cell", "cathode", "anode", "gigafactory"),
}


def plain_block(entry: dict, sector: str) -> dict | None:
    """The plain block this measure renders IN THIS SECTOR, or None.

    The sector's own wording wins; the shared block is the fallback and exists
    only for measures whose wording names no product. None is a real answer and
    the gate fails on it -- see data/transition/measure_labels.json. Returning
    the shared block regardless would be the trap this split was made to close.
    """
    per_sector = (entry.get("plain_by_sector") or {}).get(sector)
    return per_sector or entry.get("plain") or None


def plain_measure(entry: dict, money: dict, sector: str) -> dict:
    """The authored title and the slot-filled sentence, for one measure.

    The words are reviewed and stored; the figures are computed on every build.
    An unfillable slot raises, because the alternative is a sentence that says
    a measure costs nothing when what happened is that a parameter went
    missing.
    """
    plain = plain_block(entry, sector)
    if plain is None:
        raise SystemExit(
            f"sector_map: this measure has a label but no plain block for {sector!r} — "
            f"a sector view listing it would print an empty title and an empty sentence. "
            f"Write plain_by_sector.{sector}, or a shared block if the wording names no "
            f"product; see data/transition/measure_labels.json"
        )
    title, sentence = plain.get("title", ""), plain.get("sentence", "")
    values = money_slots(money)
    for name in slots_named(sentence):
        if name not in MEASURE_SLOTS:
            raise SystemExit(
                f"sector_map: key-measure sentence names {{{name}}}, which is not one of "
                f"{list(MEASURE_SLOTS)} — see data/transition/measure_labels.json"
            )
        if name not in values:
            raise SystemExit(
                f"sector_map: key-measure sentence asks for {{{name}}} and this measure's "
                f"money block cannot answer for it — either the sentence is about a figure "
                f"the measure does not carry, or the figure has gone missing"
            )
    return {
        "title": title,
        "sentence": _SLOT_RE.sub(lambda m: values[m.group(1)], sentence),
    }
