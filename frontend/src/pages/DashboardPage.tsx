import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { fetchLore } from "@/features/lore/api/loreApi";
import { LoreCard } from "@/features/lore/components/LoreCard";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";
import { fetchRecommendations } from "@/features/recommendations/api/recommendationApi";
import { fetchUnreadNotifications } from "@/features/notifications/api/notificationApi";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { formatDate } from "@/lib/utils";

export function DashboardPage() {
  const currentUser = useCurrentUser();
  const lore = useQuery({ queryKey: ["lore"], queryFn: fetchLore });
  const recommendations = useQuery({ queryKey: ["recommendations"], queryFn: fetchRecommendations });
  const unread = useQuery({ queryKey: ["notifications", "unread"], queryFn: fetchUnreadNotifications });
  const featuredLore = (lore.data ?? []).slice(0, 3);
  const engagement = useLoreEngagement(featuredLore.map((item) => item.id));

  return (
    <div className="space-y-10">
      <SectionHeading
        eyebrow="Return To The Circle"
        title={currentUser.data ? `Welcome back, ${currentUser.data.username}.` : "Welcome back."}
        description="A calm view of what matters most right now: a few meaningful stories, fresh recommendations, and the conversations waiting for you."
      />

      <section className="grid gap-4 lg:grid-cols-[1.2fr,0.8fr]">
        <Card>
          <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Today In Lore</p>
          <h2 className="mt-3 font-display text-3xl">Stay close to a few good things.</h2>
          <p className="mt-3 max-w-2xl text-lore-slate">
            Lore is quiet by design. Instead of an endless feed, you have a handful of stories worth revisiting, recommendations shaped by lived experience, and updates from readers who found meaning in your work.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/explore">
              <Button>Explore stories</Button>
            </Link>
            <Link to="/create">
              <Button variant="outline">Share wisdom</Button>
            </Link>
          </div>
        </Card>

        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          <Link to="/notifications">
          <Card className="transition hover:-translate-y-0.5 hover:shadow-xl">
            <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Unread Notifications</p>
            <p className="mt-2 font-display text-4xl">{unread.data?.count ?? 0}</p>
          </Card>
          </Link>
          <Link to="/recommendations">
          <Card className="transition hover:-translate-y-0.5 hover:shadow-xl">
            <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Recommendations Ready</p>
            <p className="mt-2 font-display text-4xl">{recommendations.data?.count ?? 0}</p>
          </Card>
          </Link>
          <Link to="/explore">
          <Card className="transition hover:-translate-y-0.5 hover:shadow-xl">
            <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Stories Preserved</p>
            <p className="mt-2 font-display text-4xl">{lore.data?.length ?? 0}</p>
          </Card>
          </Link>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Suggested Next Reads</p>
              <h2 className="font-display text-3xl">Stories chosen for resonance</h2>
            </div>
            <Link to="/recommendations" className="text-sm font-semibold text-lore-terracotta">
              View all
            </Link>
          </div>

          {recommendations.isLoading ? <Card>Gathering recommendations...</Card> : null}
          {!recommendations.isLoading && !recommendations.data?.results.length ? (
            <EmptyState
              title="No recommendations yet"
              description="Publish a story or like a few entries and Lore will begin finding thoughtful overlaps for you."
              actionLabel="Share your first story"
              actionTo="/create"
            />
          ) : null}

          <div className="space-y-4">
            {recommendations.data?.results.slice(0, 2).map((item) => (
              <Card key={item.id} className="bg-gradient-to-br from-white to-lore-ivory/70">
                <p className="text-xs uppercase tracking-[0.15em] text-lore-forest">Similarity score {item.score.toFixed(2)}</p>
                <Link to={`/lore/${item.lore.id}`} className="mt-2 block font-display text-2xl text-lore-charcoal transition hover:text-lore-terracotta">
                  {item.lore.person}
                </Link>
                <p className="mt-2 text-sm text-lore-slate">{item.reason}</p>
                <p className="mt-4 line-clamp-3 reading-prose">{item.lore.lore}</p>
                <div className="mt-4 flex items-center justify-between gap-3">
                  <Link to={`/profile?userId=${item.lore.author.id}`} className="text-sm text-lore-slate transition hover:text-lore-charcoal">
                    by {item.lore.author.username}
                  </Link>
                  <Link to={`/lore/${item.lore.id}`} className="text-sm font-semibold text-lore-terracotta">
                    Open story
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Conversations Waiting</p>
              <h2 className="font-display text-3xl">Gentle signals from readers</h2>
            </div>
            <Link to="/notifications" className="text-sm font-semibold text-lore-terracotta">
              Open inbox
            </Link>
          </div>

          {unread.data?.results.slice(0, 3).map((item) => (
            <Card key={item.id} className={!item.is_read ? "border-lore-gold/60 bg-lore-gold/5" : ""}>
              <p className="font-medium text-lore-charcoal">{item.message}</p>
              <div className="mt-3 flex items-center justify-between gap-3 text-sm text-lore-slate">
                <span>{item.type.split("_").join(" ")}</span>
                <span>{formatDate(item.created_at)}</span>
              </div>
            </Card>
          ))}

          {!unread.data?.results.length ? (
            <EmptyState
              title="Your inbox is quiet"
              description="That is not emptiness. It means you are caught up. Explore the archive when you are ready for the next discovery."
              actionLabel="Explore Lore"
              actionTo="/explore"
            />
          ) : null}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm uppercase tracking-[0.15em] text-lore-forest">Recent Additions</p>
            <h2 className="font-display text-3xl">New voices entering the archive</h2>
          </div>
          <Link to="/explore" className="text-sm font-semibold text-lore-terracotta">
            Browse all stories
          </Link>
        </div>

        {lore.isLoading ? <Card>Loading recent stories...</Card> : null}
        {!lore.isLoading && !featuredLore.length ? (
          <EmptyState
            title="No stories yet"
            description="The archive is waiting for its first memory. Share one lived lesson to begin the collection."
            actionLabel="Share a story"
            actionTo="/create"
          />
        ) : null}

        <div className="grid gap-4 xl:grid-cols-3">
          {featuredLore.map((item) => (
            <LoreCard
              key={item.id}
              lore={item}
              isBookmarked={engagement.bookmarkedLoreIds.has(item.id)}
              isLiked={engagement.likedLoreIds.has(item.id)}
              likeCount={engagement.likeCounts.get(item.id) ?? 0}
              onToggleBookmark={(loreId, bookmarked) => engagement.toggleBookmark.mutate({ loreId, bookmarked })}
              onToggleLike={(loreId, liked) => engagement.toggleLike.mutate({ loreId, liked })}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
