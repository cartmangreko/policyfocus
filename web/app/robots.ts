import type { MetadataRoute } from "next";
import { INDEXABLE } from "@/lib/launch";

// Matches the X-Robots-Tag header in next.config.ts and the robots metadata in
// layout.tsx; all three read lib/launch.ts. See that file for the switch.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: INDEXABLE
      ? { userAgent: "*", allow: "/" }
      : { userAgent: "*", disallow: "/" },
  };
}
