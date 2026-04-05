import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { DocumentList } from "@/components/documents/DocumentList";
import { UploadZone } from "@/components/documents/UploadZone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchCollection, fetchDocuments, uploadDocument } from "@/lib/api";

export function CollectionDetail() {
  const { id } = useParams<{ id: string }>();
  const cid = id ?? "";

  const colQ = useQuery({ queryKey: ["collection", cid], queryFn: () => fetchCollection(cid), enabled: !!cid });
  const docQ = useQuery({ queryKey: ["documents", cid], queryFn: () => fetchDocuments(cid), enabled: !!cid });

  async function onUpload(file: File) {
    await uploadDocument(cid, file);
    await docQ.refetch();
    await colQ.refetch();
  }

  if (!cid) {
    return null;
  }

  return (
    <div className="space-y-8 p-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          {colQ.isLoading ? (
            <Skeleton className="h-8 w-64" />
          ) : (
            <h1 className="text-2xl font-semibold tracking-tight">{colQ.data?.name}</h1>
          )}
          <p className="text-sm text-muted-foreground">
            Chunking: {colQ.data?.chunk_strategy} · {colQ.data?.chunk_size} tokens · overlap{" "}
            {colQ.data?.chunk_overlap}
          </p>
        </div>
        <Button asChild variant="default">
          <Link to={`/collections/${cid}/chat`}>Open chat</Link>
        </Button>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Upload</CardTitle>
          </CardHeader>
          <CardContent>
            <UploadZone onFile={(f) => void onUpload(f)} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {docQ.isLoading ? <Skeleton className="h-24" /> : <DocumentList docs={docQ.data ?? []} />}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
