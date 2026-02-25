/**
 * GenerateOptions — Selecteurs type/format/taille + mode toggle.
 *
 * Affiche les options de generation sous le textarea :
 * - Mode : Standard / Pro (multi-agent)
 * - Type : Auto-detect + 10 types d'infographie
 * - Format : PNG / GIF
 * - Taille : 4 presets
 */

import { useDiagramState } from "../../hooks/useDiagramState";
import { InfographicType } from "../../types/infographic";
import type { OutputFormat, OutputSize } from "../../types/infographic";

const TYPE_OPTIONS: Array<{ value: string | "auto"; label: string }> = [
  { value: "auto", label: "Auto-detect" },
  { value: InfographicType.ARCHITECTURE, label: "Architecture" },
  { value: InfographicType.FLOWCHART, label: "Flowchart" },
  { value: InfographicType.COMPARISON, label: "Comparison" },
  { value: InfographicType.PROCESS, label: "Process" },
  { value: InfographicType.CONCEPT_MAP, label: "Concept Map" },
  { value: InfographicType.PIPELINE, label: "Pipeline" },
  { value: InfographicType.TIMELINE, label: "Timeline" },
  { value: InfographicType.MULTI_AGENT, label: "Multi-Agent" },
  { value: InfographicType.RAG_PIPELINE, label: "RAG Pipeline" },
  { value: InfographicType.INFOGRAPHIC, label: "Infographic" },
];

const SIZE_OPTIONS: Array<{ value: OutputSize; label: string }> = [
  { value: "1400x900", label: "1400 x 900 (Landscape)" },
  { value: "1200x800", label: "1200 x 800 (Medium)" },
  { value: "1080x1080", label: "1080 x 1080 (Square)" },
  { value: "1080x1920", label: "1080 x 1920 (Portrait)" },
];

export function GenerateOptions() {
  const generateMode = useDiagramState((s) => s.generateMode);
  const infographicType = useDiagramState((s) => s.infographicType);
  const outputFormat = useDiagramState((s) => s.outputFormat);
  const outputSize = useDiagramState((s) => s.outputSize);
  const setGenerateMode = useDiagramState((s) => s.setGenerateMode);
  const setInfographicType = useDiagramState((s) => s.setInfographicType);
  const setOutputFormat = useDiagramState((s) => s.setOutputFormat);
  const setOutputSize = useDiagramState((s) => s.setOutputSize);

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-800">
      {/* Mode toggle */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400 w-12">
          Mode
        </span>
        <div className="flex rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden">
          <button
            type="button"
            onClick={() => setGenerateMode("standard")}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${
              generateMode === "standard"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300"
            }`}
          >
            Standard
          </button>
          <button
            type="button"
            onClick={() => setGenerateMode("pro")}
            className={`px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1 ${
              generateMode === "pro"
                ? "bg-purple-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300"
            }`}
          >
            Pro <span className="text-yellow-400">&#9733;</span>
          </button>
        </div>
        {generateMode === "pro" && (
          <span className="text-[10px] text-purple-500 dark:text-purple-400">
            3 Agents Pipeline
          </span>
        )}
      </div>

      {/* Selectors row */}
      <div className="grid grid-cols-3 gap-2">
        {/* Type */}
        <div>
          <label className="block text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">
            Type
          </label>
          <select
            value={infographicType ?? "auto"}
            onChange={(e) =>
              setInfographicType(e.target.value === "auto" ? null : e.target.value)
            }
            className="w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Format */}
        <div>
          <label className="block text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">
            Format
          </label>
          <select
            value={outputFormat}
            onChange={(e) => setOutputFormat(e.target.value as OutputFormat)}
            className="w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
          >
            <option value="png">PNG</option>
            <option value="gif">GIF</option>
          </select>
        </div>

        {/* Size */}
        <div>
          <label className="block text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">
            Taille
          </label>
          <select
            value={outputSize}
            onChange={(e) => setOutputSize(e.target.value as OutputSize)}
            className="w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
          >
            {SIZE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
