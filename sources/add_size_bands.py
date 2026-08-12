import json
from collections import Counter

with open('../data/omnibus.json', encoding='utf-8') as f:
    rows = json.load(f)

BANDS = {
    "A": "Under 500 employees",
    "B": "500 to 999 employees",
    "C": "1000+ employees, turnover up to EUR 450m",
    "D": "1000+ employees, turnover over EUR 450m",
}

# explicit per-row scope: "in" | "out" | "na" (na = addressee isn't a sized company, or a different test applies)
SCOPE = {
    "AUD-01": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission, not a company by size."),
    "RPT-01": dict(A="out", B="out", C="in", D="in"),
    "RPT-02": dict(A="out", B="out", C="in", D="in"),
    "RPT-03": dict(A="out", B="out", C="in", D="in", note="If you are under 1000 employees, this protects you as a value-chain counterparty rather than binding you directly."),
    "RPT-04": dict(A="na", B="na", C="na", D="na", note="A named-entity exemption (EFSF and specified SFDR financial products), not a size test."),
    "RPT-05": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission, not a company by size."),
    "RPT-06": dict(A="out", B="out", C="in", D="in"),
    "RPT-07": dict(A="out", B="out", C="in", D="in"),
    "RPT-08": dict(A="na", B="na", C="na", D="na", note="Binds statutory auditors and assurance providers, not the reporting company itself."),
    "RPT-09": dict(A="na", B="na", C="na", D="na", note="The threshold is the third-country parent's EU turnover, not your own employee count."),
    "RPT-10": dict(A="out", B="out", C="in", D="in", note="Applies specifically to credit institutions and insurance undertakings."),
    "TAX-01": dict(A="out", B="out", C="in", D="out", note="Needs both over 1000 employees and turnover at or below EUR 450m; above that turnover you remain on the full mandatory Article 8 route."),
    "TAX-02": dict(A="out", B="out", C="in", D="out"),
    "STD-01": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission; if you are under 1000 employees you may eventually use the resulting voluntary standard."),
    "DD-01": dict(A="out", B="out", C="out", D="in", note="CSDDD applies only above the higher, double threshold (over 1000 employees AND over EUR 450m turnover) — the 1000-employee-only band (C) is out."),
    "DD-02": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
    "DD-03": dict(A="out", B="out", C="out", D="in"),
    "DD-04": dict(A="out", B="out", C="out", D="in"),
    "DD-05": dict(A="out", B="out", C="out", D="in"),
    "DD-06": dict(A="out", B="out", C="out", D="in", note="If you are under 500 employees, this protects you as a direct business partner rather than binding you directly."),
    "DD-07": dict(A="out", B="out", C="out", D="in"),
    "DD-08": dict(A="out", B="out", C="out", D="in"),
    "DD-09": dict(A="out", B="out", C="out", D="in"),
    "DD-10": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission, not a company by size."),
    "DD-11": dict(A="out", B="out", C="out", D="in"),
    "PEN-00": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
    "PEN-01": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission, not a company by size."),
    "PEN-02": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
    "LIA-01": dict(A="out", B="out", C="out", D="in"),
    "LIA-02": dict(A="na", B="na", C="na", D="na", note="Binds Member States (courts applying national law), not a company by size."),
    "LIA-03": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
    "LIA-04": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
    "LIA-05": dict(A="out", B="out", C="out", D="in"),
    "GOV-01": dict(A="na", B="na", C="na", D="na", note="Binds the European Commission, not a company by size."),
    "GOV-02": dict(A="na", B="na", C="na", D="na", note="Binds Member States, not a company by size."),
}

assert set(SCOPE.keys()) == {r['id'] for r in rows}, set(SCOPE.keys()) ^ {r['id'] for r in rows}

for r in rows:
    s = SCOPE[r['id']]
    r['size_scope'] = {k: s[k] for k in ("A", "B", "C", "D")}
    if s.get('note'):
        r['size_scope_note'] = s['note']

with open('../data/omnibus.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
with open('../data/size_bands.json', 'w', encoding='utf-8') as f:
    json.dump(BANDS, f, ensure_ascii=False, indent=2)

print("Bands:", BANDS)
print("Per-band in-scope counts:")
for b in BANDS:
    print(" ", b, Counter(r['size_scope'][b] for r in rows))
