import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function MessageBubble({
  role,
  children,
  className,
}: {
  role: "user" | "assistant";
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "max-w-[85%] rounded-md border px-4 py-2 text-sm",
        role === "user" ? "ml-auto border-primary/30 bg-primary/5" : "mr-auto bg-muted",
        className,
      )}
    >
      {children}
    </div>
  );
}
