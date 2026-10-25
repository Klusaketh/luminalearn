"use client";

import { useId, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { CodeBlock } from "@/components/tutor/CodeBlock";

type Shape = "rect" | "round" | "diamond" | "circle";

interface FlowNode {
  id: string;
  label: string;
  shape: Shape;
}

interface FlowEdge {
  from: string;
  to: string;
  label?: string;
  dashed: boolean;
}

interface ParsedFlow {
  horizontal: boolean;
  nodes: FlowNode[];
  edges: FlowEdge[];
}

const NODE_REF = /^\s*([A-Za-z_][\w-]*)\s*(\(\([^)]*\)\)|\(\[[^\]]*\]\)|\[\[[^\]]*\]\]|\[\([^)]*\)\]|\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|>[^\]]*\])?/;
const LINK = /^\s*(?:--\s*([^-|>][^|>]*?)\s*-->|(-{2,}>|={2,}>|-\.+->|-{3,}|={3,})(?:\|([^|]*)\|)?)\s*/;

function cleanLabel(raw: string): string {
  return raw.replace(/<br\s*\/?>/gi, " ").replace(/^["'`]+|["'`]+$/g, "").trim();
}

function shapeOf(token: string): { label: string; shape: Shape } {
  if (token.startsWith("((")) return { label: cleanLabel(token.slice(2, -2)), shape: "circle" };
  if (token.startsWith("([") || token.startsWith("(")) return { label: cleanLabel(token.replace(/^\(\[?|\]?\)$/g, "")), shape: "round" };
  if (token.startsWith("{")) return { label: cleanLabel(token.slice(1, -1)), shape: "diamond" };
  if (token.startsWith("[[") || token.startsWith("[(")) return { label: cleanLabel(token.slice(2, -2)), shape: "rect" };
  if (token.startsWith(">")) return { label: cleanLabel(token.slice(1, -1)), shape: "rect" };
  return { label: cleanLabel(token.slice(1, -1)), shape: "rect" };
}

/** Parses the Mermaid flowchart subset the Concept Explainer is instructed to produce. */
export function parseFlowchart(source: string): ParsedFlow | null {
  const lines = source.split(/\n|;/).map((l) => l.trim()).filter((l) => l && !l.startsWith("%%"));
  if (lines.length === 0) return null;
  let horizontal = false;
  const header = /^(flowchart|graph)\s*(TD|TB|BT|LR|RL)?\s*$/i.exec(lines[0]);
  if (header) {
    horizontal = /LR|RL/i.test(header[2] ?? "");
    lines.shift();
  }
  const nodes = new Map<string, FlowNode>();
  const edges: FlowEdge[] = [];
  const touch = (id: string, token?: string) => {
    const existing = nodes.get(id);
    if (token) {
      const { label, shape } = shapeOf(token);
      nodes.set(id, { id, label: label || id, shape });
    } else if (!existing) {
      nodes.set(id, { id, label: id, shape: "rect" });
    }
  };

  for (const line of lines) {
    if (/^(style|classDef|class|click|linkStyle|subgraph|end|direction)\b/i.test(line)) continue;
    let rest = line;
    const first = NODE_REF.exec(rest);
    if (!first) return null;
    touch(first[1], first[2]);
    let previous = first[1];
    rest = rest.slice(first[0].length);
    while (rest.trim()) {
      const link = LINK.exec(rest);
      if (!link) return null;
      rest = rest.slice(link[0].length);
      const target = NODE_REF.exec(rest);
      if (!target) return null;
      touch(target[1], target[2]);
      const label = cleanLabel(link[1] ?? link[3] ?? "");
      edges.push({ from: previous, to: target[1], label: label || undefined, dashed: (link[2] ?? "").includes(".") });
      previous = target[1];
      rest = rest.slice(target[0].length);
    }
  }
  if (nodes.size === 0 || nodes.size > 24) return null;
  return { horizontal, nodes: [...nodes.values()], edges };
}

interface PlacedNode extends FlowNode {
  x: number;
  y: number;
  w: number;
  h: number;
  layer: number;
  lines: string[];
}

function wrap(label: string, width = 20): string[] {
  const words = label.split(/\s+/);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if ((current + " " + word).trim().length > width && current) {
      lines.push(current);
      current = word;
    } else {
      current = `${current} ${word}`.trim();
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 3);
}

function layout(flow: ParsedFlow) {
  const ids = flow.nodes.map((n) => n.id);
  const out = new Map(ids.map((id) => [id, [] as string[]]));
  flow.edges.forEach((e) => out.get(e.from)?.push(e.to));

  // Break cycles: edges pointing back to a node on the DFS stack are drawn as back edges.
  const back = new Set<string>();
  const state = new Map<string, number>();
  const visit = (id: string) => {
    state.set(id, 1);
    for (const next of out.get(id) ?? []) {
      if (state.get(next) === 1) back.add(`${id}->${next}`);
      else if (!state.get(next)) visit(next);
    }
    state.set(id, 2);
  };
  ids.forEach((id) => !state.get(id) && visit(id));
  const forward = flow.edges.filter((e) => !back.has(`${e.from}->${e.to}`));

  // Longest-path layering over forward edges (Kahn order).
  const indegree = new Map(ids.map((id) => [id, 0]));
  forward.forEach((e) => indegree.set(e.to, (indegree.get(e.to) ?? 0) + 1));
  const layer = new Map(ids.map((id) => [id, 0]));
  const queue = ids.filter((id) => indegree.get(id) === 0);
  while (queue.length) {
    const id = queue.shift() as string;
    for (const e of forward.filter((f) => f.from === id)) {
      layer.set(e.to, Math.max(layer.get(e.to) ?? 0, (layer.get(id) ?? 0) + 1));
      indegree.set(e.to, (indegree.get(e.to) ?? 1) - 1);
      if (indegree.get(e.to) === 0) queue.push(e.to);
    }
  }

  const layers: string[][] = [];
  ids.forEach((id) => {
    const l = layer.get(id) ?? 0;
    (layers[l] ||= []).push(id);
  });
  // Barycenter ordering: two sweeps reduce crossings.
  for (let sweep = 0; sweep < 2; sweep += 1) {
    for (let l = 1; l < layers.length; l += 1) {
      const position = new Map((layers[l - 1] ?? []).map((id, i) => [id, i]));
      const score = (id: string) => {
        const parents = forward.filter((e) => e.to === id && position.has(e.from)).map((e) => position.get(e.from) as number);
        return parents.length ? parents.reduce((a, b) => a + b, 0) / parents.length : Number.MAX_SAFE_INTEGER;
      };
      layers[l] = [...(layers[l] ?? [])].sort((a, b) => score(a) - score(b));
    }
  }

  const byId = new Map(flow.nodes.map((n) => [n.id, n]));
  const placed = new Map<string, PlacedNode>();
  const gapMain = flow.horizontal ? 70 : 64;
  const gapCross = 26;
  const sized = layers.map((ids) =>
    ids.map((id) => {
      const node = byId.get(id) as FlowNode;
      const lines = wrap(node.label);
      const w = Math.min(220, Math.max(104, Math.max(...lines.map((l) => l.length)) * 7.3 + 34));
      const h = 24 + lines.length * 17;
      return { node, lines, w, h };
    })
  );
  const crossSize = (row: typeof sized[number]) => row.reduce((acc, n) => acc + (flow.horizontal ? n.h : n.w), 0) + gapCross * Math.max(0, row.length - 1);
  const maxCross = Math.max(...sized.map(crossSize));
  let main = 16;
  sized.forEach((row, l) => {
    let cross = (maxCross - crossSize(row)) / 2 + 16;
    const depth = Math.max(...row.map((n) => (flow.horizontal ? n.w : n.h)));
    row.forEach(({ node, lines, w, h }) => {
      const x = flow.horizontal ? main + (depth - w) / 2 : cross;
      const y = flow.horizontal ? cross : main + (depth - h) / 2;
      placed.set(node.id, { ...node, x, y, w, h, layer: l, lines });
      cross += (flow.horizontal ? h : w) + gapCross;
    });
    main += depth + gapMain;
  });
  const width = flow.horizontal ? main - gapMain + 16 : maxCross + 32;
  const height = flow.horizontal ? maxCross + 32 : main - gapMain + 16;
  return { placed, back, width, height };
}

const LAYER_COLORS = ["#8B5CF6", "#7C6CF0", "#5B8DEF", "#22B8D6", "#2BC4C4", "#F59E0B"];

export function FlowDiagram({ source }: { source: string }) {
  const flow = useMemo(() => parseFlowchart(source), [source]);
  const graph = useMemo(() => (flow ? layout(flow) : null), [flow]);
  const [focus, setFocus] = useState<string | null>(null);
  const markerId = `flow-${useId().replace(/:/g, "")}`;

  if (!flow || !graph) return <CodeBlock code={source} language="mermaid" />;
  const { placed, back, width, height } = graph;
  const related = (id: string) => !focus || id === focus || flow.edges.some((e) => (e.from === focus && e.to === id) || (e.to === focus && e.from === id));
  const description = flow.edges.map((e) => `${placed.get(e.from)?.label} ${e.label ? `(${e.label}) ` : ""}leads to ${placed.get(e.to)?.label}`).join(". ");

  return (
    <figure className="my-3 overflow-x-auto rounded-2xl border border-white/[0.08] bg-[radial-gradient(ellipse_at_top,rgba(139,92,246,0.08),transparent_70%)] p-2">
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" style={{ maxWidth: width, minWidth: Math.min(width, 320) }} className="mx-auto block" role="img" aria-labelledby={`${markerId}-t ${markerId}-d`}>
        <title id={`${markerId}-t`}>Concept flow diagram</title>
        <desc id={`${markerId}-d`}>{description || flow.nodes.map((n) => n.label).join(", ")}</desc>
        <defs>
          <marker id={markerId} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#A9AFCA" />
          </marker>
        </defs>
        {flow.edges.map((edge, index) => {
          const a = placed.get(edge.from);
          const b = placed.get(edge.to);
          if (!a || !b) return null;
          const isBack = back.has(`${edge.from}->${edge.to}`) || edge.from === edge.to;
          let d: string;
          let lx: number;
          let ly: number;
          if (flow.horizontal) {
            const x1 = a.x + a.w, y1 = a.y + a.h / 2, x2 = b.x, y2 = b.y + b.h / 2;
            d = isBack
              ? `M ${a.x + a.w / 2} ${a.y + a.h} C ${a.x + a.w / 2} ${a.y + a.h + 46}, ${b.x + b.w / 2} ${b.y + b.h + 46}, ${b.x + b.w / 2} ${b.y + b.h}`
              : `M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}`;
            lx = isBack ? (a.x + b.x + b.w) / 2 : (x1 + x2) / 2;
            ly = isBack ? Math.max(a.y + a.h, b.y + b.h) + 34 : (y1 + y2) / 2;
          } else {
            const x1 = a.x + a.w / 2, y1 = a.y + a.h, x2 = b.x + b.w / 2, y2 = b.y;
            d = isBack
              ? `M ${a.x + a.w} ${a.y + a.h / 2} C ${a.x + a.w + 56} ${a.y + a.h / 2}, ${b.x + b.w + 56} ${b.y + b.h / 2}, ${b.x + b.w} ${b.y + b.h / 2}`
              : `M ${x1} ${y1} C ${x1} ${(y1 + y2) / 2}, ${x2} ${(y1 + y2) / 2}, ${x2} ${y2}`;
            lx = isBack ? Math.max(a.x + a.w, b.x + b.w) + 40 : (x1 + x2) / 2;
            ly = isBack ? (a.y + b.y + b.h) / 2 : (y1 + y2) / 2;
          }
          const lit = !focus || edge.from === focus || edge.to === focus;
          return (
            <g key={`${edge.from}-${edge.to}-${index}`} style={{ opacity: lit ? 1 : 0.18, transition: "opacity 200ms" }}>
              <motion.path
                d={d}
                fill="none"
                stroke={lit && focus ? "#C4B5FD" : "#5D6384"}
                strokeWidth={1.6}
                strokeDasharray={edge.dashed ? "5 5" : undefined}
                markerEnd={`url(#${markerId})`}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.15 + Math.min(a.layer, 6) * 0.12, ease: "easeOut" }}
              />
              {edge.label && (
                <g>
                  <rect x={lx - edge.label.length * 3.4 - 8} y={ly - 10} width={edge.label.length * 6.8 + 16} height={20} rx={10} fill="#0B0C15" stroke="rgba(255,255,255,0.1)" />
                  <text x={lx} y={ly + 4} textAnchor="middle" fontSize={11} fill="#C2C7DC">
                    {edge.label}
                  </text>
                </g>
              )}
            </g>
          );
        })}
        {[...placed.values()].map((node) => {
          const color = LAYER_COLORS[Math.min(node.layer, LAYER_COLORS.length - 1)];
          const lit = related(node.id);
          const cx = node.x + node.w / 2;
          const cy = node.y + node.h / 2;
          return (
            <motion.g
              key={node.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: lit ? 1 : 0.25, y: 0 }}
              transition={{ duration: 0.45, delay: Math.min(node.layer, 6) * 0.12 }}
              onMouseEnter={() => setFocus(node.id)}
              onMouseLeave={() => setFocus(null)}
              style={{ cursor: "default" }}
            >
              {node.shape === "diamond" ? (
                <polygon
                  points={`${cx},${node.y - 6} ${node.x + node.w + 8},${cy} ${cx},${node.y + node.h + 6} ${node.x - 8},${cy}`}
                  fill={`${color}22`}
                  stroke={color}
                  strokeWidth={1.4}
                />
              ) : (
                <rect
                  x={node.x}
                  y={node.y}
                  width={node.w}
                  height={node.h}
                  rx={node.shape === "circle" ? node.h / 2 : node.shape === "round" ? 16 : 11}
                  fill={`${color}1f`}
                  stroke={color}
                  strokeOpacity={0.85}
                  strokeWidth={1.3}
                />
              )}
              <text x={cx} y={cy - ((node.lines.length - 1) * 17) / 2 + 4.5} textAnchor="middle" fontSize={12.5} fontWeight={600} fill="#F5F3FF">
                {node.lines.map((line, i) => (
                  <tspan key={i} x={cx} dy={i === 0 ? 0 : 17}>
                    {line}
                  </tspan>
                ))}
              </text>
            </motion.g>
          );
        })}
      </svg>
    </figure>
  );
}
