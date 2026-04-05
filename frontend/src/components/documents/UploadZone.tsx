import { Upload } from "lucide-react";
import { useCallback, useRef, useState } from "react";

import { Button } from "@/components/ui/button";

export function UploadZone({
  onFile,
  disabled,
}: {
  onFile: (f: File) => void;
  disabled?: boolean;
}) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handle = useCallback(
    (files: FileList | null) => {
      if (!files?.length) {
        return;
      }
      onFile(files[0]);
    },
    [onFile],
  );

  return (
    <div
      className={`flex flex-col items-center justify-center rounded-md border border-dashed border-input bg-muted/30 px-6 py-10 text-center transition-colors ${
        drag ? "border-primary bg-primary/5" : ""
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        handle(e.dataTransfer.files);
      }}
    >
      <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
      <p className="text-sm text-muted-foreground">Drop a PDF, TXT, DOCX, MD, or CSV file</p>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        disabled={disabled}
        onChange={(e) => handle(e.target.files)}
      />
      <Button
        type="button"
        variant="secondary"
        size="sm"
        className="mt-4"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
      >
        Browse
      </Button>
    </div>
  );
}
