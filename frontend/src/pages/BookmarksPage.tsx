import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { fetchBookmarks } from "@/features/bookmarks/api/bookmarkApi";
import { fetchLore } from "@/features/lore/api/loreApi";
import { LoreCard } from "@/features/lore/components/LoreCard";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";

export function BookmarksPage() {
  const bookmarks = useQuery({ queryKey: ["bookmarks"], queryFn: fetchBookmarks });
  const lore = useQuery({ queryKey: ["lore"], queryFn: fetchLore });

  const bookmarkedStories = useMemo(() => {
    const bookmarkedIds = new Set((bookmarks.data ?? []).map((item) => item.lore_id));
    return (lore.data ?? []).filter((item) => bookmarkedIds.has(item.id));
  }, [bookmarks.data, lore.data]);

  const engagement = useLoreEngagement(bookmarkedStories.map((item) => item.id));

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="font-display text-4xl">Bookmarks</h1>
        <p className="text-lore-slate">Keep the stories that deserve a second reading close at hand.</p>
      </header>

      {bookmarks.isLoading || lore.isLoading ? <div className="rounded-3xl border border-black/10 bg-white/80 p-6">Loading your saved stories...</div> : null}
      {!bookmarkedStories.length && !bookmarks.isLoading ? (
        <EmptyState
          title="No bookmarks yet"
          description="Save the stories that stay with you. They will gather here for easy return."
          actionLabel="Explore Lore"
          actionTo="/explore"
        />
      ) : null}

      <section className="grid gap-4 xl:grid-cols-2">
        {bookmarkedStories.map((entry) => (
          <LoreCard
            key={entry.id}
            lore={entry}
            isBookmarked={engagement.bookmarkedLoreIds.has(entry.id)}
            isLiked={engagement.likedLoreIds.has(entry.id)}
            likeCount={engagement.likeCounts.get(entry.id) ?? 0}
            onToggleBookmark={(loreId, bookmarked) => engagement.toggleBookmark.mutate({ loreId, bookmarked })}
            onToggleLike={(loreId, liked) => engagement.toggleLike.mutate({ loreId, liked })}
          />
        ))}
      </section>
    </div>
  );
}
