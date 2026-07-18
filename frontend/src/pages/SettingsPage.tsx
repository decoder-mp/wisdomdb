import { useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { changePassword } from "@/features/auth/api/authApi";
import { fetchBookmarks } from "@/features/bookmarks/api/bookmarkApi";
import { fetchUnreadNotifications } from "@/features/notifications/api/notificationApi";
import { fetchRecommendations } from "@/features/recommendations/api/recommendationApi";
import { useAuth } from "@/app/providers/AuthProvider";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { getApiErrorMessage } from "@/lib/apiError";
import { formatDate } from "@/lib/utils";

const passwordSchema = z
  .object({
    currentPassword: z.string().min(8),
    newPassword: z.string().min(8),
    confirmPassword: z.string().min(8),
  })
  .refine((value) => value.newPassword === value.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

type PasswordFormValues = z.infer<typeof passwordSchema>;

export function SettingsPage() {
  const { token, logout } = useAuth();
  const currentUser = useCurrentUser();
  const bookmarks = useQuery({ queryKey: ["bookmarks"], queryFn: fetchBookmarks });
  const unread = useQuery({ queryKey: ["notifications", "unread"], queryFn: fetchUnreadNotifications });
  const recommendations = useQuery({ queryKey: ["recommendations"], queryFn: fetchRecommendations });
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PasswordFormValues>({ resolver: zodResolver(passwordSchema) });

  const sessionStartedAt = localStorage.getItem("lore_session_started_at");
  const tokenExpiry = useMemo(() => {
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split(".")[1] ?? "")) as { exp?: number };
      return payload.exp ? new Date(payload.exp * 1000).toISOString() : null;
    } catch {
      return null;
    }
  }, [token]);

  const endSession = () => {
    if (confirm("Sign out from this device now?")) {
      logout();
    }
  };

  const changePasswordMutation = useMutation({
    mutationFn: (payload: PasswordFormValues) =>
      changePassword({
        current_password: payload.currentPassword,
        new_password: payload.newPassword,
      }),
    onSuccess: () => reset(),
  });

  const changePasswordError = changePasswordMutation.error
    ? getApiErrorMessage(changePasswordMutation.error, "Unable to update password right now.")
    : null;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-4xl">Settings</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="font-display text-2xl">Account and Security</h2>
          <p className="mt-2 text-lore-slate">JWT sessions, protected routes, and automatic unauthorized redirect are active. Review your session and sign out anytime.</p>
          <div className="mt-4 space-y-2 text-sm text-lore-slate">
            <p>Signed in as {currentUser.data?.email ?? "..."}</p>
            <p>Role: {currentUser.data?.is_admin ? "Admin" : "Member"}</p>
            <p>Session started: {sessionStartedAt ? formatDate(sessionStartedAt) : "Unknown"}</p>
            <p>Token expires: {tokenExpiry ? formatDate(tokenExpiry) : "Unknown"}</p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button variant="outline" onClick={endSession}>End this session</Button>
            <Link to="/login">
              <Button variant="ghost">Open sign-in screen</Button>
            </Link>
          </div>
        </Card>
        <Card>
          <h2 className="font-display text-2xl">Notifications and Privacy</h2>
          <p className="mt-2 text-lore-slate">Your current activity snapshot is shown here so you can decide where to focus next.</p>
          <div className="mt-4 space-y-2 text-sm text-lore-slate">
            <p>{unread.data?.count ?? 0} unread notifications</p>
            <p>{recommendations.data?.count ?? 0} active recommendations</p>
            <p>{bookmarks.data?.length ?? 0} bookmarked stories</p>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link to="/notifications" className="text-sm font-semibold text-lore-terracotta">Manage notifications</Link>
            <Link to="/bookmarks" className="text-sm font-semibold text-lore-terracotta">Review bookmarks</Link>
            <Link to="/profile" className="text-sm font-semibold text-lore-terracotta">Edit profile details</Link>
          </div>
        </Card>
        <Card>
          <h2 className="font-display text-2xl">Change Password</h2>
          <p className="mt-2 text-lore-slate">Update your password without leaving your current session.</p>
          <form className="mt-4 space-y-3" noValidate onSubmit={handleSubmit((payload) => changePasswordMutation.mutate(payload))}>
            <div className="space-y-1">
              <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" type="password" placeholder="Current password" {...register("currentPassword")} />
              {errors.currentPassword ? <p className="text-sm text-lore-terracotta">{errors.currentPassword.message}</p> : null}
            </div>
            <div className="space-y-1">
              <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" type="password" placeholder="New password" {...register("newPassword")} />
              {errors.newPassword ? <p className="text-sm text-lore-terracotta">{errors.newPassword.message}</p> : null}
            </div>
            <div className="space-y-1">
              <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" type="password" placeholder="Confirm new password" {...register("confirmPassword")} />
              {errors.confirmPassword ? <p className="text-sm text-lore-terracotta">{errors.confirmPassword.message}</p> : null}
            </div>
            {changePasswordMutation.isSuccess ? <p className="text-sm text-lore-forest">Password updated successfully.</p> : null}
            {changePasswordError ? <p className="text-sm text-lore-terracotta">{changePasswordError}</p> : null}
            <Button type="submit">{changePasswordMutation.isPending ? "Updating password..." : "Update password"}</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
