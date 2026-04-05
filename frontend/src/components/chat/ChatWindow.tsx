import { useMutation } from "@tanstack/react-query";
import { Send } from "lucide-react";
import { useState } from "react";

import { MessageBubble } from "@/components/chat/MessageBubble";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { runChat } from "@/lib/api";

export function ChatWindow({ collectionId }: { collectionId: string }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [sources, setSources] = useState<{ filename?: string | null; excerpt: string }[]>([]);

  const mut = useMutation({
    mutationFn: async (text: string) => {
      const next = [...messages, { role: "user" as const, content: text }];
      setMessages(next);
      const res = await runChat(
        collectionId,
        next.map((m) => ({ role: m.role, content: m.content })),
        5,
      );
      return res;
    },
    onSuccess: (res) => {
      setMessages((m) => [...m, { role: "assistant", content: res.answer }]);
      setSources(res.sources ?? []);
    },
  });

  function send() {
    const t = input.trim();
    if (!t || mut.isPending) {
      return;
    }
    setInput("");
    mut.mutate(t);
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col rounded-md border bg-card">
      <ScrollArea className="flex-1 p-4">
        <div className="flex flex-col gap-3">
          {messages.length === 0 && (
            <p className="text-center text-sm text-muted-foreground">Ask a question about this collection.</p>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} role={m.role}>
              <div className="whitespace-pre-wrap">{m.content}</div>
            </MessageBubble>
          ))}
          {sources.length > 0 && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
            <div className="mt-4 rounded-md border bg-background p-3 text-xs">
              <div className="mb-2 font-medium text-muted-foreground">Sources</div>
              <ul className="space-y-2">
                {sources.map((s, i) => (
                  <li key={i}>
                    <span className="font-mono text-primary">{s.filename ?? "file"}</span>
                    <p className="text-muted-foreground">{s.excerpt}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="flex gap-2 border-t p-3">
        <Textarea
          rows={2}
          placeholder="Your question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
        />
        <Button type="button" className="self-end" onClick={() => send()} disabled={mut.isPending}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
