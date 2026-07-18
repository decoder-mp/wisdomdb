import { Outlet } from "react-router-dom";

export function PublicShell() {
  return (
    <div className="min-h-screen bg-tide">
      <Outlet />
    </div>
  );
}
