import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Collection } from "@/lib/api";

export function CollectionCard({ c }: { c: Collection }) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{c.name}</CardTitle>
        <div className="flex flex-wrap gap-2 pt-2">
          <Badge variant="secondary">{c.chunk_strategy}</Badge>
          <Badge variant="outline">{c.embedding_model}</Badge>
        </div>
      </CardHeader>
      <CardContent className="mt-auto flex items-center justify-between pt-2">
        <p className="text-xs text-muted-foreground">
          {c.document_count != null ? `${c.document_count} documents` : "—"}
        </p>
        <Button asChild size="sm" variant="default">
          <Link to={`/collections/${c.id}`}>Open</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
