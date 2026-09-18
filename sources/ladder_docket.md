# The confirmation ladder across five sectors — brief 11

**The ladder was built for hydrogen and this is the pass that takes it to the other four.**
The rules are in `sources/scope.md`, "The confirmation ladder". This file records what had
to be decided to apply them outside the sector they were written in, and it is written in
the order the work was done: the freeze first, then the populations, then the reading.

`D-L1` … `D-L7` are in `sources/hydrogen_docket.md` and are corrections to the hydrogen
scorer. `D-B1` … `D-B19` are brief 12's, also there. This file starts at **D-A1**.

## Rulings of 19 September 2026, written before anything was scored

**D-A1. THE SIX RUNG TESTS ARE BYTE-IDENTICAL TO THE D-B1 FREEZE, AND THIS PASS ADDS
READINGS RATHER THAN TESTS.** D-B1 froze the rung tests at commit
`a9542fe28f93eac7f66a3050070af6db93684e7e` and recorded the SHA-256 of the whole
`## The confirmation ladder` section. That section has since gained subsections — brief
12's work and this one's — so its hash has moved, and a hash that is expected to move
proves nothing.

**So the freeze is re-anchored on the block that must not move.** `### The six rungs`, the
2,324 bytes that state the six tests, hashes to
`47b0859d80b3e44cb2711e9011cccce2e4832390b26817f073b8294530dccea9` both at `a9542fe` and at
HEAD. It is unchanged. `check_ladder.py` recomputes it on every build and fails on a
difference, so the freeze is now enforced rather than asserted — the same move #68 made
about the build-image rule, for the same reason: prose does not fail a build.

**WHAT A READING IS ALLOWED TO DO.** Rung 2 asks for a capacity "in any unit, recorded as
stated" and rung 6 for an input edge at `firmness: contract`. Neither sentence names a
sector, and both need one to be filled in from a battery row or a storage row. The readings
say **which unit a sector's owners use** and **which dependency is the one rung 6 is about**
— a cement works with a firm electricity contract and no capture technology provider must
not clear a rung that is about its capture plant. **A reading may not make a rung easier or
harder to clear.** Where one would, it is a proposed test and goes to
`sources/ladder_questions.json`.

**AND THE READINGS WERE WRITTEN BEFORE A SINGLE CELL WAS SCORED**, in the first commit of
this branch, for the reason D-B1 gives: an instrument tuned after its answer is visible is
not an instrument. The commit is named in the next entry.
