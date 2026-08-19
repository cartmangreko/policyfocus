import fs from "node:fs";
import path from "node:path";

// The masthead's "connections mapped" figure: the total edge count of the
// knowledge graph, read from the file build_graph.py wrote. Build-time only.
// The prebuild step runs `build_graph.py --check`, which rebuilds the graph
// from the register and fails the build if data/graph/ has gone stale — so
// this number is gate-checked before anything here reads it, and it moves
// automatically with every ingestion.
const GRAPH_DIR = path.join(process.cwd(), "..", "data", "graph");

let cachedEdgeCount: number | null = null;

export function getConnectionCount(): number {
  if (cachedEdgeCount !== null) return cachedEdgeCount;
  const edges = JSON.parse(
    fs.readFileSync(path.join(GRAPH_DIR, "edges.json"), "utf-8")
  ) as unknown[];
  cachedEdgeCount = edges.length;
  return cachedEdgeCount;
}
