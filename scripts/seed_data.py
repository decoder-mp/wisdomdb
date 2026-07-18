"""
Seed production-quality demo data for the Lore application.

Usage:
    python -m scripts.seed_data
    python -m scripts.seed_data --reset   (wipes existing data first)

Run from repository root.
"""

import argparse
import os
import sys
import sqlite3
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import SessionLocal
from core.security import hash_password
from sqlalchemy import text
from models.bookmark import Bookmark
from models.comment import Comment
from models.like import Like
from models.lore import Lore
from models.notification import Notification
from models.recommendation import Recommendation
from models.user import User


# ── helpers ──────────────────────────────────────────────────────────────────

def _reset(db):
    # ensure schema exists before attempting deletes
    from core.init_db import init_db
    init_db()
    # Backfill missing columns on SQLite (safe — fails silently if already exists)
    try:
        db.execute(text("ALTER TABLE lore ADD COLUMN user_id INTEGER"))
        db.commit()
    except sqlite3.OperationalError:
        db.rollback()
    except SQLAlchemyError:
        db.rollback()

    try:
        db.execute(text("ALTER TABLE lore ADD COLUMN embedding TEXT"))
        db.commit()
    except sqlite3.OperationalError:
        db.rollback()
    except SQLAlchemyError:
        db.rollback()
    for model in [Notification, Recommendation, Bookmark, Like, Comment, Lore, User]:
        try:
            db.query(model).delete()
        except SQLAlchemyError:
            db.rollback()
    db.commit()
    print("  reset: all rows deleted")


def _user(db, username, email, password, is_admin=False):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    u = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_admin=is_admin,
    )
    db.add(u)
    db.flush()
    return u


def _lore(db, user_id, person, profession, years, theme, question, lore_text):
    l = Lore(
        user_id=user_id,
        person=person,
        profession=profession,
        years_experience=years,
        theme=theme,
        question=question,
        lore=lore_text,
    )
    db.add(l)
    db.flush()
    return l


def _like(db, user_id, lore_id):
    if not db.query(Like).filter(Like.user_id == user_id, Like.lore_id == lore_id).first():
        db.add(Like(user_id=user_id, lore_id=lore_id))


def _comment(db, user_id, lore_id, content):
    c = Comment(user_id=user_id, lore_id=lore_id, content=content)
    db.add(c)
    db.flush()
    return c


def _bookmark(db, user_id, lore_id):
    if not db.query(Bookmark).filter(Bookmark.user_id == user_id, Bookmark.lore_id == lore_id).first():
        db.add(Bookmark(user_id=user_id, lore_id=lore_id))


def _notif(db, recipient_id, actor_id, lore_id, ntype, message):
    n = Notification(
        recipient_id=recipient_id,
        legacy_user_id=recipient_id,
        actor_id=actor_id,
        lore_id=lore_id,
        type=ntype,
        message=message,
        is_read=False,
    )
    db.add(n)


def _rec(db, user_id, lore_id, score, reason):
    if not db.query(Recommendation).filter(
        Recommendation.user_id == user_id, Recommendation.lore_id == lore_id
    ).first():
        db.add(Recommendation(user_id=user_id, lore_id=lore_id, score=score, reason=reason))


# ── seed ─────────────────────────────────────────────────────────────────────

def seed():
    db = SessionLocal()
    try:
        # ── Users ──────────────────────────────────────────────────────────
        admin   = _user(db, "lore_admin",   "admin@lore.app",         "Admin1234!", is_admin=True)
        eleanor = _user(db, "eleanor_w",    "eleanor@lore.app",       "Eleanor1!")
        james   = _user(db, "james_k",      "james@lore.app",         "JamesK99!")
        amara   = _user(db, "amara_o",      "amara@lore.app",         "AmaraOk1!")
        tomás   = _user(db, "tomas_r",      "tomas@lore.app",         "TomasR1!")
        chen    = _user(db, "chen_l",       "chen@lore.app",          "ChenLi1!")
        db.commit()

        # ── Lore entries (15) ──────────────────────────────────────────────
        lore_entries = [

            _lore(db, eleanor.id,
                  "Eleanor Whitmore", "Palliative Care Nurse", 22,
                  "Death & Dying",
                  "How do you sit with someone who knows they are dying, when you still fear death yourself?",
                  """After two decades on the ward, the weight of that question never left me — it just changed shape.

The first patient I lost, I cried in the car park for forty minutes. I was twenty-three. My charge nurse found me, sat on the bonnet beside me without saying anything. When I finally asked her how she did it, she said: "I stopped pretending I'm a wall and started being a window. People don't need barriers at the end — they need something they can see through."

That metaphor shaped everything. Being a window means you show your own humanity without letting it become the story. It means you can say "this is hard for me too" and still hold the space. Families would often apologise for crying, and I'd tell them: "Please — your grief is the proof that his life mattered."

The hardest shift of my career was a man called Arthur, 71, no family. He'd outlived everyone he loved. For three nights I sat with him during my breaks, reading the newspaper aloud, even the sport — he hated cricket but liked hearing about it anyway. He died on a Tuesday at 4 a.m. He'd told me the day before that those newspaper readings were his favourite hours. Not because of the news. Because of the company.

What I know now: dying people are not asking you to fix death. They are asking you not to be afraid of it in their presence. When you can manage that — even imperfectly — you give them permission to stop pretending too. That exchange is the most human thing I have ever been part of."""),

            _lore(db, james.id,
                  "James Kariuki", "Software Engineer", 12,
                  "Failure & Resilience",
                  "What do you do when the thing you've worked hardest on completely falls apart?",
                  """In 2019 I spent eleven months building a platform I believed would change how small farmers in East Africa accessed credit. My co-founder and I worked seven-day weeks. We had forty beta users who loved it. We had a seed investor lined up.

The investor pulled out three days before we were due to sign. The reason was geopolitical risk in the region — nothing to do with us. Within a week my co-founder accepted a job offer he'd previously declined. The product died.

I sat in my apartment for a week. I ordered the same ugali every evening because making decisions felt impossible. Then I opened a new document and typed the title: "What I actually learned." Not what went wrong — what I learned. The distinction mattered.

What I wrote: I had learned to ship production code in environments with intermittent connectivity. I had learned to interview farmers about money in a context where that was embarrassing. I had learned to navigate regulatory environments in three countries. I had learned that investor risk appetite is often entirely disconnected from product quality.

Those lessons did not die with the startup. Eighteen months later I joined a fintech that was failing at exactly the problem I'd been trying to solve. I walked in already knowing what they didn't yet know. That product is now live in six countries.

Failure has a return address. If you write it down rather than just mourn it, it mails you something useful."""),

            _lore(db, amara.id,
                  "Amara Osei", "Primary School Teacher", 18,
                  "Education & Childhood",
                  "How do you teach children who have seen violence, when they are sitting in your classroom trying to pretend they haven't?",
                  """I taught in a conflict-affected district for eight years. The question of how to teach curriculum when children are carrying invisible weight is one every teacher in such settings faces — and almost none of us were trained for it.

What I learned the hard way: presence before content. Every morning I spent the first ten minutes of class not on the syllabus, but on what I called "the weather report." Each child could give a one-word forecast: sunny, cloudy, stormy, foggy. Some children told me things in a word they had never told anyone. A boy named Kwame said "tornado" every day for two weeks. I arranged for him to see the school counsellor. He told the counsellor what was happening at home. Things changed for him.

The curriculum didn't suffer. If anything, children learned more once they felt the room was safe. Literacy scores in my class went up because children were willing to try — trying requires vulnerability, and vulnerability requires safety.

The thing nobody tells you about teaching in hard places: you will absorb some of the harm. I developed vicarious trauma around year four. I went to therapy. That is not a failure of professionalism. It is the cost of genuine contact with children's lives. You cannot outsource your heart and expect to teach.

What I tell young teachers now: Learn the names of their families. Learn what they ate for breakfast if you can. The distance between a child feeling seen and a child being lost is often one adult who remembered a detail."""),

            _lore(db, tomás.id,
                  "Tomás Reyes", "Structural Engineer", 31,
                  "Craft & Precision",
                  "What does it mean to build something that outlives you?",
                  """I have signed off on three bridges and one hospital wing. My name is on no plaque. Most of the people who cross those bridges or recover in those wards have no idea anyone made a decision that kept them alive.

This used to bother me. I came from a culture that valued visible legacy — the named building, the attributed achievement. In my thirties I spent energy resenting the anonymity.

Then I watched my father die in a hospital I had not built. The equipment worked. The floor was level. The power did not fail. Someone I would never know had designed that building with a faint and steady professionalism, and my father was alive three weeks longer because of it.

That changed what I thought legacy meant.

The bridge I am most proud of is a rural crossing in a mountainous region. It replaced a seasonal ford. Before we built it, one or two people drowned there every rainy season — usually children or elderly adults. After we built it, that stopped. I know this because a colleague who grew up there told me. I've never been back.

Legacy isn't a plaque. It's a harm that no longer happens. You will never see the accident that didn't occur, the child who didn't drown, the mother who made it to hospital in time. But they happened — or rather, they didn't happen — because you did your work with honesty.

I now teach my junior engineers: the building you are about to design will outlive your marriage, your retirement, and probably your children. Build it for that person, not for the photo."""),

            _lore(db, chen.id,
                  "Chen Li", "Epidemiologist", 15,
                  "Science & Uncertainty",
                  "How do you make decisions when the data is incomplete and people are dying?",
                  """Pandemic response forces the question that most of science deliberately avoids: what do you do when you cannot wait for certainty?

I worked on outbreak modelling for fifteen years before COVID. The discipline trains you in probability, confidence intervals, sensitivity analysis — all the tools of structured uncertainty. Then a novel pathogen arrives and every model is wrong, sometimes catastrophically.

The instinct is to keep waiting for better data. The reality is that waiting is itself a decision with consequences. In March 2020 I published a forecast that I had maybe 60% confidence in. I published it because the alternative — silence — would mean decision-makers had only worse information. I was attacked by statisticians for publishing a wide confidence interval. I was attacked by politicians for alarming the public. Both groups were more comfortable with certainty than with truth.

The thing that kept me going was a practice I'd developed from a mentor: "Decision-quality versus outcome-quality." A decision can be high quality — made with the best available evidence, through a sound process — and still produce a bad outcome. A decision can be low quality and produce a good outcome by chance. These are not the same thing. When an outcome is bad, the question to ask is whether the process was sound, not whether you were wrong.

This saves you from false lessons. If you got lucky, you shouldn't credit your method. If you made the right call and a bad thing still happened, you should not change your method.

Science under pressure means being very clear about what you know, what you don't know, and what you are assuming. It means saying those things out loud in rooms where people desperately want you not to."""),

            _lore(db, admin.id,
                  "Miriam Adeyemi", "Architect", 28,
                  "Design & Human Dignity",
                  "What does it mean to design spaces for people who have been treated as if they don't deserve beauty?",
                  """My first commission was a community centre in a district that had been scheduled for demolition twice and reprieved twice. The residents had been told for thirty years that their neighbourhood was temporary. Everything in it showed that: maintenance deferred, materials cheap, colour absent.

The brief from the community group was modest: a meeting room, a kitchen, a small office. The budget was very tight. My senior partner told me to do the minimum. Instead, I asked the community group what they had always wanted in a public space that they had never had.

An elderly woman said: "Windows you can see out of. Not high up, that you have to stand to see. Proper windows, at eye level when you're sitting."

That sentence reorganised the building. Every fixed seating position has a sightline to the outside. It cost nothing extra — it was a design decision, not a budget decision.

When the building opened, that woman sat in a chair by the window for two hours. She told me afterwards that it was the first time she had sat in a public building and felt like the building knew she was there.

I have told that story in every lecture I have given since. The purpose of design in under-resourced communities is not to make the best of limited means. It is to refuse the premise that limited means justify the removal of dignity. Every person who passes through a building sends something into it and takes something out of it. If the building treats them as an afterthought, they feel it. If it treats them as the point, they feel that too."""),

            _lore(db, eleanor.id,
                  "Eleanor Whitmore", "Palliative Care Nurse", 22,
                  "Grief & Loss",
                  "What do you do with grief that has nowhere to go?",
                  """There's a kind of grief that doesn't get recognised — disenfranchised grief, we call it clinically. The person who loses a long-term partner they were never allowed to be public about. The woman who miscarries and returns to work the same week because no one knew she was pregnant. The man whose estranged father dies before reconciliation was possible.

I have held hands with all of them. The absence of a ritual — no funeral you're invited to, no bereavement leave, no sympathy card — doesn't reduce the loss. It compounds it by adding invisibility.

What I have learned: grief needs a witness. It doesn't need solutions, timelines, or silver linings. It needs someone to say "that is a real loss and I see it." Sometimes in the absence of a community that can do that, one human being — a nurse, a counsellor, a friend who just sits — has to serve as the entire witness.

The hardest cases I've encountered are the carers. Partners who spent years as the sole support for someone with dementia, and when that person dies, feel not only grief but relief, and then feel ashamed of the relief. I tell them: the relief is the grief of the years before the death. The exhaustion was a bereavement in slow motion. You have been grieving for a very long time. The death is the last chapter of something that started years ago. All of it deserves to be held."""),

            _lore(db, james.id,
                  "James Kariuki", "Software Engineer", 12,
                  "Mentorship & Growth",
                  "What's the most important thing a mentor ever told you that you didn't understand at the time?",
                  """A senior engineer I worked under in my first year said something I wrote off as corporate wisdom: "Protect the junior engineers from the fire. Let them do the work without the politics."

I didn't understand what he meant until I was the senior engineer.

Politics in a tech team looks mundane from the outside — prioritisation meetings, stakeholder management, competing requirements from product and engineering. From the inside, it's consuming. It pulls experienced engineers out of flow state and into management tasks, relationship maintenance, and institutional negotiation. If junior engineers are exposed to that environment before they've had a chance to build confidence in their technical craft, many of them decide engineering isn't for them. They conclude that the job is mostly politics, and that's accurate for senior roles but destructive to absorb before you have the foundation to see it in proportion.

What my mentor was doing was spending his political capital so I didn't have to. He absorbed the friction so I could write code. When I became senior, I did the same thing — deliberately. I sat in meetings that my junior colleagues didn't need to be in. I filtered the chaos before it reached them.

The thing I didn't understand at the time was that this was not condescension. It was prioritisation. A junior engineer's most valuable asset is undivided attention to the craft. Protecting that is a technical decision."""),

            _lore(db, amara.id,
                  "Amara Osei", "Primary School Teacher", 18,
                  "Language & Identity",
                  "What happens to children who are taught that their home language is inferior?",
                  """In my district, the official language of instruction was different from the home languages of more than half the children. I watched the process of linguistic displacement play out every year: confident children arriving in class and slowly learning that their mother tongue had no official value.

This is not an abstract observation. It has a measurable effect on learning outcomes. Children who are taught to be ashamed of their first language often lose fluency in it without gaining full fluency in the new one. They become uncertain communicators in both. The technical term is semilingualism; the human experience is feeling that you don't quite belong anywhere.

I was not permitted to change the curriculum language. What I could change was the room. I allowed children to write first drafts in whichever language was clearest. I read stories aloud in translation, in both versions, so the shape of the child's thinking was honoured even when the official output had to be in the standard language. I displayed proverbs in three different languages around the room, with translations.

A girl in my third year who had been almost mute in class for two years handed me a story she'd written in her home language. It was extraordinary — long sentences, vivid imagery, precise emotion. I had it translated and read it to the class in both versions. She stood up straighter. She began speaking in class.

The lesson I carry: language is not a communication tool. It is the medium in which a child thinks themselves into being. Treat it with that kind of respect."""),

            _lore(db, tomás.id,
                  "Tomás Reyes", "Structural Engineer", 31,
                  "Mistakes & Accountability",
                  "Have you ever made a mistake in your work that you are still carrying?",
                  """Yes. One.

In my second year of independent practice I approved a foundation specification that I had not checked thoroughly enough. The contractor had deviated from the soil survey in a way that seemed minor. It wasn't minor. A portion of the floor slab cracked within eighteen months.

No one was hurt. The building was a storage facility. But I am the one who signed the certification. The building owner had to spend significantly on remediation. The contractor avoided liability because the contract language was ambiguous in a way I hadn't caught.

I paid for half the remediation out of my firm's pocket. Not because I was legally required to — the liability was unclear — but because that is what accountability meant to me. My senior partner at the time thought I was foolish.

What that experience gave me: a specific, visceral understanding of what happens when you rush a review. Not an abstract fear of consequences — a memory. I can still see the photograph of the cracked floor. I keep a copy in my office.

Carrying a mistake is not the same as being crushed by it. Carrying it means letting it be part of your practice. Every time I review a foundation specification, that memory activates something that checklists cannot. It makes me careful in a way that training made me thorough. The difference is that thoroughness is effort applied, and carefulness is attention you cannot fake.

I have told this story to every junior engineer I've supervised. The goal is not to frighten them. The goal is to let them know that the people who taught them are also still learning, and that accountability without self-destruction is possible."""),

            _lore(db, chen.id,
                  "Chen Li", "Epidemiologist", 15,
                  "Public Health & Trust",
                  "How do you communicate risk to a public that has been lied to before?",
                  """The hardest part of public health communication is not the complexity of the science. It's the inheritance of broken trust.

I've worked in regions where previous health campaigns contained factual errors that were later discovered, where vaccination programmes had genuine documented harms that were denied, where governments had used disease surveillance to identify and persecute minorities. The people who distrust official public health messages often have concrete historical reasons.

This cannot be managed with better graphic design or simpler messaging. It requires something much harder: institutional behaviour change over years. Acknowledge previous harms explicitly. Explain not just what you're recommending but why, including the uncertainty. Involve community leaders who are not government-aligned in the design of the message. Stop communicating as though the public is a passive recipient of expert wisdom.

The specific thing I have learned to do: distinguish between "we know X" and "we believe X" and "we are uncertain about X." Most public health authorities refuse to use the second and third categories. But the public is sophisticated enough to detect the absence of uncertainty language, and they interpret it as dishonesty, which it is. Acknowledging uncertainty does not erode trust. It builds the kind of trust that survives when the situation becomes clearer and some of what you said turns out to be wrong.

The people who trusted me the most in twenty years were people to whom I had said: "We're not completely sure about this. Here is what we know, here is what we're inferring, and here is what we'll change if we learn we were wrong." That sentence is the whole of trustworthy communication, in any domain."""),

            _lore(db, admin.id,
                  "Rosa Nakamura", "Family Law Barrister", 25,
                  "Justice & Compassion",
                  "How do you represent a client you believe is not telling the truth?",
                  """Criminal and family law are different from each other in many respects, but they share a particular test of character: how do you provide zealous legal representation to someone when you have private doubts about their version of events?

First, the structural answer: in most legal systems, a client does not have to be innocent to deserve representation, and representing them does not mean endorsing their account. A functioning adversarial system requires that every side be competently challenged. I am not the finder of fact. I present the strongest possible version of what my client says, probe the opposing evidence, and allow the court to decide.

But the human answer is harder. After twenty-five years I've learned to distinguish between doubt and disbelief. Doubt is normal — I almost never know the full truth of a situation. Disbelief — a settled conviction that my client is fabricating — happens rarely, but it does happen.

When it happens, I have a conversation. I do not accuse. I say: "I want to make sure I understand your account correctly, because the strongest case I can make for you depends on it. Tell me again, in detail, about X." Often this surfaces something I'd missed. Sometimes the client corrects themselves. Occasionally, the conversation makes it clear to me that I cannot properly represent this person any further, and I have to explain why I need to withdraw.

The thing I hold onto: the people who come to me in family court are usually in the worst period of their lives. Their judgment is impaired by fear and grief. They do not always tell me the truth because they are not always sure what the truth is. My job is not to judge them. My job is to help them navigate a system that will. Those are different tasks."""),

            _lore(db, eleanor.id,
                  "Eleanor Whitmore", "Palliative Care Nurse", 22,
                  "Presence & Attention",
                  "What is the most important skill in caring for people, that nobody teaches?",
                  """Not clinical competence — that's essential but teachable. Not empathy — that word has been so overused that it's lost precision. What I mean is something I would call: the skill of staying in the room.

Most people, when confronted with extreme suffering, leave in small ways. They look at their phone. They address the ceiling rather than the person. They talk faster. They suggest things that don't need suggesting, not because suggestions are needed but because action fills the silence that suffering creates.

Staying in the room means resisting the pull to leave. It means that when a person tells you they are terrified of dying, you don't immediately offer reassurance. You say "tell me more about that" and you mean it. It means your face doesn't change in a way that signals distress that the other person will feel obligated to manage.

This is an extraordinarily difficult skill to maintain over a long career. It is not passive — it requires active regulation of your own nervous system. I learned to breathe differently before entering difficult rooms. I learned to notice when I was subtly withdrawing — a flicker of impatience, a slight lean toward the door — and bring myself back.

The reason it matters so much: people can feel when they have your full attention and when they don't. At the end of life, what people most need is not information, comfort, or intervention. What they most need is company — the real kind, from someone who is actually there."""),

            _lore(db, james.id,
                  "James Kariuki", "Software Engineer", 12,
                  "Purpose & Work",
                  "How do you avoid losing yourself in a career that rewards you for working constantly?",
                  """The technology industry is expert at making overwork feel like meaning.

When the work is interesting, when the team is good, when you're building something that feels significant, the exhaustion reads like purpose. You don't notice the substitution until something stops the machine — illness, a relationship crisis, a project collapse — and you find yourself not knowing who you are outside of your function.

That happened to me at thirty-one. I had been productive, by every external measure, for nine years. I had almost no non-professional friendships. My hobbies had quietly expired. I had difficulty sitting in a room without my laptop.

What I did: I made a list of everything I had stopped doing since I started working intensely. Music — I had played the oud seriously for twelve years and stopped. Cooking proper meals. Walking without a destination. Reading novels. I picked one thing from the list and started doing it again, without trying to make it productive.

The oud was the one I chose. I was terrible at first because I was out of practice, and being terrible at something I used to be good at was actually useful — it reminded me that incompetence is not permanent, and that effort can be its own satisfaction without any goal attached.

What I'd tell anyone earlier in their career: the self you bring to work is the one you've built outside it. If you stop building it, the work starts to hollow out too, because you have less of a real person to bring to it."""),

            _lore(db, amara.id,
                  "Amara Osei", "Primary School Teacher", 18,
                  "Belonging & Community",
                  "What makes a classroom feel like a place that belongs to the children rather than to the curriculum?",
                  """The clearest answer I can give: the presence of things they made that weren't assigned.

In a classroom that belongs to the curriculum, every object on the wall is a teaching aid or a target: a times table chart, a vocabulary list, a learning objective. In a classroom that belongs to the children, there is also evidence of them — their preferences, their histories, their humor.

In my classroom we had a corner I called the "question wall." Children could post any question on a card — anything they were genuinely wondering about — and it would stay up until we found an answer together or they took it down themselves. Over time the question wall became a character. Children would arrive in the morning and read the new questions. Some of the questions were academic. Some were existential. One seven-year-old wrote: "Why do people stop being friends?" It stayed on the wall for a term. We talked about it several times. I never gave a direct answer, because I didn't have one.

The physical environment is not separate from the learning environment. When children see their own questions on the wall, they understand that their wondering is the curriculum. When they see only pre-prepared material, they understand that education is something that happens to them rather than something they participate in.

The single intervention with the biggest impact in my experience: let children teach something. Anything. For ten minutes. The child who teaches knows it in a different way than the child who learned it. And every child watching knows that the teacher is willing to be displaced, which makes the teacher safer."""),
        ]

        db.commit()
        print(f"  created {len(lore_entries)} lore entries")

        # IDs for convenience
        ids = [l.id for l in lore_entries]

        # ── Likes ──────────────────────────────────────────────────────────
        like_pairs = [
            (eleanor, ids[1]), (eleanor, ids[4]), (eleanor, ids[7]), (eleanor, ids[11]),
            (james,   ids[0]), (james,   ids[2]), (james,   ids[5]), (james,   ids[12]),
            (amara,   ids[1]), (amara,   ids[3]), (amara,   ids[6]), (amara,   ids[9]),
            (tomás,   ids[0]), (tomás,   ids[4]), (tomás,   ids[8]), (tomás,   ids[13]),
            (chen,    ids[2]), (chen,    ids[5]), (chen,    ids[10]),(chen,    ids[14]),
            (admin,   ids[0]), (admin,   ids[6]), (admin,   ids[11]),
        ]
        for user, lore_id in like_pairs:
            _like(db, user.id, lore_id)
        db.commit()
        print(f"  created {len(like_pairs)} likes")

        # ── Comments ───────────────────────────────────────────────────────
        comments = [
            (james,   ids[0],  "This brought tears to my eyes. The window metaphor will stay with me for a very long time."),
            (amara,   ids[0],  "Arthur's newspaper readings — that detail about hating cricket but liking the company. Everything."),
            (tomás,   ids[0],  "I'm going to share this with my partner who is a nurse. She needs to hear this."),
            (eleanor, ids[1],  "The framing of failure having a return address is genuinely useful. I'm writing this down."),
            (chen,    ids[1],  "I went through something similar with a research project. The lessons-not-losses reframe took me two years to find. You articulated it so clearly."),
            (amara,   ids[2],  "The weather report morning ritual is one of the most practical things I've read about teaching in difficult contexts. I'm going to try it."),
            (james,   ids[2],  "Kwame's story. The one-word forecast. This should be standard practice everywhere."),
            (eleanor, ids[3],  "The accident that didn't happen. I work in healthcare and I feel this in my bones. Anonymous lives saved."),
            (admin,   ids[3],  "This reframing of legacy as harm that no longer occurs is the most quietly powerful thing I've read here."),
            (eleanor, ids[4],  "Decision quality versus outcome quality — I've been looking for these exact words for years."),
            (james,   ids[5],  "Sitting eye-level at eye-level. The window that costs nothing extra. Beautiful."),
            (chen,    ids[6],  "Disenfranchised grief for carers is so underrecognised. The slow-motion bereavement framing is clinically precise and humanly true."),
            (amara,   ids[8],  "What you describe here is why my own mother struggled for years. I never had the language for it until now."),
            (tomás,   ids[9],  "The cracked floor photograph on the wall. That's what integrity looks like in practice."),
            (eleanor, ids[10], "The distinction between doubt and disbelief — this is exactly the kind of ethical precision that doesn't get written down often enough."),
            (james,   ids[12], "The oud. Coming back to something you love that you'd abandoned. I'm going to find my sketchbook this weekend."),
            (chen,    ids[13], "The question wall. A seven-year-old asking why people stop being friends. I want to be in that class."),
            (amara,   ids[14], "Let children teach something. Yes. This is the whole theory of learning in four words."),
        ]
        for user, lore_id, content in comments:
            _comment(db, user.id, lore_id, content)
        db.commit()
        print(f"  created {len(comments)} comments")

        # ── Bookmarks ──────────────────────────────────────────────────────
        bookmark_pairs = [
            (admin,   ids[0]), (admin,   ids[4]), (admin,   ids[9]),
            (eleanor, ids[1]), (eleanor, ids[7]), (eleanor, ids[10]),
            (james,   ids[0]), (james,   ids[5]), (james,   ids[12]),
            (amara,   ids[2]), (amara,   ids[8]), (amara,   ids[13]),
            (tomás,   ids[3]), (tomás,   ids[9]), (tomás,   ids[11]),
            (chen,    ids[4]), (chen,    ids[6]), (chen,    ids[14]),
        ]
        for user, lore_id in bookmark_pairs:
            _bookmark(db, user.id, lore_id)
        db.commit()
        print(f"  created {len(bookmark_pairs)} bookmarks")

        # ── Notifications ──────────────────────────────────────────────────
        notifs = [
            (eleanor.id, james.id,  ids[0],  "LIKE",    "James liked your story about sitting with dying patients."),
            (eleanor.id, amara.id,  ids[0],  "COMMENT", "Amara commented on your story: 'Arthur's newspaper readings…'"),
            (eleanor.id, tomás.id,  ids[0],  "COMMENT", "Tomás commented: 'I'm going to share this with my partner…'"),
            (james.id,   eleanor.id,ids[1],  "LIKE",    "Eleanor liked your story about the startup that collapsed."),
            (james.id,   chen.id,   ids[1],  "COMMENT", "Chen commented on your story: 'The lessons-not-losses reframe…'"),
            (amara.id,   james.id,  ids[2],  "COMMENT", "James commented: 'Kwame's story. The one-word forecast.'"),
            (amara.id,   admin.id,  ids[5],  "LIKE",    "Miriam liked your design story about eye-level windows."),
            (tomás.id,   admin.id,  ids[3],  "COMMENT", "Miriam commented: 'The most quietly powerful thing I've read here.'"),
            (chen.id,    eleanor.id,ids[4],  "LIKE",    "Eleanor liked your story about epidemiology under pressure."),
            (admin.id,   tomás.id,  ids[3],  "LIKE",    "Tomás liked your story about the bridge and invisible legacy."),
            (eleanor.id, None,      None,    "SYSTEM",  "Welcome to Lore. Your wisdom is now part of the circle."),
            (james.id,   None,      None,    "RECOMMENDATION", "New stories in 'Failure & Resilience' match your interests."),
            (amara.id,   None,      None,    "RECOMMENDATION", "Stories in 'Language & Identity' were saved by readers like you."),
        ]
        for recipient_id, actor_id, lore_id, ntype, msg in notifs:
            _notif(db, recipient_id, actor_id, lore_id, ntype, msg)
        db.commit()
        print(f"  created {len(notifs)} notifications")

        # ── Recommendations ────────────────────────────────────────────────
        recs = [
            (eleanor.id, ids[4],  8.5, "Matches your interest in science and evidence-based practice"),
            (eleanor.id, ids[11], 7.8, "Closely related to your theme of human dignity in professional work"),
            (james.id,   ids[7],  9.1, "Shared profession and mentorship theme"),
            (james.id,   ids[12], 8.7, "Overlapping themes of purpose and work-life integration"),
            (amara.id,   ids[6],  8.9, "Related to grief and invisible experiences — your area of care"),
            (amara.id,   ids[13], 9.2, "Strong match on community and belonging themes"),
            (tomás.id,   ids[9],  8.3, "Shared theme of mistakes and professional accountability"),
            (tomás.id,   ids[5],  7.9, "Related to craft, legacy and built environments"),
            (chen.id,    ids[10], 8.6, "Justice and institutional trust — adjacent to your public health work"),
            (chen.id,    ids[3],  7.5, "Long-term impact of professional decisions — a shared preoccupation"),
            (admin.id,   ids[0],  9.5, "Highest-rated story in the collection"),
            (admin.id,   ids[2],  9.0, "Highly engaged story with a strong community response"),
        ]
        for user_id, lore_id, score, reason in recs:
            _rec(db, user_id, lore_id, score, reason)
        db.commit()
        print(f"  created {len(recs)} recommendations")

        print("\n✓ Seed complete.")
        print("\n  Login credentials (all use password shown):")
        print("  admin@lore.app       / Admin1234!  (is_admin=True)")
        print("  eleanor@lore.app     / Eleanor1!")
        print("  james@lore.app       / JamesK99!")
        print("  amara@lore.app       / AmaraOk1!")
        print("  tomas@lore.app       / TomasR1!")
        print("  chen@lore.app        / ChenLi1!")

    finally:
        db.close()


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Lore demo data")
    parser.add_argument("--reset", action="store_true", help="Delete all existing data before seeding")
    args = parser.parse_args()

    reset_db = SessionLocal()
    if args.reset:
        print("Resetting database…")
        _reset(reset_db)
    reset_db.close()

    seed()
