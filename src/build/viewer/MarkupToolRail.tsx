import {
  Cloud,
  Eraser,
  Hexagon,
  MapPin,
  MousePointer2,
  Pencil,
  Ruler,
  Spline,
  Square,
  Type
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { MarkupTool } from "./viewerData";

const tools: { tool: MarkupTool; icon: LucideIcon }[] = [
  { tool: "선택", icon: MousePointer2 },
  { tool: "텍스트", icon: Type },
  { tool: "도형", icon: Square },
  { tool: "클라우드", icon: Cloud },
  { tool: "폴리라인", icon: Spline },
  { tool: "다각형", icon: Hexagon },
  { tool: "펜", icon: Pencil },
  { tool: "지우개", icon: Eraser },
  { tool: "이슈 핀", icon: MapPin },
  { tool: "측정", icon: Ruler }
];

export default function MarkupToolRail({
  activeTool,
  onSelectTool
}: {
  activeTool: MarkupTool;
  onSelectTool: (tool: MarkupTool) => void;
}) {
  return (
    <aside className="viewer-tool-rail" aria-label="마크업 도구">
      {tools.map(({ tool, icon: Icon }) => (
        <button
          key={tool}
          type="button"
          aria-label={tool}
          aria-pressed={activeTool === tool}
          onClick={() => onSelectTool(tool)}
        >
          <Icon size={18} aria-hidden="true" />
        </button>
      ))}
    </aside>
  );
}
