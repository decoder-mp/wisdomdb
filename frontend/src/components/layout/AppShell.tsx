import { Outlet } from "react-router-dom";
import { TopNav } from "@/components/layout/TopNav";

export function AppShell() {
  return (
    <div className="min-h-screen bg-tide">
      <TopNav />
      <main className="mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-12">
        <Outlet />
      </main>
    </div>
  );
}
