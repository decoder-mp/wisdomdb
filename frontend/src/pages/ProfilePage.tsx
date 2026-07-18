import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { fetchBookmarks } from "@/features/bookmarks/api/bookmarkApi";
import { fetchLore } from "@/features/lore/api/loreApi";
import { LoreCard } from "@/features/lore/components/LoreCard";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";
import { fetchUserById, fetchUsers } from "@/features/users/api/userApi";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { formatDate } from "@/lib/utils";

export function ProfilePage() {
  const [searchParams] = useSearchParams();
  const userIdParam = Number(searchParams.get("userId") ?? "0");
  const currentUser = useCurrentUser();
  const bookmarks = useQuery({ queryKey: ["bookmarks"], queryFn: fetchBookmarks, enabled: Boolean(currentUser.data) });
  const lore = useQuery({ queryKey: ["lore"], queryFn: fetchLore });
  const selectedUser = useQuery({
    queryKey: ["user", userIdParam],
    queryFn: () => fetchUserById(userIdParam),
    enabled: Boolean(userIdParam) && Boolean(currentUser.data) && (currentUser.data?.is_admin || currentUser.data?.id === userIdParam),
  });
  const community = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
    enabled: Boolean(currentUser.data?.is_admin),
  });

  const derivedProfile = useMemo(() => {
    if (!userIdParam || userIdParam === currentUser.data?.id) {
      return currentUser.data;
    }

    if (selectedUser.data) {
      return selectedUser.data;
    }

    const author = (lore.data ?? []).find((item) => item.author.id === userIdParam)?.author;
    return author ?? null;
  }, [currentUser.data, lore.data, selectedUser.data, userIdParam]);

  const profileLore = useMemo(() => {
    if (!derivedProfile) return [];
    return (lore.data ?? []).filter((item) => item.user_id === derivedProfile.id);
  }, [derivedProfile, lore.data]);

  const editableUserId = derivedProfile?.id ?? 0;
  const profileStorageKey = `lore_profile_${editableUserId}`;
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(() => {
    if (!editableUserId) {
      return {
        fullName: "",
        bio: "",
        country: "",
        lifeStage: "",
        photoUrl: "",
      };
    }
    const raw = localStorage.getItem(profileStorageKey);
    if (!raw) {
      return {
        fullName: "",
        bio: "",
        country: "",
        lifeStage: "",
        photoUrl: "",
      };
    }
    try {
      return JSON.parse(raw) as {
        fullName: string;
        bio: string;
        country: string;
        lifeStage: string;
        photoUrl: string;
      };
    } catch {
      return {
        fullName: "",
        bio: "",
        country: "",
        lifeStage: "",
        photoUrl: "",
      };
    }
  });

  const isOwnProfile = Boolean(currentUser.data && derivedProfile?.id === currentUser.data.id);
  const profilePhoto = draft.photoUrl.trim();
  const wisdomShared = profileLore.length;
  const storiesBookmarked = isOwnProfile ? (bookmarks.data?.length ?? 0) : 0;
  const themesExplored = new Set(profileLore.map((item) => item.theme.toLowerCase())).size;
  const memberSince = derivedProfile?.created_at ? formatDate(derivedProfile.created_at) : "From the archive";
  const completionFields = [draft.fullName, draft.bio, draft.country, draft.lifeStage, profilePhoto].filter((item) => item.trim().length > 0).length;
  const completion = Math.round((completionFields / 5) * 100);

  const profileDetails = [
    { label: "Profile photo", value: profilePhoto ? "Uploaded" : "Not set" },
    { label: "Full name", value: draft.fullName || "Not set" },
    { label: "Username", value: derivedProfile?.username ?? "-" },
    { label: "Short biography", value: draft.bio || "Not set" },
    { label: "Country", value: draft.country || "Optional" },
    { label: "Life stage", value: draft.lifeStage || "Not set" },
    { label: "Wisdom shared", value: `${wisdomShared}` },
    { label: "Stories bookmarked", value: `${storiesBookmarked}` },
    { label: "Themes explored", value: `${themesExplored}` },
    { label: "Member since", value: memberSince },
  ];

  const recentActivity = [
    ...profileLore.slice(0, 3).map((entry) => `Published: ${entry.person} (${entry.theme})`),
    ...(isOwnProfile ? [`Bookmarked stories: ${storiesBookmarked}`] : []),
  ].slice(0, 4);

  const engagement = useLoreEngagement(profileLore.map((item) => item.id));

  useEffect(() => {
    if (!editableUserId) {
      return;
    }
    const raw = localStorage.getItem(`lore_profile_${editableUserId}`);
    if (!raw) {
      setDraft({
        fullName: "",
        bio: "",
        country: "",
        lifeStage: "",
        photoUrl: "",
      });
      return;
    }
    try {
      setDraft(JSON.parse(raw));
    } catch {
      setDraft({
        fullName: "",
        bio: "",
        country: "",
        lifeStage: "",
        photoUrl: "",
      });
    }
  }, [editableUserId]);

  return (
    <div className="space-y-6">
      <h1 className="font-display text-4xl">Profile</h1>

      {!derivedProfile ? (
        <EmptyState
          title="Profile unavailable"
          description="Lore could not resolve this profile from the current session. Try opening a story by this author first or return to your own profile."
          actionLabel="Go to my profile"
          actionTo="/profile"
        />
      ) : (
        <>
          <div className="grid gap-4 lg:grid-cols-[0.85fr,1.15fr]">
            <Card className="space-y-4">
              <div className="flex items-center gap-4">
                {profilePhoto ? (
                  <img
                    src={profilePhoto}
                    alt={`${derivedProfile.username} profile`}
                    className="h-16 w-16 rounded-full object-cover"
                  />
                ) : (
                  <div className="grid h-16 w-16 place-items-center rounded-full bg-lore-charcoal text-2xl font-display text-lore-ivory">
                    {derivedProfile.username.charAt(0).toUpperCase()}
                  </div>
                )}
                <div>
                  <h2 className="font-display text-3xl">{draft.fullName || derivedProfile.username}</h2>
                  <p className="text-lore-slate">{derivedProfile.email}</p>
                </div>
              </div>

              <div className="rounded-2xl border border-lore-ocean/20 bg-lore-ocean/5 p-3">
                <p className="text-xs uppercase tracking-[0.14em] text-lore-forest">Profile completion</p>
                <p className="mt-2 font-display text-3xl">{completion}%</p>
                <div className="mt-3 h-2 w-full rounded-full bg-white/70">
                  <div className="h-full rounded-full bg-gradient-to-r from-lore-ocean to-lore-turquoise" style={{ width: `${completion}%` }} />
                </div>
              </div>
            </Card>

            <Card className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <h2 className="font-display text-2xl">Profile details</h2>
                {isOwnProfile ? (
                  <Button variant="outline" onClick={() => setIsEditing((value) => !value)}>
                    {isEditing ? "Close editor" : "Edit profile"}
                  </Button>
                ) : null}
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {profileDetails.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-black/10 bg-white/60 p-3">
                    <p className="text-xs uppercase tracking-[0.13em] text-lore-forest">{item.label}</p>
                    <p className="mt-2 text-sm text-lore-charcoal">{item.value}</p>
                  </div>
                ))}
              </div>

              {isOwnProfile && isEditing ? (
                <form
                  className="grid gap-3"
                  onSubmit={(event) => {
                    event.preventDefault();
                    localStorage.setItem(profileStorageKey, JSON.stringify(draft));
                    setIsEditing(false);
                  }}
                >
                  <input
                    className="focus-ring rounded-xl border border-black/15 px-3 py-2"
                    placeholder="Full name"
                    value={draft.fullName}
                    onChange={(event) => setDraft((value) => ({ ...value, fullName: event.target.value }))}
                  />
                  <textarea
                    className="focus-ring min-h-[90px] rounded-xl border border-black/15 px-3 py-2"
                    placeholder="Short biography"
                    value={draft.bio}
                    onChange={(event) => setDraft((value) => ({ ...value, bio: event.target.value }))}
                  />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <input
                      className="focus-ring rounded-xl border border-black/15 px-3 py-2"
                      placeholder="Country"
                      value={draft.country}
                      onChange={(event) => setDraft((value) => ({ ...value, country: event.target.value }))}
                    />
                    <input
                      className="focus-ring rounded-xl border border-black/15 px-3 py-2"
                      placeholder="Life stage"
                      value={draft.lifeStage}
                      onChange={(event) => setDraft((value) => ({ ...value, lifeStage: event.target.value }))}
                    />
                  </div>
                  <input
                    className="focus-ring rounded-xl border border-black/15 px-3 py-2"
                    placeholder="Profile photo URL"
                    value={draft.photoUrl}
                    onChange={(event) => setDraft((value) => ({ ...value, photoUrl: event.target.value }))}
                  />
                  <Button type="submit">Save profile</Button>
                </form>
              ) : null}

              <div className="mt-1">
                <p className="text-xs uppercase tracking-[0.13em] text-lore-forest">Recent activity</p>
                <ul className="mt-2 space-y-2 text-sm text-lore-slate">
                  {recentActivity.map((entry) => (
                    <li key={entry} className="rounded-xl bg-white/50 px-3 py-2">{entry}</li>
                  ))}
                </ul>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link to="/bookmarks" className="text-sm font-semibold text-lore-terracotta">Open bookmarks</Link>
                <Link to="/notifications" className="text-sm font-semibold text-lore-terracotta">Open notifications</Link>
                <Link to="/recommendations" className="text-sm font-semibold text-lore-terracotta">Open recommendations</Link>
              </div>
            </Card>
          </div>

          <section className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="font-display text-3xl">Stories by {derivedProfile.username}</h2>
              <Link to="/create" className="text-sm font-semibold text-lore-terracotta">Share a new story</Link>
            </div>
            {!profileLore.length ? (
              <EmptyState
                title="No stories yet"
                description="This member has not added any stories to the archive yet."
              />
            ) : (
              <div className="grid gap-4 xl:grid-cols-2">
                {profileLore.map((entry) => (
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
              </div>
            )}
          </section>

          {currentUser.data?.is_admin ? (
            <section className="space-y-4">
              <h2 className="font-display text-3xl">Community Directory</h2>
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {community.data?.map((user) => (
                  <Link key={user.id} to={`/profile?userId=${user.id}`}>
                    <Card className="transition hover:-translate-y-0.5 hover:shadow-xl">
                      <p className="font-medium text-lore-charcoal">{user.username}</p>
                      <p className="text-sm text-lore-slate">{user.email}</p>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
