import Link from "next/link";
import type { DiagramEdge, DiagramNode, FindingDiagram as Diagram } from "@/lib/findings";

// The finding's diagram: 3-5 nodes (acts and sectors) in a vertical flow, with
// every edge label computed and verified by the gate — this component only
// lays out what data/findings/diagrams/<id>.json already says.
//
// The gate guarantees the shape this layout depends on: every node after the
// first connects to exactly one earlier node, so the diagram is a tree rooted
// at the first node and can be drawn as nested branches without a layout
// engine. The arrow on each branch keeps the edge's direction honest in a
// vertical layout: ↓ when the flow runs parent-to-child down the page, ↑ when
// the child acts on its parent (a supplier feeding the sector above it).

interface TreeNode {
  node: DiagramNode;
  edge: DiagramEdge | null; // the edge linking this node to its parent
  children: TreeNode[];
}

function buildTree(diagram: Diagram): TreeNode | null {
  const [root, ...rest] = diagram.nodes;
  if (!root) return null;
  const byId = new Map<string, TreeNode>();
  const rootTree: TreeNode = { node: root, edge: null, children: [] };
  byId.set(root.id, rootTree);
  for (const node of rest) {
    const edge = diagram.edges.find(
      (e) =>
        (e.from === node.id && byId.has(e.to)) || (e.to === node.id && byId.has(e.from))
    );
    if (!edge) return null; // gate-checked invariant; nothing honest to draw without it
    const parent = byId.get(edge.from === node.id ? edge.to : edge.from)!;
    const tree: TreeNode = { node, edge, children: [] };
    parent.children.push(tree);
    byId.set(node.id, tree);
  }
  return rootTree;
}

function NodeChip({ node }: { node: DiagramNode }) {
  return (
    <Link href={node.href} className={`diagram-node diagram-node-${node.kind}`}>
      {node.label}
    </Link>
  );
}

function Branch({ tree }: { tree: TreeNode }) {
  // Edge direction relative to the layout: the child sits below its parent, so
  // an edge running parent→child points down and child→parent points up.
  const down = tree.edge!.from !== tree.node.id;
  return (
    <div className="diagram-branch">
      <div className="diagram-edge">
        <span className="diagram-arrow" aria-hidden="true">
          {down ? "↓" : "↑"}
        </span>
        {tree.edge!.label}
      </div>
      <NodeChip node={tree.node} />
      {tree.children.map((c) => (
        <Branch key={c.node.id} tree={c} />
      ))}
    </div>
  );
}

// The caption is a prop because a record diagram is the same species drawn
// from different sources: a finding's edges can carry a figure from the
// input-output data, and a record's are counts from the act alone. A single
// hardcoded caption would overstate one or the other.
const DEFAULT_CAPTION =
  "Every figure on this diagram is computed from the register and the " +
  "input-output data, and checked before the page is built.";

export default function FindingDiagram({
  diagram,
  caption = DEFAULT_CAPTION,
}: {
  diagram: Diagram;
  caption?: string;
}) {
  const tree = buildTree(diagram);
  if (!tree) return null;
  return (
    <figure className="finding-diagram">
      <NodeChip node={tree.node} />
      {tree.children.map((c) => (
        <Branch key={c.node.id} tree={c} />
      ))}
      <figcaption className="diagram-caption">{caption}</figcaption>
    </figure>
  );
}
