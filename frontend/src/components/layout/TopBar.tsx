import { Moon, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAppStore } from "@/store/appStore";

export function TopBar() {
  const { apiKey, setApiKey, theme, toggleTheme } = useAppStore();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-6">
      <div className="text-sm text-muted-foreground">Signed in with API key (Bearer)</div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Label htmlFor="api-key" className="sr-only">
            API key
          </Label>
          <Input
            id="api-key"
            type="password"
            placeholder="rgs_…"
            className="w-64 font-mono text-xs"
            value={apiKey ?? ""}
            onChange={(e) => setApiKey(e.target.value || null)}
          />
        </div>
        <Button variant="outline" size="icon" type="button" onClick={() => toggleTheme()} aria-label="Toggle theme">
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  );
}
