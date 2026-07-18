import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { fetchLore } from "@/features/lore/api/loreApi";

export function LandingPage() {
  const lore = useQuery({ queryKey: ["public", "lore"], queryFn: fetchLore });
  const stories = lore.data ?? [];
  const metrics = [
    { label: "Years of Experience Preserved", value: `${stories.reduce((sum, item) => sum + item.years_experience, 0)}+` },
    { label: "Stories Shared", value: `${stories.length}` },
    { label: "Voices Represented", value: `${new Set(stories.map((item) => item.author.id)).size}` },
    { label: "Themes Explored", value: `${new Set(stories.map((item) => item.theme.toLowerCase())).size}` },
    { label: "Recent Additions", value: `${stories.slice(0, 5).length}` },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8 md:py-14">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="grid gap-8 md:grid-cols-2"
      >
        <div className="space-y-6">
          <p className="font-sans text-xs uppercase tracking-[0.2em] text-lore-forest">Humanity's Living Memory</p>
          <h1 className="font-display text-5xl leading-tight text-lore-charcoal md:text-6xl">
            Every person carries a story. Every story carries wisdom.
          </h1>
          <p className="max-w-xl text-lg text-lore-slate">
            Lore preserves lived experience with calm, trust, and reflection. Enter a circle of stories worth remembering.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/explore">
              <Button>Explore Lore</Button>
            </Link>
            <Link to="/create">
              <Button variant="outline">Share Your Wisdom</Button>
            </Link>
          </div>
        </div>

        <aside className="relative overflow-hidden rounded-[2rem] border border-lore-ocean/20 bg-[linear-gradient(145deg,#163847_0%,#214e62_52%,#2d5b55_100%)] p-6 text-white shadow-[0_18px_46px_rgba(22,56,71,0.24)] md:p-8">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(239,138,61,0.12),transparent_28%),radial-gradient(circle_at_bottom_left,rgba(46,165,160,0.12),transparent_34%),linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.01))]" />
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.02),rgba(0,0,0,0.14))]" />
          <div className="relative z-10">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[#f6dda0]">Around The Fire</p>
            <blockquote className="mt-4 max-w-xl font-display text-3xl font-normal leading-tight text-white [text-shadow:0_1px_6px_rgba(0,0,0,0.28)] md:text-4xl">
              Before books and before the internet, people gathered around fire and passed wisdom forward.
            </blockquote>
            <p className="mt-6 max-w-xl reading-prose font-normal text-white/92 [text-shadow:0_1px_6px_rgba(0,0,0,0.22)]">
              Lore is the digital circle where elders, workers, parents, travelers, and makers preserve what life actually taught them.
            </p>
            <div className="mt-6 inline-flex max-w-xl items-center gap-3 rounded-2xl border border-white/12 bg-white/8 px-4 py-3 text-white backdrop-blur-sm">
              <span aria-hidden className="inline-block h-2.5 w-2.5 rounded-full bg-[#f6dda0] shadow-[0_0_0_4px_rgba(246,221,160,0.18)]" />
              <p className="text-sm font-medium">A place to return to for reflection, courage, and hard-earned clarity.</p>
            </div>
          </div>
        </aside>
      </motion.section>

      <section className="mt-14 grid gap-4 md:grid-cols-5">
        {metrics.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.06 }}
            className="rounded-2xl border border-black/10 bg-white/80 p-4"
          >
            <p className="font-display text-3xl text-lore-charcoal">{item.value}</p>
            <p className="mt-1 text-sm text-lore-slate">{item.label}</p>
          </motion.div>
        ))}
      </section>

      <section className="mt-16 space-y-8">
        <SectionHeading
          eyebrow="Mission"
          title="Preserve human wisdom before it disappears."
          description="Learning should feel sacred. Reading should feel intentional. Writing should feel meaningful."
        />
        <div className="grid gap-4 md:grid-cols-3">
          {stories.slice(0, 3).map((story) => (
            <Card key={story.id}>
              <p className="text-xs uppercase tracking-[0.12em] text-lore-forest">{story.theme}</p>
              <h3 className="mt-2 font-display text-2xl">{story.person}</h3>
              <p className="mt-3 line-clamp-2 text-lore-slate">{story.question}</p>
              <p className="mt-4 line-clamp-3 reading-prose">{story.lore}</p>
              <div className="mt-4 flex items-center justify-between gap-3">
                <p className="text-sm text-lore-slate">by {story.author.username}</p>
                <Link to="/register" className="text-sm font-semibold text-lore-terracotta">Join to read</Link>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
