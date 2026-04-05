import { useParams } from "react-router-dom";

import { ChatWindow } from "@/components/chat/ChatWindow";

export function ChatPage() {
  const { id } = useParams<{ id: string }>();
  if (!id) {
    return null;
  }
  return (
    <div className="p-8">
      <h1 className="mb-4 text-xl font-semibold">Chat</h1>
      <ChatWindow collectionId={id} />
    </div>
  );
}
