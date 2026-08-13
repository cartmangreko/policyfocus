// Four bars, bottom-aligned — the same shape as the burden strip and the
// ledger. `tone="dark"` is the variant that sits on the footer ground.
export default function Logomark({ tone = "light" }: { tone?: "light" | "dark" }) {
  return (
    <span className={`logomark logomark-${tone}`} aria-hidden="true">
      <i />
      <i />
      <i />
      <i />
    </span>
  );
}
