export function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="space-y-2">
      <p className="font-sans text-xs uppercase tracking-[0.18em] text-lore-forest">{eyebrow}</p>
      <h2 className="font-display text-3xl leading-tight text-lore-charcoal md:text-4xl">{title}</h2>
      {description ? <p className="max-w-2xl text-lore-slate">{description}</p> : null}
    </header>
  );
}
