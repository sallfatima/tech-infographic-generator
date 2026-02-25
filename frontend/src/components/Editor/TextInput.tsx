/**
 * TextInput — Zone de saisie pour décrire l'infographie.
 *
 * L'utilisateur tape une description textuelle (ex: "How RAG works"),
 * clique "Générer", et le backend LLM génère InfographicData.
 */

import { useState } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";

/** Texte placeholder pour guider l'utilisateur. */
const PLACEHOLDER = `Décris ton infographie technique...

Exemples :
• "How Kubernetes scheduling works with pods, nodes, and the control plane"
• "RAG pipeline: document ingestion → chunking → embedding → vector DB → retrieval → LLM → response"
• "Compare fine-tuning vs RAG vs prompt engineering for LLM customization"`;

export default function TextInput() {
  const { inputText, setInputText, analyze, isLoading, error } =
    useDiagramState();
  const [localText, setLocalText] = useState(inputText);

  const handleSubmit = () => {
    const text = localText.trim();
    if (!text) return;
    setInputText(text);
    analyze(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter ou Cmd+Enter pour envoyer
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-blue-500" />
        <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
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
        className="flex-1 min-h-[200px] p-4 rounded-lg border border-slate-200
                   bg-white text-sm text-slate-800
                   placeholder:text-slate-400 resize-none
                   focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all"
      />

      {/* Bouton Générer */}
      <button
        onClick={handleSubmit}
        disabled={isLoading || !localText.trim()}
        className="flex items-center justify-center gap-2 px-6 py-3
                   bg-blue-600 text-white font-medium rounded-lg
                   hover:bg-blue-700 active:bg-blue-800
                   disabled:bg-slate-300 disabled:cursor-not-allowed
                   transition-colors cursor-pointer"
      >
        {isLoading ? (
          <>
            {/* Spinner */}
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
            Analyse en cours...
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
            Générer l&apos;infographie
          </>
        )}
      </button>

      {/* Raccourci clavier */}
      <p className="text-xs text-slate-400 text-center">
        Ctrl+Enter pour générer
      </p>

      {/* Erreur */}
      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
          <strong>Erreur :</strong> {error}
        </div>
      )}
    </div>
  );
}
