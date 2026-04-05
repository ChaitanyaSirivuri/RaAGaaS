import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";

import { CollectionCard } from "@/components/dashboard/CollectionCard";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { createCollection, fetchCollections } from "@/lib/api";

export function Dashboard() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const q = useQuery({ queryKey: ["collections"], queryFn: fetchCollections });

  async function onCreate() {
    if (!name.trim()) {
      return;
    }
    await createCollection({ name: name.trim() });
    setName("");
    setOpen(false);
    await q.refetch();
  }

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Collections</h1>
          <p className="text-sm text-muted-foreground">Create a collection, upload documents, then query.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New collection
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New collection</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="cname">Name</Label>
                <Input id="cname" value={name} onChange={(e) => setName(e.target.value)} placeholder="Support docs" />
              </div>
              <Button className="w-full" onClick={() => void onCreate()}>
                Create
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      {q.isLoading && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      )}
      {q.data && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {q.data.map((c) => (
            <CollectionCard key={c.id} c={c} />
          ))}
        </div>
      )}
    </div>
  );
}
