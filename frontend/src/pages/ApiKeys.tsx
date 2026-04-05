import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { ApiKeyCard } from "@/components/keys/ApiKeyCard";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createKey, listKeys } from "@/lib/api";
import { useAppStore } from "@/store/appStore";

export function ApiKeysPage() {
  const [raw, setRaw] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const setApiKey = useAppStore((s) => s.setApiKey);
  const q = useQuery({ queryKey: ["keys"], queryFn: listKeys });

  async function onCreate() {
    const res = await createKey(["query", "ingest", "admin"]);
    setRaw(res.key);
    setApiKey(res.key);
    setOpen(true);
    await q.refetch();
  }

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">API keys</h1>
          <p className="text-sm text-muted-foreground">The raw key is shown only once.</p>
        </div>
        <Button onClick={() => void onCreate()}>Create key</Button>
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save your API key</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label>Copy now — it will not be shown again.</Label>
            <Input readOnly className="font-mono text-xs" value={raw ?? ""} />
          </div>
        </DialogContent>
      </Dialog>
      <div className="grid gap-4 md:grid-cols-2">
        {q.data?.map((k) => (
          <ApiKeyCard key={k.id} k={k} />
        ))}
      </div>
    </div>
  );
}
