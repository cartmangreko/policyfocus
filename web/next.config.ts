import type { NextConfig } from "next";
import { INDEXABLE } from "./lib/launch";

const nextConfig: NextConfig = {
  // Until the launch switch is set, every response carries noindex — including
  // the ones no page component renders (static assets, the RSC payloads). The
  // header is the authoritative signal; app/robots.ts and the robots metadata
  // in app/layout.tsx say the same thing from the same source.
  async headers() {
    if (INDEXABLE) return [];
    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
      },
    ];
  },
};

export default nextConfig;
