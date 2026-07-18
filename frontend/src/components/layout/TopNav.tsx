import { useState } from "react";
import { Bell, Bookmark, Compass, Feather, Home, Menu, Search, Sparkles, UserCircle2, X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link, NavLink } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/app/providers/AuthProvider";
import { fetchUnreadNotifications } from "@/features/notifications/api/notificationApi";
import { useCurrentUser } from "@/hooks/useCurrentUser";

const baseLinks = [
  { to: "/dashboard", label: "Home", icon: Home },
  { to: "/explore", label: "Explore", icon: Compass },
  { to: "/search", label: "Search", icon: Search },
  { to: "/bookmarks", label: "Bookmarks", icon: Bookmark },
  { to: "/notifications", label: "Notifications", icon: Bell },
  { to: "/recommendations", label: "Recommendations", icon: Sparkles },
  { to: "/profile", label: "Profile", icon: UserCircle2 },
];

export function TopNav() {
  const { logout } = useAuth();
  const currentUser = useCurrentUser();
  const unread = useQuery({ queryKey: ["notifications", "unread"], queryFn: fetchUnreadNotifications });
  const unreadCount = unread.data?.count ?? 0;
  const [mobileOpen, setMobileOpen] = useState(false);
  const links = currentUser.data?.is_admin
    ? [...baseLinks, { to: "/admin", label: "Admin", icon: Sparkles }]
    : baseLinks;

  const closeMobile = () => setMobileOpen(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-black/10 bg-lore-ivory/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 md:px-8">
        <Link to="/" className="flex items-center gap-3 font-display text-2xl text-lore-charcoal">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-lore-ocean to-lore-indigo text-lore-ivory shadow-glow">L</span>
          Lore
        </Link>

        <div className="hidden items-center gap-1 lg:flex">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={closeMobile}
                className={({ isActive }) =>
                  `focus-ring rounded-full px-4 py-2 text-sm font-medium transition ${
                    isActive ? "bg-lore-charcoal text-lore-ivory shadow-glow" : "text-lore-charcoal hover:bg-lore-ocean/10"
                  }`
                }
              >
                <span className="inline-flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {item.label}
                  {item.to === "/notifications" && unreadCount > 0 ? (
                    <span className="animate-pulse-soft rounded-full bg-lore-gold px-2 py-0.5 text-[11px] font-bold text-lore-charcoal">
                      {unreadCount}
                    </span>
                  ) : null}
                </span>
              </NavLink>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          {currentUser.data ? (
            <Link to="/profile" className="hidden text-sm text-lore-slate transition hover:text-lore-charcoal lg:block">
              {currentUser.data.username}
            </Link>
          ) : null}
          <Link to="/create" className="hidden md:block">
            <Button>
              <Feather className="mr-2 h-4 w-4" />
              Share Wisdom
            </Button>
          </Link>
          <Button variant="ghost" className="hidden md:inline-flex" onClick={logout}>
            Sign out
          </Button>
          <Button
            type="button"
            variant="ghost"
            className="inline-flex lg:hidden"
            aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
            onClick={() => setMobileOpen((value) => !value)}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {mobileOpen ? (
        <div className="animate-fade-rise border-t border-black/10 bg-lore-ivory/95 px-4 py-4 lg:hidden">
          <div className="grid gap-2">
            {links.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={closeMobile}
                  className={({ isActive }) =>
                    `focus-ring inline-flex min-h-11 items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition ${
                      isActive ? "bg-lore-charcoal text-lore-ivory" : "bg-white/70 text-lore-charcoal"
                    }`
                  }
                >
                  <span className="inline-flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </span>
                  {item.to === "/notifications" && unreadCount > 0 ? (
                    <span className="animate-pulse-soft rounded-full bg-lore-gold px-2 py-0.5 text-[11px] font-bold text-lore-charcoal">
                      {unreadCount}
                    </span>
                  ) : null}
                </NavLink>
              );
            })}
            <div className="soft-divider my-1" />
            <Link to="/create" onClick={closeMobile}>
              <Button className="w-full">
                <Feather className="mr-2 h-4 w-4" />
                Share Wisdom
              </Button>
            </Link>
            <Button variant="ghost" className="w-full" onClick={logout}>
              Sign out
            </Button>
          </div>
        </div>
      ) : null}
    </nav>
  );
}
