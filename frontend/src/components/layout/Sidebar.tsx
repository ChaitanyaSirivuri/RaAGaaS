import { Database, Home, KeyRound, MessageSquare } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/keys", label: "API Keys", icon: KeyRound },
  { to: "/db-import", label: "DB Import", icon: Database },
];

export function Sidebar() {
  return (
    <aside className="flex w-56 flex-col border-r bg-card">
      <div className="border-b px-6 py-5">
        <div className="text-sm font-semibold tracking-tight text-foreground">RaaGaaS</div>
        <p className="text-xs text-muted-foreground">RAG as a Service</p>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t p-3 text-xs text-muted-foreground">
        Chat opens from a collection detail page.
        <MessageSquare className="mb-1 mt-2 h-4 w-4 opacity-50" />
      </div>
    </aside>
  );
}
