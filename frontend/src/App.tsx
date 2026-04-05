import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Route, Routes } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ApiKeysPage } from "@/pages/ApiKeys";
import { ChatPage } from "@/pages/Chat";
import { CollectionDetail } from "@/pages/CollectionDetail";
import { Dashboard } from "@/pages/Dashboard";
import { DbImportPage } from "@/pages/DbImport";

const qc = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <TooltipProvider>
        <div className="flex min-h-screen bg-background">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <TopBar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/collections/:id" element={<CollectionDetail />} />
                <Route path="/collections/:id/chat" element={<ChatPage />} />
                <Route path="/keys" element={<ApiKeysPage />} />
                <Route path="/db-import" element={<DbImportPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
