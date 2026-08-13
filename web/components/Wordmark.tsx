import Link from "next/link";
import Logomark from "./Logomark";

export default function Wordmark({ tone = "light" }: { tone?: "light" | "dark" }) {
  return (
    <Link href="/" className={`wordmark wordmark-${tone}`}>
      <Logomark tone={tone} />
      <span className="wordmark-text">
        <span className="wordmark-lo">Policy</span>
        <span className="wordmark-hi">Focus</span>
      </span>
    </Link>
  );
}
