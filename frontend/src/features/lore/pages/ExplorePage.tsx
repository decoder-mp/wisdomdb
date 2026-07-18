import { useDeferredValue, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { fetchLore } from "@/features/lore/api/loreApi";
import { LoreCard } from "@/features/lore/components/LoreCard";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";

export function ExplorePage() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const loreQuery = useQuery({ queryKey: ["lore", "explore"], queryFn: fetchLore });

  const filtered = useMemo(() => {
    const items = loreQuery.data ?? [];
    if (!deferredQuery.trim()) return items;
    return items.filter((entry) =>
      [entry.person, entry.theme, entry.question, entry.lore, entry.author.username]
        .join(" ")
        .toLowerCase()
        .includes(deferredQuery.toLowerCase()),
    );
  }, [deferredQuery, loreQuery.data]);

  const engagement = useLoreEngagement(filtered.map((entry) => entry.id));

  return (
    <div className="space-y-6">
      <header className="space-y-3">
        <h1 className="font-display text-4xl">Explore Lore</h1>
        <p className="max-w-2xl text-lore-slate">Search lived wisdom by theme, question, author, and life experience. The archive is meant for discovery, not noise.</p>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search stories, themes, questions"
          className="focus-ring w-full rounded-2xl border border-black/15 bg-white/80 px-4 py-3"
        />
        <p className="text-sm text-lore-slate">{filtered.length} stories found</p>
      </header>

      {loreQuery.isLoading ? <div className="rounded-3xl border border-black/10 bg-white/80 p-6">Loading the archive...</div> : null}
      {!loreQuery.isLoading && !filtered.length ? (
        <EmptyState
          title="No stories matched"
          description="Try another phrase, a broader theme, or explore without a filter to wander more freely through the archive."
        />
      ) : null}

      <section className="grid gap-4 xl:grid-cols-2">
        {filtered.map((entry) => (
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
