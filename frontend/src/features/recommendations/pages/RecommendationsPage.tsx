import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";
import {
  clearRecommendations,
  dismissRecommendation,
  fetchRecommendations,
  refreshRecommendations,
} from "@/features/recommendations/api/recommendationApi";
import { estimateReadingTime } from "@/lib/utils";

export function RecommendationsPage() {
  const queryClient = useQueryClient();
  const recommendations = useQuery({ queryKey: ["recommendations"], queryFn: fetchRecommendations });
  const engagement = useLoreEngagement((recommendations.data?.results ?? []).map((item) => item.lore.id));

  const refresh = useMutation({
    mutationFn: refreshRecommendations,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recommendations"] }),
  });
  const clearAll = useMutation({
    mutationFn: clearRecommendations,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recommendations"] }),
  });
  const dismiss = useMutation({
    mutationFn: dismissRecommendation,
    onMutate: async (recommendationId) => {
      await queryClient.cancelQueries({ queryKey: ["recommendations"] });
      const previous = queryClient.getQueryData<typeof recommendations.data>(["recommendations"]);
      queryClient.setQueryData(["recommendations"], (current: typeof previous) => {
        if (!current) return current;
        const results = current.results.filter((item) => item.id !== recommendationId);
        return { count: results.length, results };
      });
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["recommendations"], context.previous);
      }
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["recommendations"] }),
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl">Recommendations</h1>
          <p className="text-lore-slate">Stories chosen by overlap in themes, questions, and lived experience.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => clearAll.mutate()} disabled={!recommendations.data?.count || clearAll.isPending}>
            Clear all
          </Button>
          <Button onClick={() => refresh.mutate()}>{refresh.isPending ? "Refreshing..." : "Refresh"}</Button>
        </div>
      </header>

      {recommendations.isLoading ? <Card>Finding stories for you...</Card> : null}
      {!recommendations.isLoading && !recommendations.data?.results.length ? (
        <EmptyState
          title="No recommendations yet"
          description="Add a story or refresh after engaging with the archive. Lore will look for lived overlap, not shallow trends."
          actionLabel="Share your story"
          actionTo="/create"
        />
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        {recommendations.data?.results.map((item) => (
          <Card key={item.id} className="bg-gradient-to-br from-white to-lore-ivory/70">
            <p className="text-xs uppercase tracking-[0.12em] text-lore-forest">Similarity score {item.score.toFixed(2)}</p>
            <Link to={`/lore/${item.lore.id}`} className="mt-2 block font-display text-2xl text-lore-charcoal transition hover:text-lore-terracotta">
              {item.lore.person}
            </Link>
            <p className="mt-1 text-lore-slate">{item.reason}</p>
            <div className="mt-3 rounded-2xl border border-lore-ocean/20 bg-lore-ocean/5 p-3 text-sm text-lore-slate">
              <p><strong className="text-lore-charcoal">Shared themes:</strong> {item.lore.theme}</p>
              <p className="mt-1"><strong className="text-lore-charcoal">Shared life experience:</strong> {item.lore.profession || "General lived wisdom"}</p>
              <p className="mt-1"><strong className="text-lore-charcoal">Reading time:</strong> {estimateReadingTime(item.lore.lore)}</p>
            </div>
            <p className="mt-3 line-clamp-3">{item.lore.lore}</p>
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <Link to={`/profile?userId=${item.lore.author.id}`} className="text-sm text-lore-slate transition hover:text-lore-charcoal">
                by {item.lore.author.username}
              </Link>
              <div className="flex flex-wrap gap-2">
                <Link to={`/lore/${item.lore.id}`}>
                  <Button variant="outline">Open story</Button>
                </Link>
                <Button
                  variant={engagement.bookmarkedLoreIds.has(item.lore.id) ? "outline" : "ghost"}
                  onClick={() =>
                    engagement.toggleBookmark.mutate({
                      loreId: item.lore.id,
                      bookmarked: engagement.bookmarkedLoreIds.has(item.lore.id),
                    })
                  }
                >
                  {engagement.bookmarkedLoreIds.has(item.lore.id) ? "Saved" : "Save for later"}
                </Button>
                <Button variant="ghost" onClick={() => dismiss.mutate(item.id)}>
                  Dismiss
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
