import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { DocumentRow } from "@/lib/api";

export function DocumentList({ docs }: { docs: DocumentRow[] }) {
  if (!docs.length) {
    return <p className="text-sm text-muted-foreground">No documents yet.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>File</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Chunks</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {docs.map((d) => (
          <TableRow key={d.id}>
            <TableCell className="font-medium">{d.filename}</TableCell>
            <TableCell>
              <Badge variant="outline">{d.status}</Badge>
            </TableCell>
            <TableCell>{d.chunk_count}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
