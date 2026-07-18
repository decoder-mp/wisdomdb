import { cn } from "@/lib/utils";

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <article
      className={cn(
        "surface-panel grain rounded-3xl border border-black/10 bg-white/85 p-5 shadow-vellum transition md:p-6",
        className,
      )}
    >
      {children}
    </article>
  );
}
