/**
 * PipelineProgress — Barre de progression du pipeline multi-agent Pro.
 *
 * Affiche 3 etapes : Research → Structure → Render
 * avec connecteurs animes entre chaque etape.
 * Visible seulement en mode Pro + quand le pipeline est actif.
 */

import { useDiagramState } from "../../hooks/useDiagramState";
import type { PipelineStatus } from "../../types/infographic";
import { Check, X, Loader2 } from "lucide-react";

interface StepDef {
  id: PipelineStatus;
  label: string;
  description: string;
  number: number;
}

const STEPS: StepDef[] = [
  {
    id: "researching",
    label: "Research",
    description: "Recherche de references",
    number: 1,
  },
  {
    id: "structuring",
    label: "Structure",
    description: "Analyse LLM du texte",
    number: 2,
  },
  {
    id: "rendering",
    label: "Render",
    description: "Rendu image PIL",
    number: 3,
  },
];

const STATUS_ORDER: PipelineStatus[] = [
  "idle",
  "researching",
  "structuring",
  "rendering",
  "completed",
  "failed",
];

function getStepState(
  stepId: PipelineStatus,
  currentStatus: PipelineStatus,
): "idle" | "active" | "completed" | "failed" {
  if (currentStatus === "failed") return "failed";
  if (currentStatus === "completed") return "completed";

  const stepIdx = STATUS_ORDER.indexOf(stepId);
  const currentIdx = STATUS_ORDER.indexOf(currentStatus);

  if (stepIdx < currentIdx) return "completed";
  if (stepIdx === currentIdx) return "active";
  return "idle";
}

export function PipelineProgress() {
  const pipelineStatus = useDiagramState((s) => s.pipelineStatus);
  const generateMode = useDiagramState((s) => s.generateMode);

  // Ne pas afficher si pas en mode Pro ou si idle
  if (generateMode !== "pro" || pipelineStatus === "idle") return null;

  return (
    <div className="flex items-center justify-center gap-1 px-4 py-3 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border-b border-gray-200 dark:border-gray-700">
      {STEPS.map((step, i) => {
        const state = getStepState(step.id, pipelineStatus);
        return (
          <div key={step.id} className="flex items-center">
            {/* Step circle + label */}
            <div className="flex flex-col items-center gap-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-300 ${
                  state === "completed"
                    ? "bg-green-500 border-green-500 text-white"
                    : state === "active"
                      ? "bg-purple-500 border-purple-500 text-white animate-pulse"
                      : state === "failed"
                        ? "bg-red-500 border-red-500 text-white"
                        : "bg-white border-gray-300 text-gray-400 dark:bg-gray-800 dark:border-gray-600"
                }`}
              >
                {state === "completed" ? (
                  <Check size={16} strokeWidth={3} />
                ) : state === "failed" ? (
                  <X size={16} strokeWidth={3} />
                ) : state === "active" ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  step.number
                )}
              </div>
              <span
                className={`text-[10px] font-medium whitespace-nowrap ${
                  state === "completed"
                    ? "text-green-600 dark:text-green-400"
                    : state === "active"
                      ? "text-purple-600 dark:text-purple-400"
                      : state === "failed"
                        ? "text-red-600 dark:text-red-400"
                        : "text-gray-400 dark:text-gray-500"
                }`}
              >
                {step.label}
              </span>
            </div>

            {/* Connector */}
            {i < STEPS.length - 1 && (
              <div className="w-12 mx-2 mb-4">
                <div
                  className={`h-0.5 w-full transition-all duration-500 ${
                    getStepState(STEPS[i + 1].id, pipelineStatus) !== "idle"
                      ? "bg-green-400"
                      : state === "active"
                        ? "bg-purple-300 animate-pulse"
                        : "bg-gray-200 dark:bg-gray-600"
                  }`}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
