/**
 * TextInput — Zone de saisie + options de generation.
 *
 * Contient :
 * - Textarea pour la description
 * - GenerateOptions (mode, type, format, taille)
 * - Bouton "Generer l'infographie" (appelle generate())
 * - Bouton "Analyser seulement" (appelle analyze(), retourne JSON only)
 */

import { useState } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";
import { GenerateOptions } from "./GenerateOptions";

/** Texte placeholder pour guider l'utilisateur. */
const PLACEHOLDER = `Decris ton infographie technique...

Exemples :
\u2022 "How Kubernetes scheduling works with pods, nodes, and the control plane"
\u2022 "RAG pipeline: document ingestion \u2192 chunking \u2192 embedding \u2192 vector DB \u2192 retrieval \u2192 LLM \u2192 response"
\u2022 "Compare fine-tuning vs RAG vs prompt engineering for LLM customization"`;

export default function TextInput() {
  const {
    inputText,
    setInputText,
    analyze,
    generate,
    isLoading,
    error,
    generateMode,
  } = useDiagramState();
  const [localText, setLocalText] = useState(inputText);

  /** Generer = analyse LLM + rendu PIL image. */
  const handleGenerate = () => {
    const text = localText.trim();
    if (!text) return;
    setInputText(text);
    generate(text);
  };

  /** Analyser seulement = JSON preview sans rendu image. */
  const handleAnalyzeOnly = () => {
    const text = localText.trim();
    if (!text) return;
    setInputText(text);
    analyze(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter ou Cmd+Enter pour generer
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const buttonLabel =
    generateMode === "pro"
      ? "Generer Pro (3 Agents)"
      : "Generer l'infographie";

  const buttonColor =
    generateMode === "pro"
      ? "bg-purple-600 hover:bg-purple-700 active:bg-purple-800"
      : "bg-blue-600 hover:bg-blue-700 active:bg-blue-800";

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-blue-500" />
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200 uppercase tracking-wide">
          Description
        </h2>
      </div>

      {/* Textarea */}
      <textarea
        value={localText}
        onChange={(e) => setLocalText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={PLACEHOLDER}
        disabled={isLoading}
        className="flex-1 min-h-[160px] p-4 rounded-lg border border-slate-200
                   bg-white text-sm text-slate-800
                   placeholder:text-slate-400 resize-none
                   focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400
                   disabled:opacity-50 disabled:cursor-not-allowed
                   dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100
                   dark:placeholder:text-gray-500
                   transition-all"
      />

      {/* Options de generation */}
      <GenerateOptions />

      {/* Boutons */}
      <div className="flex gap-2">
        {/* Bouton principal : Generer */}
        <button
          onClick={handleGenerate}
          disabled={isLoading || !localText.trim()}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5
                     text-white font-medium rounded-lg text-sm
                     disabled:bg-slate-300 disabled:cursor-not-allowed
                     transition-colors cursor-pointer ${buttonColor}`}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="opacity-25"
                />
                <path
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  fill="currentColor"
                  className="opacity-75"
                />
              </svg>
              Generation en cours...
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {buttonLabel}
            </>
          )}
        </button>

        {/* Bouton secondaire : Analyser seulement */}
        <button
          onClick={handleAnalyzeOnly}
          disabled={isLoading || !localText.trim()}
          className="px-3 py-2.5 text-xs font-medium rounded-lg border
                     border-gray-300 text-gray-600
                     hover:bg-gray-100 active:bg-gray-200
                     disabled:opacity-50 disabled:cursor-not-allowed
                     dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700
                     transition-colors cursor-pointer"
          title="Analyse LLM sans rendu image (JSON seulement)"
        >
          Analyser
        </button>
      </div>

      {/* Raccourci clavier */}
      <p className="text-[10px] text-slate-400 dark:text-slate-500 text-center">
        Ctrl+Enter pour generer
      </p>

      {/* Erreur */}
      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
          <strong>Erreur :</strong> {error}
        </div>
      )}
    </div>
  );
}
