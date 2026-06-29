import { ArrowLeft, Download, Grid2X2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import type { Sheet } from "../buildSheetsData";
import {
  createMarkup,
  createMeasurement,
  deleteMarkup as apiDeleteMarkup,
  deleteMeasurement as apiDeleteMeasurement,
  listMarkups,
  listMeasurements,
  sheetImageUrl,
  updateMarkup,
  type Drawing,
  type Markup,
  type Measurement,
  type VectorUnits
} from "../api/drawings";
import CalibrationModal from "./viewer/CalibrationModal";
import CompareModal from "./viewer/CompareModal";
import CompareOverlay from "./viewer/CompareOverlay";
import IssueAddPanel from "./viewer/IssueAddPanel";
import MarkupCanvas from "./viewer/MarkupCanvas";
import MarkupListPanel from "./viewer/MarkupListPanel";
import MarkupPropertyPanel from "./viewer/MarkupPropertyPanel";
import MarkupToolRail from "./viewer/MarkupToolRail";
import MeasurePanel from "./viewer/MeasurePanel";
import VectorCanvas from "./viewer/VectorCanvas";
import {
  issueCategories,
  measureTypes,
  type MarkupTool,
  type MeasureType,
  type ViewerLeftTab
} from "./viewer/viewerData";

const leftTabs: ViewerLeftTab[] = ["마크업", "마크업 로그", "이슈"];
type Pt = [number, number];

export default function SheetViewerShell({
  projectName,
  selectedSheet,
  sheets,
  onBack
}: {
  projectName: string;
  selectedSheet: Sheet;
  sheets: Sheet[];
  onBack: () => void;
}) {
  const [activeTool, setActiveTool] = useState<MarkupTool>("선택");
  const [leftTab, setLeftTab] = useState<ViewerLeftTab>("마크업");
  const [selectedMarkupId, setSelectedMarkupId] = useState<string | null>(null);
  const [selectedIssueCategory, setSelectedIssueCategory] = useState<string | null>(null);
  const [measureOpen, setMeasureOpen] = useState(false);
  const [activeMeasureType, setActiveMeasureType] = useState<MeasureType>("선형");
  const [calibrationOpen, setCalibrationOpen] = useState(false);
  const [compareOpen, setCompareOpen] = useState(false);
  const [compareAgainst, setCompareAgainst] = useState<Drawing | null>(null);
  const [units, setUnits] = useState<VectorUnits | undefined>(undefined);

  const [markups, setMarkups] = useState<Markup[]>([]);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [opError, setOpError] = useState<string | null>(null);

  const fileId = selectedSheet.fileId;
  const sheetId = selectedSheet.id;
  const sheetIndex = selectedSheet.sheetIndex ?? 0;

  // S1.5: ②벡터(승자) ↔ ①래스터 토글. DWG/DXF만 벡터 가용.
  const vectorCapable = Boolean(fileId) && selectedSheet.source !== "pdf-page";
  const [renderEngine, setRenderEngine] = useState<"vector" | "raster">(vectorCapable ? "vector" : "raster");
  const showVector = vectorCapable && renderEngine === "vector";

  // 시트가 바뀌면 마크업/측정 로드(새로고침·재진입 복원 = E2/E6).
  useEffect(() => {
    setSelectedMarkupId(null);
    setMeasureOpen(false);
    setMarkups([]);
    setMeasurements([]);
    if (!fileId) return;
    let alive = true;
    Promise.all([listMarkups(fileId, sheetId), listMeasurements(fileId, sheetId)])
      .then(([m, ms]) => {
        if (!alive) return;
        setMarkups(m);
        setMeasurements(ms);
      })
      .catch(() => {/* 로드 실패는 빈 상태 유지 */});
    return () => {
      alive = false;
    };
  }, [fileId, sheetId]);

  // DXF=world, PDF/래스터=image 좌표계로 마크업을 분리해 해당 캔버스에만 렌더한다.
  const coordSpace: "world" | "image" = showVector ? "world" : "image";
  const visibleMarkups = markups.filter((m) => m.coord_space === coordSpace);
  const selectedMarkup = markups.find((m) => m.markup_id === selectedMarkupId) ?? null;
  const compareResultOpen = Boolean(compareAgainst);
  const hasAside = !compareResultOpen && (measureOpen || Boolean(selectedMarkup));

  const commitMarkup = useCallback(
    async (m: { kind: string; geometry: Pt[]; text?: string; color: string }) => {
      if (!fileId) return;
      try {
        const created = await createMarkup(fileId, {
          sheet_id: sheetId,
          kind: m.kind,
          coord_space: coordSpace,
          geometry: m.geometry,
          style: { color: m.color, width: 2 },
          text: m.text ?? ""
        });
        setMarkups((prev) => [...prev, created]);
        setOpError(null);
      } catch (e) {
        setOpError(e instanceof Error ? e.message : "마크업 저장 실패");
      }
    },
    [fileId, sheetId, coordSpace]
  );

  const commitMeasurement = useCallback(
    async (m: { type: MeasureType; geometry: Pt[]; value: number; unit: string }) => {
      if (!fileId) return;
      try {
        const created = await createMeasurement(fileId, {
          sheet_id: sheetId,
          type: m.type,
          geometry: m.geometry,
          value: m.value,
          unit: m.unit
        });
        setMeasurements((prev) => [...prev, created]);
        setOpError(null);
      } catch (e) {
        setOpError(e instanceof Error ? e.message : "측정 저장 실패");
      }
    },
    [fileId, sheetId]
  );

  async function removeMarkup(id: string) {
    if (!fileId) return;
    try {
      await apiDeleteMarkup(fileId, id);
      setMarkups((prev) => prev.filter((m) => m.markup_id !== id));
      setSelectedMarkupId(null);
    } catch (e) {
      setOpError(e instanceof Error ? e.message : "마크업 삭제 실패");
    }
  }

  async function changeMarkup(id: string, patch: { text?: string; style?: Markup["style"] }) {
    if (!fileId) return;
    try {
      const updated = await updateMarkup(fileId, id, patch);
      setMarkups((prev) => prev.map((m) => (m.markup_id === id ? updated : m)));
    } catch (e) {
      setOpError(e instanceof Error ? e.message : "마크업 수정 실패");
    }
  }

  async function removeMeasurement(id: string) {
    if (!fileId) return;
    try {
      await apiDeleteMeasurement(fileId, id);
      setMeasurements((prev) => prev.filter((m) => m.measurement_id !== id));
    } catch (e) {
      setOpError(e instanceof Error ? e.message : "측정 삭제 실패");
    }
  }

  function selectTool(tool: MarkupTool) {
    setActiveTool(tool);
    if (tool === "측정") {
      setSelectedMarkupId(null);
      setMeasureOpen(true);
    } else {
      setMeasureOpen(false);
      if (tool !== "선택") setSelectedMarkupId(null);
    }
  }

  function closeMeasure() {
    setMeasureOpen(false);
    setActiveTool("선택");
  }

  function selectMarkup(id: string | null) {
    setSelectedMarkupId(id);
    if (id) setMeasureOpen(false);
  }

  function startCompare(against: Drawing) {
    setSelectedMarkupId(null);
    setMeasureOpen(false);
    setActiveTool("선택");
    setCompareOpen(false);
    setCompareAgainst(against);
  }

  const compareBSheet = compareAgainst ? compareAgainst.sheets[sheetIndex] ?? compareAgainst.sheets[0] : null;

  return (
    <section className="viewer-shell" aria-label="2D 시트 뷰어">
      <header className="viewer-header">
        <button className="ghost-action" type="button" onClick={onBack}>
          <ArrowLeft size={16} aria-hidden="true" />
          시트 목록
        </button>
        <div>
          <h1>{selectedSheet.number}</h1>
          <p>{selectedSheet.title}</p>
          <span>{projectName}</span>
        </div>
        <div className="viewer-header-actions">
          {fileId ? (
            <button className="secondary-action" type="button" onClick={() => setCompareOpen(true)}>
              <Grid2X2 size={16} aria-hidden="true" />
              시트 비교
            </button>
          ) : null}
          <button className="secondary-action" type="button">
            <Download size={16} aria-hidden="true" />
            내보내기
          </button>
        </div>
      </header>

      {opError ? (
        <div className="viewer-op-error" role="alert">
          {opError}
        </div>
      ) : null}

      <div className={`viewer-grid${hasAside ? " has-aside" : ""}`}>
        <aside className="viewer-panel">
          <div className="viewer-panel-tabs" role="tablist" aria-label="뷰어 패널">
            {leftTabs.map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={leftTab === tab}
                onClick={() => setLeftTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
          {leftTab === "이슈" ? (
            <IssueAddPanel
              categories={issueCategories}
              selectedCategoryId={selectedIssueCategory}
              onSelectCategory={(id) => setSelectedIssueCategory((current) => (current === id ? null : id))}
            />
          ) : (
            <MarkupListPanel
              markups={visibleMarkups}
              selectedMarkupId={selectedMarkupId}
              isLog={leftTab === "마크업 로그"}
              onSelectMarkup={selectMarkup}
            />
          )}
        </aside>

        <div className="viewer-stage">
          {compareResultOpen && compareAgainst && fileId ? (
            <CompareOverlay
              aLabel={`v${selectedSheet.version}`}
              bLabel={`v${compareAgainst.version}`}
              aUrl={selectedSheet.imageUrl}
              bUrl={compareBSheet ? sheetImageUrl(compareBSheet) : undefined}
              fileId={fileId}
              againstId={compareAgainst.file_id}
              sheetIndex={sheetIndex}
              onClose={() => setCompareAgainst(null)}
            />
          ) : (
            <>
              {vectorCapable ? (
                <div className="render-engine-toggle" role="group" aria-label="렌더 엔진">
                  <button type="button" aria-pressed={renderEngine === "vector"} onClick={() => setRenderEngine("vector")}>
                    벡터
                  </button>
                  <button type="button" aria-pressed={renderEngine === "raster"} onClick={() => setRenderEngine("raster")}>
                    래스터
                  </button>
                </div>
              ) : null}
              {showVector ? (
                <VectorCanvas
                  fileId={fileId as string}
                  activeTool={activeTool}
                  markups={visibleMarkups}
                  measurements={measurements}
                  measureType={activeMeasureType}
                  selectedMarkupId={selectedMarkupId}
                  onSelectMarkup={selectMarkup}
                  onCommitMarkup={commitMarkup}
                  onCommitMeasurement={commitMeasurement}
                  onUnits={setUnits}
                />
              ) : (
                <MarkupCanvas
                  selectedSheet={selectedSheet}
                  markups={visibleMarkups}
                  activeTool={activeTool}
                  selectedMarkupId={selectedMarkupId}
                  onSelectMarkup={selectMarkup}
                  onCommitMarkup={commitMarkup}
                />
              )}
            </>
          )}
        </div>

        {hasAside &&
          (measureOpen ? (
            <MeasurePanel
              measureTypes={measureTypes}
              activeMeasureType={activeMeasureType}
              measurements={measurements}
              units={units}
              enabled={showVector}
              disabledReason={
                vectorCapable ? "래스터 엔진에서는 측정할 수 없습니다. 벡터로 전환하세요." : "측정은 DXF 벡터 시트 전용입니다(PDF 제외)."
              }
              onSelectMeasureType={setActiveMeasureType}
              onDeleteMeasurement={removeMeasurement}
              onCalibrate={() => setCalibrationOpen(true)}
              onClose={closeMeasure}
            />
          ) : selectedMarkup ? (
            <MarkupPropertyPanel
              markup={selectedMarkup}
              onClose={() => setSelectedMarkupId(null)}
              onChange={(patch) => changeMarkup(selectedMarkup.markup_id, patch)}
              onDelete={() => removeMarkup(selectedMarkup.markup_id)}
            />
          ) : null)}

        <MarkupToolRail activeTool={activeTool} onSelectTool={selectTool} />
      </div>

      <footer className="sheet-filmstrip" aria-label="필름스트립">
        <strong>필름스트립</strong>
        <div>
          {sheets.map((sheet) => (
            <button key={sheet.id} type="button" aria-current={sheet.id === selectedSheet.id ? "page" : undefined}>
              {sheet.number}
            </button>
          ))}
        </div>
      </footer>

      {calibrationOpen && (
        <CalibrationModal units={units} onClose={() => setCalibrationOpen(false)} onConfirm={() => setCalibrationOpen(false)} />
      )}
      {compareOpen && (
        <CompareModal currentSheet={selectedSheet} onClose={() => setCompareOpen(false)} onCompare={startCompare} />
      )}
    </section>
  );
}
