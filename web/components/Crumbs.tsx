import Link from "next/link";

// The breadcrumb trail — every page below the root gets one, and the trail is
// the URL hierarchy: a child sector's trail runs Home / Sectors / parent /
// child. The last crumb is the current page and does not link.
export interface Crumb {
  label: string;
  href?: string;
}

export default function Crumbs({ trail }: { trail: Crumb[] }) {
  return (
    <div className="crumbs">
      {trail.map((c, i) => (
        <span key={`${c.label}-${i}`} className="crumb-item">
          {i > 0 && (
            <span className="crumb-sep" aria-hidden="true">
              {" / "}
            </span>
          )}
          {c.href ? (
            <Link href={c.href} className="crumb-link">
              {c.label}
            </Link>
          ) : (
            <span className="crumb">{c.label}</span>
          )}
        </span>
      ))}
    </div>
  );
}
