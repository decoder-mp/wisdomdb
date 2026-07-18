import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type EmptyStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  actionTo?: string;
};

export function EmptyState({ title, description, actionLabel, actionTo }: EmptyStateProps) {
  return (
    <Card className="border-dashed bg-white/70 text-center">
      <h2 className="font-display text-2xl text-lore-charcoal">{title}</h2>
      <p className="mx-auto mt-3 max-w-xl text-lore-slate">{description}</p>
      {actionLabel && actionTo ? (
        <div className="mt-5">
          <Link to={actionTo}>
            <Button>{actionLabel}</Button>
          </Link>
        </div>
      ) : null}
    </Card>
  );
}