import { create } from "zustand";
import type { Citation } from "@/types/citation";

interface ReferenceState {
  activeCitations: Citation[];
  highlightedId: string | null;
  isPanelOpen: boolean;
  setActiveCitations: (citations: Citation[]) => void;
  addCitation: (citation: Citation) => void;
  setHighlightedId: (id: string | null) => void;
  setPanelOpen: (open: boolean) => void;
  highlightAndScroll: (id: string) => void;
  clearCitations: () => void;
}

export const useReferenceStore = create<ReferenceState>((set) => ({
  activeCitations: [],
  highlightedId: null,
  isPanelOpen: false,

  setActiveCitations: (citations) => set({ activeCitations: citations }),

  addCitation: (citation) =>
    set((state) => ({
      activeCitations: [...state.activeCitations, citation],
    })),

  setHighlightedId: (id) => set({ highlightedId: id }),

  setPanelOpen: (open) => set({ isPanelOpen: open }),

  highlightAndScroll: (id) =>
    set({
      highlightedId: id,
      isPanelOpen: true,
    }),

  clearCitations: () =>
    set({ activeCitations: [], highlightedId: null }),
}));
