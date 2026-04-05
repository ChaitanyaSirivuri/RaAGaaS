import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "light" | "dark";

type AppState = {
  apiKey: string | null;
  setApiKey: (k: string | null) => void;
  tenant: string | null;
  setTenant: (t: string | null) => void;
  theme: Theme;
  toggleTheme: () => void;
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      apiKey: null,
      setApiKey: (k) => set({ apiKey: k }),
      tenant: null,
      setTenant: (t) => set({ tenant: t }),
      theme: "light",
      toggleTheme: () => {
        const next = get().theme === "light" ? "dark" : "light";
        document.documentElement.classList.toggle("dark", next === "dark");
        set({ theme: next });
      },
    }),
    {
      name: "ragaas-app",
      partialize: (s) => ({ apiKey: s.apiKey, tenant: s.tenant, theme: s.theme }),
      onRehydrateStorage: () => (state) => {
        if (state?.theme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      },
    },
  ),
);
