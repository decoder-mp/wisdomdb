import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  deleteNotification,
  fetchNotifications,
  readAllNotifications,
  readNotification,
} from "@/features/notifications/api/notificationApi";
import { formatDate } from "@/lib/utils";
import type { ApiList, Notification } from "@/types/api";

export function NotificationsPage() {
  const queryClient = useQueryClient();
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: fetchNotifications });

  const markRead = useMutation({
    mutationFn: readNotification,
    onMutate: async (notificationId) => {
      await queryClient.cancelQueries({ queryKey: ["notifications"] });
      const previous = queryClient.getQueryData<ApiList<Notification>>(["notifications"]);
      queryClient.setQueryData(["notifications"], (current: typeof previous) => {
        if (!current) return current;
        return {
          ...current,
          results: current.results.map((item) => (item.id === notificationId ? { ...item, is_read: true } : item)),
        };
      });
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["notifications"], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
  });
  const markAll = useMutation({
    mutationFn: readAllNotifications,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
  });
  const remove = useMutation({
    mutationFn: deleteNotification,
    onMutate: async (notificationId) => {
      await queryClient.cancelQueries({ queryKey: ["notifications"] });
      const previous = queryClient.getQueryData<ApiList<Notification>>(["notifications"]);
      queryClient.setQueryData(["notifications"], (current: typeof previous) => {
        if (!current) return current;
        const results = current.results.filter((item) => item.id !== notificationId);
        return { count: results.length, results };
      });
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["notifications"], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
  });

  const unreadCount = notifications.data?.results.filter((item) => !item.is_read).length ?? 0;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl">Notifications</h1>
          <p className="text-lore-slate">Timeline of meaningful activity around your stories.</p>
        </div>
        <Button variant="outline" onClick={() => markAll.mutate()} disabled={!unreadCount || markAll.isPending}>
          Read all
        </Button>
      </header>

      <Card className="bg-gradient-to-br from-white to-lore-ivory/80">
        <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Unread</p>
        <p className="mt-2 font-display text-4xl">{unreadCount}</p>
      </Card>

      {notifications.isLoading ? <Card>Loading notifications...</Card> : null}
      {!notifications.isLoading && !notifications.data?.results.length ? (
        <EmptyState
          title="No notifications"
          description="When readers respond to your stories or Lore refreshes your recommendations, those moments will appear here."
        />
      ) : null}

      <div className="space-y-3">
        {notifications.data?.results.map((item) => (
          <Card key={item.id} className={!item.is_read ? "border-lore-gold/60" : ""}>
            <div className="flex items-start justify-between gap-3">
              <div>
                {item.lore_id ? (
                  <Link
                    to={`/lore/${item.lore_id}`}
                    className="font-medium text-lore-charcoal transition hover:text-lore-terracotta"
                    onClick={() => {
                      if (!item.is_read) {
                        markRead.mutate(item.id);
                      }
                    }}
                  >
                    {item.message}
                  </Link>
                ) : (
                  <p className="font-medium">{item.message}</p>
                )}
                <p className="mt-1 text-xs uppercase tracking-[0.12em] text-lore-smoke">{item.type} - {formatDate(item.created_at)}</p>
              </div>
              <div className="flex gap-2">
                {!item.is_read ? (
                  <Button variant="ghost" onClick={() => markRead.mutate(item.id)}>
                    Read
                  </Button>
                ) : null}
                <Button variant="ghost" onClick={() => remove.mutate(item.id)}>
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
