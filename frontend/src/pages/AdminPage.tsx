import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SectionHeading } from "@/components/ui/SectionHeading";
import {
  deleteAdminLore,
  deleteAdminUser,
  fetchAdminLore,
  fetchAdminStats,
  fetchAdminUsers,
  resetAdminUserPassword,
  toggleAdminUser,
} from "@/features/admin/api/adminApi";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { getApiErrorMessage } from "@/lib/apiError";

export function AdminPage() {
  const qc = useQueryClient();
  const currentUser = useCurrentUser();
  const [resetUserId, setResetUserId] = useState<number | null>(null);
  const [resetPasswordValue, setResetPasswordValue] = useState("");
  const stats = useQuery({ queryKey: ["admin", "stats"], queryFn: fetchAdminStats });
  const users = useQuery({ queryKey: ["admin", "users"], queryFn: fetchAdminUsers });
  const lore = useQuery({ queryKey: ["admin", "lore"], queryFn: fetchAdminLore });

  const reload = () => {
    qc.invalidateQueries({ queryKey: ["admin"] });
    qc.invalidateQueries({ queryKey: ["lore"] });
  };

  const deleteUser = useMutation({
    mutationFn: deleteAdminUser,
    onSuccess: reload,
  });

  const deleteLore = useMutation({
    mutationFn: deleteAdminLore,
    onSuccess: reload,
  });

  const toggleAdmin = useMutation({
    mutationFn: toggleAdminUser,
    onSuccess: reload,
  });

  const resetPassword = useMutation({
    mutationFn: ({ email, newPassword }: { email: string; newPassword: string }) =>
      resetAdminUserPassword(email, newPassword),
    onSuccess: () => {
      setResetUserId(null);
      setResetPasswordValue("");
    },
  });

  const topLore = useMemo(() => (lore.data ?? []).slice(0, 10), [lore.data]);
  const resetPasswordError = resetPassword.error
    ? getApiErrorMessage(resetPassword.error, "Unable to reset password right now.")
    : null;

  if (currentUser.isLoading) return <Card>Checking admin access...</Card>;
  if (!currentUser.data?.is_admin) return <Navigate to="/dashboard" replace />;

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Admin"
        title="Admin Console"
        description="Manage users, moderate stories, and monitor the platform at a glance."
      />

      <section className="grid gap-4 md:grid-cols-5">
        <Card><p className="text-xs uppercase tracking-[0.15em] text-lore-slate">Users</p><p className="mt-2 font-display text-4xl">{stats.data?.users ?? 0}</p></Card>
        <Card><p className="text-xs uppercase tracking-[0.15em] text-lore-slate">Admins</p><p className="mt-2 font-display text-4xl">{stats.data?.admins ?? 0}</p></Card>
        <Card><p className="text-xs uppercase tracking-[0.15em] text-lore-slate">Stories</p><p className="mt-2 font-display text-4xl">{stats.data?.lore ?? 0}</p></Card>
        <Card><p className="text-xs uppercase tracking-[0.15em] text-lore-slate">Comments</p><p className="mt-2 font-display text-4xl">{stats.data?.comments ?? 0}</p></Card>
        <Card><p className="text-xs uppercase tracking-[0.15em] text-lore-slate">Likes</p><p className="mt-2 font-display text-4xl">{stats.data?.likes ?? 0}</p></Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-3xl">Users</h2>
            <span className="text-sm text-lore-slate">{users.data?.length ?? 0} total</span>
          </div>
          <div className="space-y-3">
            {(users.data ?? []).slice(0, 20).map((u) => (
              <div key={u.id} className="rounded-2xl border border-black/10 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold text-lore-charcoal">{u.username}</p>
                    <p className="text-sm text-lore-slate">{u.email}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setResetUserId((current) => (current === u.id ? null : u.id));
                        setResetPasswordValue("");
                      }}
                      disabled={resetPassword.isPending}
                    >
                      Reset password
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => toggleAdmin.mutate(u.id)}
                      disabled={toggleAdmin.isPending || currentUser.data?.id === u.id}
                    >
                      {u.is_admin ? "Remove admin" : "Make admin"}
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={() => deleteUser.mutate(u.id)}
                      disabled={deleteUser.isPending || currentUser.data?.id === u.id}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
                {resetUserId === u.id ? (
                  <div className="mt-3 space-y-2 rounded-xl border border-black/10 bg-white/60 p-3">
                    <p className="text-sm text-lore-slate">Set a temporary password for {u.email}.</p>
                    <input
                      className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2"
                      type="password"
                      placeholder="Temporary password"
                      value={resetPasswordValue}
                      onChange={(event) => setResetPasswordValue(event.target.value)}
                    />
                    {resetPasswordError ? <p className="text-sm text-lore-terracotta">{resetPasswordError}</p> : null}
                    {resetPassword.isSuccess ? <p className="text-sm text-lore-forest">Password reset complete.</p> : null}
                    <div className="flex gap-2">
                      <Button
                        onClick={() => resetPassword.mutate({ email: u.email, newPassword: resetPasswordValue })}
                        disabled={resetPassword.isPending || resetPasswordValue.length < 8}
                      >
                        {resetPassword.isPending ? "Resetting..." : "Save temporary password"}
                      </Button>
                      <Button variant="ghost" onClick={() => setResetUserId(null)} disabled={resetPassword.isPending}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-3xl">Recent Stories</h2>
            <span className="text-sm text-lore-slate">{lore.data?.length ?? 0} total</span>
          </div>
          <div className="space-y-3">
            {topLore.map((item) => (
              <div key={item.id} className="rounded-2xl border border-black/10 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-lore-charcoal">{item.person}</p>
                    <p className="text-sm text-lore-slate">{item.theme} · by {item.author.username}</p>
                    <p className="mt-1 line-clamp-2 text-sm text-lore-slate">{item.question}</p>
                  </div>
                  <Button
                    variant="ghost"
                    onClick={() => deleteLore.mutate(item.id)}
                    disabled={deleteLore.isPending}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
