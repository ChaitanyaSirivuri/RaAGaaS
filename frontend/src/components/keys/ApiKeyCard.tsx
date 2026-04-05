import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ApiKeyRow } from "@/lib/api";

export function ApiKeyCard({ k }: { k: ApiKeyRow }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="font-mono text-sm">{k.key_prefix}…</CardTitle>
      </CardHeader>
      <CardContent className="text-xs text-muted-foreground">
        <p>Scopes: {k.scopes.join(", ")}</p>
        <p className="mt-1">Created {new Date(k.created_at).toLocaleString()}</p>
      </CardContent>
    </Card>
  );
}
