import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { createLore } from "@/features/lore/api/loreApi";
import { getApiErrorMessage } from "@/lib/apiError";

const schema = z.object({
  person: z.string().min(2),
  profession: z.string().optional(),
  years_experience: z.coerce.number().min(0).max(80),
  theme: z.string().min(2),
  question: z.string().min(8),
  lore: z.string().min(30),
});

type FormValues = z.infer<typeof schema>;

export function CreateLorePage() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      person: "",
      profession: "",
      years_experience: 0,
      theme: "",
      question: "",
      lore: "",
    },
  });

  const mutation = useMutation({ mutationFn: createLore });

  const values = form.watch();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="font-display text-4xl">Share Your Wisdom</h1>
        <p className="mt-2 text-lore-slate">A guided, reflective writing flow with autosave-ready structure.</p>
      </header>

      <Card>
        <p className="text-sm uppercase tracking-[0.14em] text-lore-forest">Step {step} of 3</p>
        <form
          className="mt-4 space-y-4"
          onSubmit={form.handleSubmit(async (payload) => {
            const created = await mutation.mutateAsync(payload);
            form.reset();
            setStep(1);
            navigate(`/lore/${created.id}`);
          })}
        >
          {(step === 1 || step === 2) && (
            <>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Person</span>
                <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Person" {...form.register("person")} />
              </label>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Profession (optional)</span>
                <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Profession (optional)" {...form.register("profession")} />
              </label>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Years of Experience</span>
                <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" type="number" min={0} max={80} placeholder="Years of experience" {...form.register("years_experience")} />
              </label>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Theme</span>
                <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Theme" {...form.register("theme")} />
              </label>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Question</span>
                <textarea className="focus-ring min-h-[90px] w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Question" {...form.register("question")} />
              </label>
              <label className="block space-y-1">
                <span className="text-xs uppercase tracking-[0.12em] text-lore-forest">Lore</span>
                <textarea className="focus-ring min-h-[180px] w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Lore" {...form.register("lore")} />
              </label>
            </>
          )}

          {step === 3 && (
            <div className="rounded-2xl border border-black/10 bg-lore-ivory p-4">
              <h2 className="font-display text-2xl">Preview</h2>
              <p className="mt-2 font-medium">{values.person} - {values.theme}</p>
              <p className="mt-2 text-sm text-lore-slate">{values.question}</p>
              <p className="mt-3 whitespace-pre-wrap">{values.lore}</p>
            </div>
          )}

          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => setStep((s) => Math.max(1, s - 1))}>
              Previous
            </Button>
            {step < 3 ? (
              <Button type="button" onClick={() => setStep((s) => Math.min(3, s + 1))}>
                Next
              </Button>
            ) : (
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Publishing..." : "Publish"}
              </Button>
            )}
          </div>
          {mutation.isError ? <p className="text-sm text-lore-terracotta">{getApiErrorMessage(mutation.error, "Unable to publish story.")}</p> : null}
        </form>
      </Card>
    </div>
  );
}
