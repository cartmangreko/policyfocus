import Link from "next/link";
import Mark from "./Mark";

// The lockup: the mark, then `eu|fabric` set as one word.
//
// THE SEAM IS THE ONLY ACCENT IN THE NAME. A single pipe between `eu` and
// `fabric`, set at regular weight in signal blue while the letters are bold
// ink — the one place the accent colour touches the wordmark, and the reason
// signal blue is confined everywhere else.
//
// Always lowercase, always one word. The four-bar logomark this replaced was
// built from the burden strip, which made the site's identity a picture of its
// oldest data component; the weave is an identity that does not depend on which
// panel happens to be on the page.
// `size` is the lockup at two settings, not two logos: `lg` in the chrome
// where the name is being stated, `sm` in the footer where it is being
// remembered. Anything else would be a third mark.
export default function Wordmark({
  tone = "light",
  size = "lg",
}: {
  tone?: "light" | "dark";
  size?: "lg" | "sm";
}) {
  return (
    <Link
      href="/"
      className={`wordmark wordmark-${tone}${size === "sm" ? " wordmark-sm" : ""}`}
      aria-label="eufabric, home"
    >
      <Mark size={size === "sm" ? 36 : 42} tone={tone === "dark" ? "paper" : "ink"} />
      <span className="wordmark-text" aria-hidden="true">
        eu<span className="wordmark-seam">|</span>fabric
      </span>
    </Link>
  );
}
