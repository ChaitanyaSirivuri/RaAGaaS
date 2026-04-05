import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { fetchCollections, fetchDbSchema, fetchImportJob, registerDbSource, startDbImport } from "@/lib/api";

type Step = 0 | 1 | 2 | 3;

export function DbImportPage() {
  const [step, setStep] = useState<Step>(0);
  const [label, setLabel] = useState("Imported DB");
  const [uri, setUri] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [sourceId, setSourceId] = useState<string | null>(null);
  const [collectionId, setCollectionId] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);

  const colQ = useQuery({ queryKey: ["collections"], queryFn: fetchCollections });
  const schemaQ = useQuery({
    queryKey: ["db-schema", sourceId],
    queryFn: () => fetchDbSchema(sourceId!),
    enabled: !!sourceId && step >= 1,
  });

  const [selection, setSelection] = useState<
    Record<string, Record<string, { text: boolean; meta: boolean }>>
  >({});

  useEffect(() => {
    if (!schemaQ.data) {
      return;
    }
    const next: typeof selection = {};
    for (const t of schemaQ.data.tables) {
      next[t.name] = {};
      for (const c of t.columns) {
        next[t.name][c.name] = { text: false, meta: false };
      }
    }
    setSelection(next);
  }, [schemaQ.data]);

  const pollQ = useQuery({
    queryKey: ["import-job", sourceId, jobId],
    queryFn: () => fetchImportJob(sourceId!, jobId!),
    enabled: !!sourceId && !!jobId && step === 3,
    refetchInterval: 2000,
  });

  const progressVal = useMemo(() => {
    const st = pollQ.data?.status;
    if (st === "done") {
      return 100;
    }
    if (st === "running") {
      return 50;
    }
    return 10;
  }, [pollQ.data?.status]);

  async function connect() {
    const res = await registerDbSource(label, uri || undefined, file ?? undefined);
    setSourceId(res.id);
    setStep(1);
  }

  function buildSelections() {
    const out: {
      table: string;
      columns: { column: string; use_as_text: boolean; store_as_metadata: boolean }[];
    }[] = [];
    for (const [table, cols] of Object.entries(selection)) {
      const columns = Object.entries(cols)
        .filter(([, v]) => v.text || v.meta)
        .map(([name, v]) => ({
          column: name,
          use_as_text: v.text,
          store_as_metadata: v.meta,
        }));
      if (columns.length) {
        out.push({ table, columns });
      }
    }
    return out;
  }

  async function startJob() {
    if (!sourceId || !collectionId) {
      return;
    }
    const res = await startDbImport(sourceId, collectionId, buildSelections());
    setJobId(res.id);
    setStep(3);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Database import</h1>
        <p className="text-sm text-muted-foreground">Connect → Schema → Map → Monitor</p>
      </div>
      <div className="flex gap-2 text-xs text-muted-foreground">
        {["Connect", "Schema", "Map", "Monitor"].map((s, i) => (
          <span key={s} className={step === i ? "font-semibold text-primary" : ""}>
            {i + 1}. {s}
          </span>
        ))}
      </div>
      <Separator />

      {step === 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Connection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Label</Label>
              <Input value={label} onChange={(e) => setLabel(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>URI (postgresql+asyncpg://, mysql+aiomysql://, sqlite+aiosqlite://)</Label>
              <Input value={uri} onChange={(e) => setUri(e.target.value)} placeholder="optional if uploading file" />
            </div>
            <div className="space-y-2">
              <Label>SQLite file</Label>
              <Input type="file" accept=".db,.sqlite,.sqlite3" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </div>
            <Button onClick={() => void connect()}>Continue</Button>
          </CardContent>
        </Card>
      )}

      {step === 1 && schemaQ.data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Schema</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {schemaQ.data.tables.map((t) => (
              <div key={t.name} className="rounded-md border p-4">
                <div className="mb-2 font-medium">{t.name}</div>
                <div className="space-y-2">
                  {t.columns.map((c) => (
                    <div key={c.name} className="flex flex-wrap items-center gap-4 text-sm">
                      <span className="w-40 font-mono text-xs">{c.name}</span>
                      <span className="text-muted-foreground">{c.type}</span>
                      <label className="flex items-center gap-1">
                        <input
                          type="checkbox"
                          checked={selection[t.name]?.[c.name]?.text ?? false}
                          onChange={(e) =>
                            setSelection((s) => ({
                              ...s,
                              [t.name]: {
                                ...s[t.name],
                                [c.name]: { ...s[t.name][c.name], text: e.target.checked },
                              },
                            }))
                          }
                        />
                        vector text
                      </label>
                      <label className="flex items-center gap-1">
                        <input
                          type="checkbox"
                          checked={selection[t.name]?.[c.name]?.meta ?? false}
                          onChange={(e) =>
                            setSelection((s) => ({
                              ...s,
                              [t.name]: {
                                ...s[t.name],
                                [c.name]: { ...s[t.name][c.name], meta: e.target.checked },
                              },
                            }))
                          }
                        />
                        metadata
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <Button onClick={() => setStep(2)}>Next</Button>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Map to collection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select value={collectionId} onValueChange={setCollectionId}>
              <SelectTrigger>
                <SelectValue placeholder="Choose collection" />
              </SelectTrigger>
              <SelectContent>
                {colQ.data?.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button disabled={!collectionId} onClick={() => void startJob()}>
              Start import
            </Button>
          </CardContent>
        </Card>
      )}

      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Monitor</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={progressVal} />
            <p className="text-sm text-muted-foreground">
              Status: {pollQ.data?.status ?? "…"} · Rows processed: {pollQ.data?.rows_processed ?? 0}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
