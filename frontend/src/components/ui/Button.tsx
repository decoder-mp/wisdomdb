import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "focus-ring inline-flex min-h-11 items-center justify-center rounded-full px-5 py-2.5 text-sm font-semibold transition active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary" && "bg-gradient-to-r from-lore-charcoal via-lore-indigo to-lore-charcoal text-lore-ivory shadow-glow hover:from-lore-indigo hover:to-lore-ocean",
        variant === "ghost" && "text-lore-charcoal hover:bg-lore-ocean/10",
        variant === "outline" && "border border-lore-ocean/30 text-lore-charcoal hover:bg-lore-ocean/10",
        className,
      )}
      {...props}
    />
  );
}
