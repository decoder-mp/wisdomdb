import { type ReactNode, Suspense, lazy } from "react";
import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { PublicShell } from "@/components/layout/PublicShell";
import { ProtectedRoute } from "@/app/routes/ProtectedRoute";

const LandingPage = lazy(() => import("@/pages/LandingPage").then((m) => ({ default: m.LandingPage })));
const DashboardPage = lazy(() => import("@/pages/DashboardPage").then((m) => ({ default: m.DashboardPage })));
const LoginPage = lazy(() => import("@/pages/LoginPage").then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import("@/pages/RegisterPage").then((m) => ({ default: m.RegisterPage })));
const ForgotPasswordPage = lazy(() => import("@/pages/ForgotPasswordPage").then((m) => ({ default: m.ForgotPasswordPage })));
const ResetPasswordPage = lazy(() => import("@/pages/ResetPasswordPage").then((m) => ({ default: m.ResetPasswordPage })));
const VerifyEmailPage = lazy(() => import("@/pages/VerifyEmailPage").then((m) => ({ default: m.VerifyEmailPage })));
const ExplorePage = lazy(() => import("@/features/lore/pages/ExplorePage").then((m) => ({ default: m.ExplorePage })));
const LoreDetailsPage = lazy(() => import("@/features/lore/pages/LoreDetailsPage").then((m) => ({ default: m.LoreDetailsPage })));
const CreateLorePage = lazy(() => import("@/features/lore/pages/CreateLorePage").then((m) => ({ default: m.CreateLorePage })));
const NotificationsPage = lazy(() => import("@/features/notifications/pages/NotificationsPage").then((m) => ({ default: m.NotificationsPage })));
const RecommendationsPage = lazy(() => import("@/features/recommendations/pages/RecommendationsPage").then((m) => ({ default: m.RecommendationsPage })));
const BookmarksPage = lazy(() => import("@/pages/BookmarksPage").then((m) => ({ default: m.BookmarksPage })));
const ProfilePage = lazy(() => import("@/pages/ProfilePage").then((m) => ({ default: m.ProfilePage })));
const SettingsPage = lazy(() => import("@/pages/SettingsPage").then((m) => ({ default: m.SettingsPage })));
const AiCenterPage = lazy(() => import("@/pages/AiCenterPage").then((m) => ({ default: m.AiCenterPage })));
const SearchPage = lazy(() => import("@/pages/SearchPage").then((m) => ({ default: m.SearchPage })));
const AdminPage = lazy(() => import("@/pages/AdminPage").then((m) => ({ default: m.AdminPage })));

function lazyView(node: ReactNode) {
  return (
    <Suspense fallback={<div className="surface-panel animate-fade-rise p-6">Loading...</div>}>
      {node}
    </Suspense>
  );
}

export const appRouter = createBrowserRouter([
  {
    element: <PublicShell />,
    children: [
      { path: "/", element: lazyView(<LandingPage />) },
      { path: "/login", element: lazyView(<LoginPage />) },
      { path: "/register", element: lazyView(<RegisterPage />) },
      { path: "/forgot-password", element: lazyView(<ForgotPasswordPage />) },
      { path: "/reset-password", element: lazyView(<ResetPasswordPage />) },
      { path: "/verify-email", element: lazyView(<VerifyEmailPage />) },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/dashboard", element: lazyView(<DashboardPage />) },
          { path: "/explore", element: lazyView(<ExplorePage />) },
          { path: "/lore/:loreId", element: lazyView(<LoreDetailsPage />) },
          { path: "/create", element: lazyView(<CreateLorePage />) },
          { path: "/bookmarks", element: lazyView(<BookmarksPage />) },
          { path: "/notifications", element: lazyView(<NotificationsPage />) },
          { path: "/recommendations", element: lazyView(<RecommendationsPage />) },
          { path: "/profile", element: lazyView(<ProfilePage />) },
          { path: "/settings", element: lazyView(<SettingsPage />) },
          { path: "/ai", element: lazyView(<AiCenterPage />) },
          { path: "/search", element: lazyView(<SearchPage />) },
          { path: "/admin", element: lazyView(<AdminPage />) },
        ],
      },
    ],
  },
]);
