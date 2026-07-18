export type ApiList<T> = {
  count: number;
  results: T[];
};

export type User = {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
};

export type Lore = {
  id: number;
  person: string;
  profession: string;
  years_experience: number;
  theme: string;
  question: string;
  lore: string;
  created_at: string;
  user_id: number;
  author: User;
};

export type LoreInput = {
  person: string;
  profession?: string;
  years_experience: number;
  theme: string;
  question: string;
  lore: string;
};

export type Comment = {
  id: number;
  user_id: number;
  lore_id: number;
  content: string;
  created_at: string;
};

export type Bookmark = {
  id: number;
  user_id: number;
  lore_id: number;
};

export type LikeCount = {
  lore_id: number;
  likes: number;
};

export type Notification = {
  id: number;
  recipient_id: number;
  actor_id: number | null;
  lore_id: number | null;
  comment_id: number | null;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
};

export type Recommendation = {
  id: number;
  user_id: number;
  lore_id: number;
  score: number;
  reason: string;
  created_at: string;
  lore: Lore;
};

export type MutationMessage = {
  message: string;
};
