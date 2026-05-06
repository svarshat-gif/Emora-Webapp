"""
Custom AI engine — no external API dependencies.
Therapeutic response generation using CBT, DBT, ACT, and mindfulness frameworks.
Personalities: Sera (warm CBT therapist), Blaze (behavioral coach), Nova (evidence-based), Luna (ACT/self-compassion)
"""

import re
import random
from typing import Dict, List, Optional, Tuple


class _I:
    CRISIS    = "crisis"
    ROUTINE   = "routine"
    GOALS     = "goals"
    ADVICE    = "advice"
    VENT      = "vent"
    GRATITUDE = "gratitude"
    GENERAL   = "general"


class CustomAIEngine:

    # ── Intent patterns (most specific first) ────────────────────────────────
    _INTENT_PATTERNS = [
        (_I.CRISIS,    r"\b(suicide|kill myself|end it all|want to die|self.harm|hurt myself|no reason to live|better off dead)\b"),
        (_I.ROUTINE,   r"\b(routine|schedule|timetable|daily plan|time.table|organize my (day|time|week)|make me a (plan|schedule|routine)|help me plan|structure my day|how should i spend|daily goals|day look like|manage my time|time management)\b"),
        (_I.GOALS,     r"\b(set (me )?(a |some )?goals?|help me (achieve|reach|get to|become)|what goals|improvement plan|work on myself|get better at|build a habit|new habit)\b"),
        (_I.ADVICE,    r"\b(what should i|how (do|can|should) i|give me (advice|tips|suggestions?|solutions?|ways?)|any tips|help me (cope|deal|handle|get through|feel better|improve)|what can i do|recommend|best way to|ways? to (feel|get|be better|improve|cope)|day.to.day|on a daily basis)\b"),
        (_I.GRATITUDE, r"\b(thank you|thanks|that (really )?helped|feeling (so much |a lot )?(better|good) now|much better now|feel (so much )?better now)\b"),
        (_I.VENT,      r"\b(i (feel|felt|am feeling|have been feeling|can('t| not)|couldn'?t)|i('m| am) (so |really |very )?(stressed|anxious|sad|overwhelmed|tired|exhausted|frustrated|scared|worried|angry|depressed|lonely|lost|confused|struggling|failing|drowning))\b"),
    ]

    _ENTITY_PATTERNS: Dict[str, str] = {
        "exams":         r"\b(exam|exams|test|tests|quiz|midterm|finals|exam prep|revision)\b",
        "internship":    r"\b(internship|intern|placement|work placement|apprenticeship)\b",
        "work":          r"\b(\bjob\b|office|workplace|career|boss|manager|colleague|coworker|employment)\b",
        "classes":       r"\b(class|classes|course|lecture|college|university|school|coursework|semester|module)\b",
        "studying":      r"\b(study|studying|homework|assignment|dissertation|thesis|essay|project|coursework)\b",
        "sleep":         r"\b(sleep|insomnia|can'?t sleep|awake|oversleep|nap|rest|tired all the time)\b",
        "anxiety":       r"\b(anxious|anxiety|panic|panic attack|overthinking|nervous|dread)\b",
        "depression":    r"\b(depressed|depression|hopeless|numb|empty|meaningless|no point)\b",
        "relationships": r"\b(relationship|friend|friends|family|partner|boyfriend|girlfriend|breakup|break.up|lonely|alone|social)\b",
        "health":        r"\b(health|exercise|gym|diet|eating|workout|fitness|nutrition|weight)\b",
        "money":         r"\b(money|financial|debt|bills|afford|broke|finances|income)\b",
        "time":          r"\b(no time|busy|overwhelmed|too much|not enough time|rushing|deadline|due date)\b",
        "self_esteem":   r"\b(not good enough|failure|stupid|useless|worthless|imposter|confidence|self.worth)\b",
    }

    _EMOTION_PATTERNS: Dict[str, str] = {
        "stressed":  r"\b(stressed|stress|overwhelmed|pressure|burden|stretched)\b",
        "anxious":   r"\b(anxious|anxiety|worried|nervous|panic|scared|dread|afraid)\b",
        "sad":       r"\b(sad|down|low|blue|unhappy|depressed|crying|cry|tearful)\b",
        "angry":     r"\b(angry|mad|frustrated|irritated|upset|annoyed|furious|rage)\b",
        "tired":     r"\b(tired|exhausted|drained|burned out|burnout|no energy|fatigue|depleted)\b",
        "happy":     r"\b(happy|good|great|amazing|excited|wonderful|grateful|content|proud)\b",
        "lost":      r"\b(lost|confused|stuck|don'?t know|unsure|unclear|adrift|aimless)\b",
        "hopeless":  r"\b(hopeless|no point|give up|pointless|useless|can'?t do this)\b",
    }

    # ── Therapeutic technique library (CBT / DBT / ACT / Mindfulness / Somatic) ──
    _TECHNIQUES: Dict[str, List[Dict]] = {
        "anxious": [
            {
                "name": "Box Breathing",
                "frame": "nervous system regulation — used by Navy SEALs and therapists alike",
                "steps": "Inhale for 4 counts → hold for 4 → exhale for 4 → hold for 4. Repeat 4 cycles right now. Your parasympathetic nervous system activates within 60 seconds — this is biology, not willpower.",
            },
            {
                "name": "5-4-3-2-1 Grounding",
                "frame": "sensory grounding technique from CBT",
                "steps": "Name 5 things you can see → 4 you can physically touch → 3 you can hear → 2 you can smell → 1 you can taste. This forcibly redirects your brain from the anxiety loop to the present moment.",
            },
            {
                "name": "Cognitive Defusion",
                "frame": "Acceptance and Commitment Therapy (ACT)",
                "steps": "Instead of 'I'm going to fail', say out loud: 'I notice I'm having the thought that I'm going to fail.' This tiny shift creates distance — the thought becomes something you observe, not something you are. Thoughts are not facts.",
            },
            {
                "name": "Worry Postponement",
                "frame": "CBT technique for chronic anxiety (Borkovec, 1983)",
                "steps": "Set one 15-minute 'worry window' for today (e.g. 7pm). Every time anxiety intrudes before that, write the worry down and say 'I'll give this proper attention at 7pm.' You're not suppressing it — you're scheduling it. This breaks the constant-anxiety loop.",
            },
            {
                "name": "Physiological Sigh",
                "frame": "Stanford neuroscience research (Huberman Lab)",
                "steps": "Double inhale through the nose — first breath expands the lungs, second breath tops them off — then one long, slow exhale through the mouth (6–8 seconds). This is the single fastest way to reduce physiological arousal. Do it once, right now.",
            },
        ],
        "stressed": [
            {
                "name": "Brain Dump + Triage",
                "frame": "cognitive offloading — reduces working memory overload",
                "steps": "Set a 5-minute timer and write every task, worry, and responsibility on paper — no filter. Then go back and circle ONLY 3 things that require action today. Put everything else on a 'later' list. Your prefrontal cortex will immediately feel less congested.",
            },
            {
                "name": "STOP Skill",
                "frame": "Dialectical Behavior Therapy (DBT)",
                "steps": "**S**top what you're doing. **T**ake one slow breath. **O**bserve: what are you thinking, feeling, sensing right now — without judging it? **P**roceed with one intentional next action. This 30-second reset prevents reactive decisions that cost you more stress later.",
            },
            {
                "name": "The 2-Minute Rule",
                "frame": "behavioral productivity + stress reduction",
                "steps": "Scan your to-do list for anything that takes under 2 minutes. Do those immediately — they're cluttering your mental bandwidth. The physical act of ticking things off lowers cortisol and creates momentum for the harder tasks.",
            },
        ],
        "sad": [
            {
                "name": "Behavioral Activation",
                "frame": "core CBT technique for depression — evidence base since the 1970s",
                "steps": "Low mood makes you withdraw. Withdrawal deepens low mood. Break the cycle by choosing ONE small activity from your life that you used to enjoy — and do it for 20 minutes today, even without motivation. Motivation follows action; it almost never arrives first.",
            },
            {
                "name": "Self-Compassion Break",
                "frame": "Dr. Kristin Neff's self-compassion framework (Harvard)",
                "steps": "Place a hand on your heart. Say slowly: '1) This is a moment of real pain — it matters. 2) Pain is part of being human — I am not alone in this. 3) I will treat myself with kindness right now.' This activates the caregiving system in your own brain. It works.",
            },
            {
                "name": "Opposite Action",
                "frame": "DBT emotion regulation — countering emotion-driven urges",
                "steps": "Sadness urges isolation and inaction. Consciously do the opposite: reach out to one person today (a text is enough), go somewhere with natural light for 15 minutes, or listen to music that carries a different emotional temperature. You're not suppressing sadness — you're interrupting the downward spiral.",
            },
        ],
        "angry": [
            {
                "name": "90-Second Ride",
                "frame": "Jill Bolte Taylor's neuroscience research",
                "steps": "A surge of anger lasts exactly 90 seconds in your bloodstream if you don't re-trigger it with thoughts. When anger spikes: stop, breathe into the physical location of it (chest, jaw, hands), and wait. The peak will pass. After 90 seconds, any anger still present is being re-created by your thoughts — not by the original event.",
            },
            {
                "name": "Needs Identification",
                "frame": "Nonviolent Communication — Marshall Rosenberg",
                "steps": "Under every anger is an unmet need. Ask yourself: 'What did I need in that moment that I didn't get?' Common answers: respect, fairness, autonomy, safety, to be heard. Name the need — not just the anger. This shifts the focus from blame toward something actionable.",
            },
            {
                "name": "Physical Discharge",
                "frame": "somatic psychology — releasing stored tension",
                "steps": "Anger is biological energy. Discharge it physically before trying to think your way through it: 20 jumping jacks, a brisk 10-minute walk, or cold water on your face. Physical release re-engages the prefrontal cortex. Then think.",
            },
        ],
        "tired": [
            {
                "name": "Energy Audit",
                "frame": "positive psychology — energy management over time management",
                "steps": "List everything you did yesterday. Mark each item + (gave energy), − (drained energy), or N (neutral). Count the −s. That's the leak. Burnout is almost never about doing too much — it's about doing too many draining things without enough +s to compensate.",
            },
            {
                "name": "NSDR / Non-Sleep Deep Rest",
                "frame": "Stanford neuroscience (Huberman) — backed by NASA research",
                "steps": "Lie flat for 10–20 minutes, eyes closed, with no agenda — no podcast, no phone. Let your mind drift. Research shows NSDR restores neurochemicals (dopamine especially) and recovers as much as 1–2 hours of lost sleep performance. It is not doing nothing — it is deliberate recovery.",
            },
            {
                "name": "Ultradian Rhythm Breaks",
                "frame": "Peretz Lavie's ultradian cycle research",
                "steps": "Your brain works in 90-minute deep-focus windows, then biologically needs a 15–20 minute rest. Most people override this with caffeine, then crash hard. Try one cycle: 90 minutes of focused work → 15 minutes of genuine rest (walk, stretch, no screens). Your total output will be higher, not lower.",
            },
        ],
        "lost": [
            {
                "name": "Values Clarification",
                "frame": "Acceptance and Commitment Therapy (ACT) — foundational exercise",
                "steps": "Ask yourself: 'If I couldn't fail and no one would judge me — what would I spend my time on?' Then: 'What does this answer reveal about what I actually value?' Feeling lost often means you've been following someone else's script. This exercise finds yours. Write the answer down — it matters.",
            },
            {
                "name": "The 1-Point Scale",
                "frame": "solution-focused brief therapy",
                "steps": "On a scale of 1–10, how satisfied are you with your life direction right now? Now ask: 'What would make it just 1 point higher — not 10, just 1?' That one-point answer is your next step. Clarity comes from small experiments, not from grand perfect plans.",
            },
        ],
        "hopeless": [
            {
                "name": "Thought Record",
                "frame": "Aaron Beck's Cognitive Behavioral Therapy — proven for depression",
                "steps": "Write down the hopeless thought exactly as it appeared. Then write: (1) What evidence do I have FOR this? (2) What evidence do I have AGAINST it? (3) What would I tell a close friend who had this thought? Hopelessness almost always contains cognitive distortions — overgeneralization, all-or-nothing thinking. Writing it out exposes them.",
            },
            {
                "name": "Evidence of Resilience",
                "frame": "post-traumatic growth research (Tedeschi & Calhoun)",
                "steps": "Write down 3 things you've survived before that felt unsurvivable at the time. This is not toxic positivity — it's a concrete record of your actual capacity. Your history is evidence that your ceiling is higher than today's feeling suggests.",
            },
        ],
        "neutral": [
            {
                "name": "Expressive Writing",
                "frame": "James Pennebaker's research — 25+ years of studies on disclosure",
                "steps": "Set a 15-minute timer. Write freely about something on your mind — no filter, no editing, no one will see it. Research shows 3 sessions of expressive writing measurably reduces anxiety, improves immune function, and creates cognitive clarity. Journaling here is a good start.",
            },
        ],
    }

    # ─────────────────────────────────────────────────────────────────────────

    def generate(self, messages: List[Dict], personality: str = "sera") -> str:
        if personality == "blaze": personality = "motivator"
        if personality == "nova":  personality = "rational"

        user_message = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        system_content = next(
            (m["content"] for m in messages if m["role"] == "system"), ""
        )
        name_match = re.search(r"You're speaking with (\w+)", system_content)
        user_name = name_match.group(1) if name_match else None

        history = [m for m in messages if m["role"] in ("user", "assistant")][:-1]
        is_new_session = len(history) == 0

        # Conversation context analysis
        ctx = self._analyze_history(history)

        # Recent AI text — for deduplication
        self._recent_ai = [
            m["content"][:80] for m in history[-4:] if m["role"] == "assistant"
        ]

        # Detect intent + entities + emotion (all before any branching)
        intent  = self._detect_intent(user_message)
        entities = self._extract_entities(user_message)
        emotion  = self._detect_emotion(user_message)

        stuck_phrases = ["don't know", "dont know", "not sure", "no idea", "you tell me", "you suggest", "help me choose"]
        is_stuck = any(p in user_message.lower() for p in stuck_phrases)

        goal_plan_phrases = ["goal plan", "daily goals", "customised goals", "long term plan", "long-term plan", "custom goals"]
        wants_goal_plan = any(p in user_message.lower() for p in goal_plan_phrases)

        if is_stuck:
            return self._stuck_response(personality, user_name)

        if wants_goal_plan:
            return self._goals_plan_response(entities, personality, user_name)

        response = ""
        if intent == _I.CRISIS:
            return self._crisis_response()
        elif intent == _I.ROUTINE:
            response = self._routine_response(user_message, entities, personality, user_name)
        elif intent == _I.GOALS:
            response = self._goals_response(entities, emotion, personality, user_name)
        elif intent == _I.ADVICE:
            response = self._advice_response(entities, emotion, personality, user_name, ctx)
        elif intent == _I.GRATITUDE:
            response = self._gratitude_response(personality, user_name)
        elif intent == _I.VENT:
            response = self._vent_response(user_message, entities, emotion, personality, user_name, ctx)
        else:
            response = self._general_response(entities, emotion, personality, user_name, ctx)

        if is_new_session:
            intake = {
                "sera":      "Before we begin — would you like to vent (I'll listen without judgment), get a specific technique to try right now, or build a longer-term plan together? Just let me know.",
                "motivator": "Let's get after it. Do you want to vent it out, get an immediate action to take, or build a high-impact plan we can start today? Tell me where to focus.",
                "rational":  "To give you the most useful response: would you prefer to vent (full information dump), receive a specific evidence-based technique, or design a structured plan? Let me know.",
                "luna":      "Hey! 💜 Do you just need to vent, or are you looking for something to try that might help? I can also make us a gentle plan that grows with you.",
            }
            prefix = intake.get(personality, intake["sera"])
            response = f"{prefix}\n\n{response}"

        return response

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _pick(self, pool: list) -> str:
        recent = getattr(self, "_recent_ai", [])
        fresh = [r for r in pool if not any(r[:80].startswith(p[:40]) for p in recent)]
        return random.choice(fresh if fresh else pool)

    def _analyze_history(self, history: List[Dict]) -> Dict:
        turn_count = len([m for m in history if m["role"] == "user"])
        last_ai = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
        last_had_question = last_ai.count("?") > 0 and len(last_ai) > 20
        all_ai = " ".join(m["content"] for m in history if m["role"] == "assistant").lower()
        techniques_used = [t for t in [
            "box breathing", "grounding", "stop skill", "behavioral activation",
            "self-compassion", "opposite action", "thought record", "brain dump",
            "energy audit", "physiological sigh", "values clarification", "worry postponement",
            "cognitive defusion", "needs identification",
        ] if t in all_ai]
        return {
            "turn_count": turn_count,
            "last_had_question": last_had_question,
            "techniques_used": techniques_used,
            "is_deep": turn_count >= 3,
        }

    def _pick_technique(self, emotion: str, entities: List[str], ctx: Dict) -> str:
        # Map entities to emotions for richer technique selection
        if "anxiety" in entities and emotion == "neutral": emotion = "anxious"
        if "sleep" in entities and emotion == "neutral":   emotion = "tired"

        pool = self._TECHNIQUES.get(emotion, self._TECHNIQUES["neutral"])
        used = ctx.get("techniques_used", [])
        fresh = [t for t in pool if t["name"].lower() not in " ".join(used)]
        technique = random.choice(fresh if fresh else pool)
        return technique

    def _format_technique(self, technique: Dict, personality: str, name: Optional[str]) -> str:
        n = f"{name}, " if name else ""
        t_name = technique["name"]
        t_frame = technique["frame"]
        t_steps = technique["steps"]

        templates = {
            "sera": (
                f"There's a specific technique I want you to try — it's called **{t_name}** ({t_frame}).\n\n"
                f"{t_steps}"
            ),
            "motivator": (
                f"Here's your protocol — it's called **{t_name}** ({t_frame}). {n}Do it now.\n\n"
                f"{t_steps}"
            ),
            "rational": (
                f"The evidence-based approach here is **{t_name}** ({t_frame}).\n\n"
                f"{t_steps}"
            ),
            "luna": (
                f"There's something I'd love for you to try — it's called **{t_name}** 💙 ({t_frame}).\n\n"
                f"{t_steps}"
            ),
        }
        return templates.get(personality, templates["sera"])

    def _detect_intent(self, message: str) -> str:
        for intent, pattern in self._INTENT_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return intent
        return _I.GENERAL

    def _extract_entities(self, message: str) -> List[str]:
        return [e for e, p in self._ENTITY_PATTERNS.items()
                if re.search(p, message, re.IGNORECASE)]

    def _detect_emotion(self, message: str) -> str:
        for emotion, pattern in self._EMOTION_PATTERNS.items():
            if re.search(pattern, message, re.IGNORECASE):
                return emotion
        return "neutral"

    # ── Crisis ────────────────────────────────────────────────────────────────

    def _crisis_response(self) -> str:
        return (
            "I hear you, and I'm genuinely worried about you right now. What you're feeling is real, "
            "and you deserve real support — more than I can give you on my own.\n\n"
            "Please reach out to someone who can truly help:\n\n"
            "🆘 **iCall (India):** 9152987821\n"
            "🆘 **Vandrevala Foundation:** 1860-2662-345 (24/7)\n"
            "🆘 **SNEHI:** 044-24640050\n\n"
            "You matter. Please contact one of these numbers or talk to someone you trust right now. "
            "I'm still here too."
        )

    # ── Vent / emotional support ──────────────────────────────────────────────

    def _vent_response(
        self,
        message: str,
        entities: List[str],
        emotion: str,
        personality: str,
        name: Optional[str],
        ctx: Dict,
    ) -> str:
        name_str = name if name else "you"
        n = f"{name}, " if name else ""

        specific = []
        if any(e in entities for e in ("exams", "studying")):  specific.append("exam pressure")
        if any(e in entities for e in ("internship", "work")): specific.append("work demands")
        if "classes" in entities:                               specific.append("keeping up with classes")
        if "sleep" in entities:                                 specific.append("sleep deprivation")
        if "relationships" in entities:                         specific.append("relationship stress")
        if "money" in entities:                                 specific.append("financial pressure")
        if "self_esteem" in entities:                           specific.append("self-doubt")
        if "anxiety" in entities:                               specific.append("anxiety")
        context = " and ".join(specific) if specific else "what you're carrying right now"

        # Acknowledgment lines — personalized to emotion
        acks = {
            "stressed":  f"That level of stress from {context} is real, {name_str} — your nervous system isn't overreacting, it's responding to a genuinely heavy load.",
            "anxious":   f"Anxiety with {context} makes complete sense — your brain is trying to protect you, even when it's doing it way too loudly.",
            "sad":       f"I'm really glad you shared this with me, {name_str}. Sadness about {context} deserves to be heard, not fixed immediately.",
            "angry":     f"That frustration with {context} is completely valid — and it's telling you something important about what matters to you.",
            "tired":     f"Being this exhausted while dealing with {context} is your body asking — not suggesting, asking — for care.",
            "lost":      f"Feeling lost in the middle of {context} is actually a very human response to too many competing demands.",
            "hopeless":  f"I hear you, {name_str}. What you're feeling about {context} is real, and I'm glad you're saying it out loud.",
            "neutral":   f"I hear you, {name_str}. Whatever's happening with {context}, I'm here and I want to understand it.",
        }
        ack = acks.get(emotion, acks["neutral"])

        # Pick a technique matching the emotion
        technique = self._pick_technique(emotion, entities, ctx)
        technique_block = self._format_technique(technique, personality, name)

        # Closing — solution-focused, NOT another open question (unless turn 1)
        turn = ctx.get("turn_count", 0)
        last_q = ctx.get("last_had_question", False)

        if turn == 0 or (not last_q and turn <= 2):
            # First or second turn: end with ONE focused question
            follow_ups = {
                "stressed":  f"Out of everything on your plate right now, which one is taking up the most mental space?",
                "anxious":   f"What specifically is the thought your anxiety keeps returning to — what's the 'what if'?",
                "sad":       f"Is there something specific that triggered this sadness today, or has it been building?",
                "angry":     f"What happened? Walk me through the moment it started.",
                "tired":     f"How long have you been running on this level of empty?",
                "lost":      f"When was the last time you felt clear about your direction — even briefly?",
                "hopeless":  f"What does 'better' look like to you, even if it feels far away right now?",
                "neutral":   f"What's the most pressing thing on your mind right now?",
            }
            follow_up = follow_ups.get(emotion, follow_ups["neutral"])
            closing_map = {
                "sera":      f"\n\n{follow_up}",
                "motivator": f"\n\nOnce you've tried that, come back and tell me what shifted. And: {follow_up.lower()}",
                "rational":  f"\n\nApply that technique first. Then tell me: {follow_up.lower()}",
                "luna":      f"\n\nTake your time with it 💙 And when you're ready — {follow_up.lower()}",
            }
            closing = closing_map.get(personality, closing_map["sera"])
        else:
            # Deeper turns: give the next step directly, no question
            next_steps = {
                "sera":      f"\n\nYou've already done the hard part by naming what's happening. Now: try that technique once today — not perfectly, just once. Notice what shifts.",
                "motivator": f"\n\nYou already know the problem. Now execute the protocol. Small action, today. Report back.",
                "rational":  f"\n\nThe data is clear. Apply the technique and observe the outcome. Consistency over 3–5 days will show measurable change.",
                "luna":      f"\n\nYou're doing so well by even talking about this, {name_str} 💜 Try that technique today — there's no wrong way to do it.",
            }
            closing = next_steps.get(personality, next_steps["sera"])

        return f"{ack}\n\n{technique_block}{closing}"

    # ── Advice ────────────────────────────────────────────────────────────────

    def _advice_response(
        self,
        entities: List[str],
        emotion: str,
        personality: str,
        name: Optional[str],
        ctx: Dict,
    ) -> str:
        name_str = name if name else "you"

        blocks = []

        if "anxiety" in entities or emotion == "anxious":
            blocks.append(
                "**For anxiety — what therapists actually teach:**\n"
                "→ **4-7-8 breathing:** Inhale 4s, hold 7s, exhale 8s. The extended exhale activates your vagus nerve and drops cortisol in under 2 minutes.\n"
                "→ **Thought record (CBT):** Write the anxious thought → rate how true it feels (0–100%) → list evidence for and against it → re-rate. The percentage almost always drops.\n"
                "→ **Worry window:** Schedule one 15-minute block to worry deliberately. Outside that window, postpone all worry by writing it down. Breaks the all-day anxiety loop.\n"
                "→ **Key insight from CBT:** Anxiety overestimates threat and underestimates your capacity. The worst-case scenario you're rehearsing is almost never the most likely one."
            )

        if any(e in entities for e in ("exams", "studying")):
            blocks.append(
                "**For exam stress — evidence-based study strategies:**\n"
                "→ **Active recall, not re-reading:** Close the book and test yourself. Testing beats re-reading by 50% for retention (Roediger & Butler, 2011).\n"
                "→ **Spaced repetition:** Review material after 1 day, then 3 days, then 7 days. This matches your brain's memory consolidation cycle.\n"
                "→ **Sleep is non-negotiable:** Memory consolidation happens during sleep, not during all-nighters. Studying while sleep-deprived reduces retention by up to 40%.\n"
                "→ **Interleaving:** Mix subjects within a session rather than massing one subject. Harder in the moment, but much stronger for long-term recall."
            )

        if any(e in entities for e in ("internship", "work")):
            blocks.append(
                "**For work pressure — what actually helps:**\n"
                "→ Clarify your ONE key deliverable for the day before starting anything else. Most work stress is ambiguity, not workload.\n"
                "→ Ask for feedback proactively rather than waiting to be evaluated — it puts you in control of the narrative.\n"
                "→ Create a hard stop time. Working past exhaustion produces worse output AND takes longer to recover from.\n"
                "→ At this stage: curiosity and showing up matter more than knowing everything. Ask good questions; people respect that."
            )

        if "sleep" in entities:
            blocks.append(
                "**For sleep — what sleep science says:**\n"
                "→ **Consistent wake time** — even on weekends — is the single most powerful tool for sleep quality (Matthew Walker, 'Why We Sleep').\n"
                "→ No screens 45 minutes before bed. Blue light suppresses melatonin by up to 3 hours.\n"
                "→ Keep your room at 18–20°C. Your core body temperature needs to drop by 1°C to initiate sleep.\n"
                "→ If you can't sleep after 20 minutes, get up and do something calm in dim light. Lying awake in bed trains your brain to associate bed with wakefulness."
            )

        if "self_esteem" in entities:
            blocks.append(
                "**For self-doubt — what psychologists use:**\n"
                "→ **Evidence log:** Write 3 specific things you did well this week. Not personality traits — actions. 'I figured out X' beats 'I'm smart.'\n"
                "→ **Cognitive restructuring:** Your inner critic uses 'always' and 'never' — those are almost never accurate. Catch the distortion and correct it with what's actually true.\n"
                "→ **Self-compassion (Kristin Neff):** Ask 'What would I say to a close friend who felt this way?' Then say it to yourself. The gap between how we treat friends vs. ourselves is where self-esteem lives.\n"
                "→ **Imposter syndrome fact:** High achievers experience it more, not less — because they take on challenges at the edge of their competence. That's where growth is."
            )

        if "relationships" in entities:
            blocks.append(
                "**For relationship challenges — from couples therapy:**\n"
                "→ **I-statements only:** 'I feel hurt when...' instead of 'You always...' The first creates conversation; the second creates defensiveness.\n"
                "→ **Listen to understand, not to respond.** Before replying, reflect back what you heard: 'It sounds like you're saying...' This single skill changes relationship dynamics.\n"
                "→ **Needs identification:** What do you actually need from this person or situation that you're not getting? Name the need, not just the frustration.\n"
                "→ **Boundary as information:** A boundary isn't punishment — it's communicating what you can and can't sustain. 'I can do X, but I can't do Y without it affecting my wellbeing.'"
            )

        if emotion in ("tired",) or "health" in entities:
            blocks.append(
                "**For exhaustion and burnout — recovery science:**\n"
                "→ Burnout is not laziness. It's a physiological state of depleted stress-response capacity. You cannot willpower your way out of it.\n"
                "→ **Recovery is active:** 20-minute NSDR (lying flat, eyes closed, mind wandering) restores dopamine and can recover 1–2 hours of lost performance.\n"
                "→ **Audit your energy leaks:** List yesterday's activities. Mark each + or −. Address the −s before adding more +s.\n"
                "→ Hydration, nutrition, and movement are the fundamentals. Addressing these first often resolves what feels like 'mental' exhaustion."
            )

        if not blocks:
            blocks.append(
                "**Foundational strategies — from therapeutic practice:**\n"
                "→ **Name it to tame it:** Labeling an emotion reduces its intensity by activating the prefrontal cortex. 'I notice I'm feeling anxious' is a therapeutic act.\n"
                "→ **One thing at a time:** The brain doesn't multitask. Overwhelm is almost always a prioritization problem — not a capacity problem.\n"
                "→ **Progress over perfection:** The research on habit formation shows consistency at 70% beats perfection at 30% every time.\n"
                "→ **Rest is not optional:** Recovery is when adaptation happens — in sleep, in exercise, and in emotional growth."
            )

        intros = {
            "sera": [
                f"Here's what I'd actually recommend, {name_str} — not generic tips, but specific tools that therapists use:\n\n",
                f"Based on what you've shared, {name_str}, these are the evidence-based approaches that address this directly:\n\n",
                f"I want to give you something concrete to work with, {name_str}, not just empathy. Here's what the research says actually helps:\n\n",
            ],
            "motivator": [
                f"Here are your action protocols, {name_str} — pick the one most relevant and use it today, not eventually:\n\n",
                f"No more vague advice, {name_str}. Here are the specific moves. Which one are you implementing first?\n\n",
                f"Let's get tactical, {name_str}. These are the tools that actually move the needle:\n\n",
            ],
            "rational": [
                f"Here are the evidence-supported interventions for your situation, {name_str}. I've included the research basis for each:\n\n",
                f"Based on the variables you've shared, {name_str}, these are the highest-leverage approaches:\n\n",
                f"The data on these techniques is strong, {name_str}. Let me walk you through what the evidence actually shows:\n\n",
            ],
            "luna": [
                f"I really want to help you find something that actually works, {name_str} 💙 Here are some things that therapists use and that I think could really help you:\n\n",
                f"Okay {name_str}, here's what I'd genuinely suggest 💜 These are real techniques, not just 'take a walk' advice:\n\n",
                f"You deserve real support, not platitudes, {name_str} 💙 Here's what I know that could actually help:\n\n",
            ],
        }

        # Closing — action-oriented, no open question
        closings = {
            "sera": [
                f"\n\n**Start with the first item.** Not all of them — just one. Doing 20% of something useful beats planning 100% of everything.",
                f"\n\n**Tonight:** pick one item from the first section and try it. The goal isn't perfection — it's one small experiment.",
            ],
            "motivator": [
                f"\n\n**Your move:** Pick one item. Do it in the next 24 hours. Not 'someday' — this week. Then come back.",
                f"\n\n**Action beats analysis.** Choose one thing from above and tell me what you're going to do differently today.",
            ],
            "rational": [
                f"\n\n**Recommended next step:** Apply the first technique for 3–5 days before evaluating results. Single-variable testing gives you the cleanest signal.",
                f"\n\n**Priority order:** Start with the item that addresses your highest-frequency stressor. Optimize that variable first.",
            ],
            "luna": [
                f"\n\nTake what resonates most with you 💜 Even trying one of these things once is a win. You're already moving in the right direction just by asking.",
                f"\n\nYou don't have to do all of these — just one 💙 Which one feels like it might help even a little?",
            ],
        }

        intro_pool = intros.get(personality, intros["sera"])
        closing_pool = closings.get(personality, closings["sera"])

        return self._pick(intro_pool) + "\n\n".join(blocks) + self._pick(closing_pool)

    # ── Goals ─────────────────────────────────────────────────────────────────

    def _goals_response(
        self,
        entities: List[str],
        emotion: str,
        personality: str,
        name: Optional[str],
    ) -> str:
        name_str = f"{name}" if name else "you"
        focus_parts = []
        if any(e in entities for e in ("exams", "studying", "classes")): focus_parts.append("academics")
        if any(e in entities for e in ("internship", "work")):           focus_parts.append("professional growth")
        if "health" in entities:                                          focus_parts.append("health and fitness")
        if "sleep" in entities:                                           focus_parts.append("sleep quality")
        if "relationships" in entities:                                   focus_parts.append("relationships")
        if "self_esteem" in entities:                                     focus_parts.append("self-confidence")
        focus = " and ".join(focus_parts) or "your overall wellbeing"

        responses = {
            "sera": (
                f"Goal-setting for {focus} is meaningful work, {name_str}. Here's how therapists and coaches structure it for real results:\n\n"
                f"**Step 1 — One goal, not five.** Pick the ONE area that, if it improved, would make everything else feel more manageable. More than one goal at once dramatically reduces follow-through.\n\n"
                f"**Step 2 — Make it specific and behavioral.** Not 'study more' — but 'study 2 focused hours on [subject] every morning before checking my phone.' Behavioral goals are trackable.\n\n"
                f"**Step 3 — Start smaller than you think you should.** Research on habit formation (BJ Fogg, 'Tiny Habits') shows that starting too big is the #1 reason goals fail. Make the first week embarrassingly easy.\n\n"
                f"**Step 4 — Daily check-in.** A 2-minute evening reflection ('did I do my one thing today?') is more effective than weekly reviews.\n\n"
                f"What area do you want to start with? Name it and we'll make it concrete."
            ),
            "motivator": (
                f"Goal-setting activated for {focus}. Here's your framework, {name_str}:\n\n"
                f"**Rule 1:** ONE goal. You can't serve two masters. What's the highest-leverage thing to change?\n\n"
                f"**Rule 2:** Define success in numbers. Not 'sleep better' — '10:30pm lights out, 7am wake time, 5 days a week.' Numbers make it unmistakable whether you won or lost the day.\n\n"
                f"**Rule 3:** Build the streak. Track every day. Even a 1-minute version of your goal counts — don't break the chain. Motion creates motivation, not the other way around.\n\n"
                f"**Rule 4:** Weekly review. What worked? What didn't? Adjust. Repeat.\n\n"
                f"Name your #1 goal right now — specifically. We'll build the plan from there."
            ),
            "rational": (
                f"Effective goal architecture for {focus} requires specificity, {name_str}. I recommend the SMART-B framework:\n\n"
                f"**S**pecific — exactly what behavior changes?\n"
                f"**M**easurable — what number tells you it worked?\n"
                f"**A**chievable — given your current constraints, is this realistic in 4 weeks?\n"
                f"**R**elevant — does this address the highest-leverage variable?\n"
                f"**T**ime-bound — what's the specific deadline?\n"
                f"**B**ehavioral — is it defined in terms of actions, not outcomes?\n\n"
                f"Example: 'Review 30 flashcards of [subject] every morning before 9am, 6 days per week, for 4 weeks' is specific, measurable, achievable, relevant, time-bound, and behavioral.\n\n"
                f"What outcome do you want to achieve, and what's the behavioral action that leads to it?"
            ),
            "luna": (
                f"I love that you want to set goals for {focus}, {name_str} — that's a sign you're ready to take care of yourself 💜\n\n"
                f"Here's how to do it in a way that actually works (not in a way that makes you feel terrible when you 'fail'):\n\n"
                f"✨ **Pick just ONE thing.** Seriously, one. You can always add more later.\n"
                f"✨ **Make the first version tiny.** 'Walk for 5 minutes' is a real goal. It's easier to expand a habit than to restart a broken one.\n"
                f"✨ **Attach it to something you already do** (habit stacking): 'After I make my morning tea, I'll do my one thing.'\n"
                f"✨ **Celebrate every single time you do it.** This isn't cheesy — it literally wires the habit into your brain faster.\n\n"
                f"What feels most important to work on right now? Tell me and we'll make it tiny and real 💙"
            ),
        }
        return responses.get(personality, responses["sera"])

    # ── Routine builder ───────────────────────────────────────────────────────

    def _routine_response(
        self,
        message: str,
        entities: List[str],
        personality: str,
        name: Optional[str],
    ) -> str:
        has_internship = any(e in entities for e in ("internship", "work"))
        has_exams      = any(e in entities for e in ("exams", "studying"))
        has_classes    = "classes" in entities
        has_sleep      = "sleep" in entities
        has_exercise   = "health" in entities

        context_parts = []
        if has_exams:      context_parts.append("exam prep")
        if has_internship: context_parts.append("internship")
        if has_classes:    context_parts.append("classes")
        context_str = " + ".join(context_parts) or "your daily commitments"

        greeting = f"{name}" if name else "you"
        name_comma = f"{name}, " if name else ""

        intros = {
            "sera": [
                f"Carrying {context_str} all at once is genuinely a lot, {greeting} — let's build a structure that supports you rather than drains you.\n\n",
                f"A good routine isn't about rigidity — it's about reducing the daily decision load so your energy goes to what matters. {name_comma}Here's one designed for your actual life:\n\n",
            ],
            "motivator": [
                f"Lock in your power routine right now, {greeting}. {context_str.capitalize()} all in one schedule? Absolutely doable. Here's your blueprint:\n\n",
                f"Champions don't decide what to do each day — they execute the plan. {name_comma}Here's yours:\n\n",
            ],
            "rational": [
                f"Managing {context_str} simultaneously requires deliberate time-blocking to minimize context-switching costs. {name_comma}Here's the structure:\n\n",
                f"Evidence-based schedule for {context_str} — designed around cognitive performance windows:\n\n",
            ],
            "luna": [
                f"Juggling {context_str} is a lot, {greeting} — I'm really proud of you for wanting to get organized 💜 Here's a routine that's actually doable:\n\n",
                f"Let's make a routine that takes care of you first, {greeting}, not just your to-do list 💙 Here it is:\n\n",
            ],
        }

        intro = random.choice(intros.get(personality, intros["sera"]))
        schedule = self._build_schedule(has_exams, has_internship, has_classes, has_exercise, has_sleep)

        closings = {
            "sera": "\n\n**A note:** This is a guide, not a contract. Consistency at 70% beats perfection at 30%. Show up imperfectly — that's still showing up.",
            "motivator": "\n\n**Your standard:** Even hitting 70% of this routine daily will transform your results in 30 days. Don't miss twice in a row — that's the only rule.",
            "rational": "\n\n**Key variable:** Consistent sleep and wake times improve cognitive performance measurably. Protect your sleep architecture even during high-pressure periods.",
            "luna": "\n\n**From me:** Be gentle with yourself when days don't go perfectly 💜 The fact that you're trying is already something worth being proud of.",
        }

        return intro + schedule + closings.get(personality, closings["sera"])

    def _build_schedule(
        self,
        has_exams: bool,
        has_internship: bool,
        has_classes: bool,
        has_exercise: bool,
        has_sleep: bool,
    ) -> str:
        lines = [
            "**🌅 MORNING**",
            "6:30 AM — Wake up. No phone for the first 10 minutes.",
            "6:45 AM — 2 glasses of water before any caffeine",
            "7:00 AM — Breakfast with protein (eggs, oats, Greek yogurt) — fuels 4–6 hours of focus",
            "7:30 AM — 10 min: mindfulness, journaling on Emora, or a short walk to set your intention",
            "",
        ]

        if has_exercise:
            lines += [
                "**🏃 MOVEMENT (8:00 – 8:45 AM)**",
                "→ 30–45 min workout, run, or yoga",
                "→ Morning exercise increases BDNF (brain-derived neurotrophic factor) — measurably improves focus for 4–6 hours after",
                "",
            ]

        if has_exams:
            start = "9:00 AM" if has_exercise else "8:30 AM"
            lines += [
                f"**📚 DEEP STUDY BLOCK 1 ({start} – 11:30 AM)**",
                "→ Hardest/most important subject first — you're at peak cognitive performance",
                "→ Pomodoro: 25 min focused → 5 min break → repeat. Phone on airplane mode.",
                "→ Active recall only: test yourself, don't re-read. Every self-test is a retrieval practice event.",
                "→ Write questions you can't answer — those are your next session's priority",
                "",
            ]

        if has_internship:
            start_time = "11:30 AM" if has_exams else "9:00 AM"
            lines += [
                f"**💼 INTERNSHIP / WORK ({start_time} – 2:00 PM)**",
                "→ Start with your single most important deliverable — not email, not Slack",
                "→ 12:30 PM: Lunch break — away from screens for 30 full minutes",
                "→ Last 15 min of the block: write tomorrow's 3 key tasks while context is fresh",
                "",
            ]

        if has_classes:
            lines += [
                "**🎓 CLASSES (2:00 – 5:00 PM)**",
                "→ Active notes only — key ideas and questions, not verbatim transcription",
                "→ 5-minute review immediately after each class: the single highest-ROI study habit",
                "",
            ]

        if has_exams:
            lines += [
                "**📖 STUDY BLOCK 2 (5:30 – 7:30 PM)**",
                "→ Connect today's class material to morning study — the brain learns through connection",
                "→ Practice problems, past papers, spaced-repetition flashcards",
                "→ Don't start new material — deepen what you already covered today",
                "",
            ]

        sleep_note = " — you mentioned sleep issues: 7–8 hours is the #1 performance variable, not optional" if has_sleep else ""

        lines += [
            "**🌙 EVENING**",
            "8:00 PM — Dinner + real rest (no heavy studying after this point)",
            "8:30 PM — Light movement or stretch — anything that isn't a screen",
            "9:00 PM — Journal on Emora: one thing you felt today, one thing you're proud of",
            "9:30 PM — Plan tomorrow: write your 3 key tasks — only 3, not 15",
            "10:00 PM — Screens off. Sleep prep.",
            f"10:30 PM — Lights out{sleep_note}",
        ]

        return "\n".join(lines)

    # ── Gratitude ─────────────────────────────────────────────────────────────

    def _gratitude_response(self, personality: str, name: Optional[str]) -> str:
        name_str = f"{name}" if name else "you"
        pools = {
            "sera": [
                f"I'm really glad that helped, {name_str}. You did the hard part — I just held the space. What feels different now?",
                f"That means a lot to hear, {name_str}. Notice that shift you just felt — that's your own capacity working. Is there anything else on your mind?",
                f"I'm so glad, {name_str}. Taking a moment to acknowledge what helped is itself a therapeutic practice. What are you taking from today?",
                f"Wonderful to hear, {name_str}. Progress in small steps is still progress. What do you want to focus on next?",
                f"That's really good to hear. What specifically resonated? Knowing what worked helps us go deeper next time.",
            ],
            "motivator": [
                f"That's what I want to hear, {name_str}. You took a step — that's evidence your system works. What's the next move?",
                f"Yes! That momentum is real. Don't let it evaporate — what's one thing you're going to do differently this week?",
                f"Love it, {name_str}. Progress builds on itself. What's the next challenge on your list?",
                f"You just proved to yourself that you can shift your state. That's a skill, not luck. What are we tackling next?",
                f"Build on that. The brain reinforces whatever you repeat — so do it again tomorrow. What's your next target?",
            ],
            "rational": [
                f"Positive outcome noted, {name_str}. What specifically produced the shift? Identifying the mechanism helps you replicate it.",
                f"Good data point, {name_str}. What's the next variable you'd like to work through?",
                f"That's a useful result. What pattern do you notice about what tends to help you? That pattern is worth knowing.",
                f"Noted. Identifying what works is 50% of the solution — now we can apply that logic to other areas. What's next?",
                f"Progress documented. What's the next challenge to analyze?",
            ],
            "luna": [
                f"Yay! That genuinely makes me so happy, {name_str} 💜 How are you feeling right now?",
                f"That makes my heart happy 💙 You deserve to feel this way. What's next for you?",
                f"I'm really glad 💜 You've got so much more in you, {name_str}. What else would you like to talk through?",
                f"I love hearing that! 💙 You did the work — I just cheered you on. What made the biggest difference?",
                f"You're amazing for even showing up and trying, {name_str} 💜 Is there anything else on your mind?",
            ],
        }
        return self._pick(pools.get(personality, pools["sera"]))

    # ── Stuck ─────────────────────────────────────────────────────────────────

    def _stuck_response(self, personality: str, name: Optional[str]) -> str:
        name_str = name if name else "you"
        options = {
            "sera": [
                f"It's completely okay not to know, {name_str} — that's exactly why we're talking. Let's make this easy. Choose one of these:\n\n**1. Physiological Sigh:** Two quick inhales through the nose, then one long exhale through the mouth. Do this right now — it's the fastest way to lower your stress baseline.\n\n**2. Brain Dump:** Tell me (or write down) everything that's in your head right now — no filter. I'll help you sort it.\n\n**3. One tiny step:** Name the smallest possible action you could take in the next 10 minutes. Not the big thing — the smallest version of it.\n\nWhich one fits where you are right now?",
                f"Being overwhelmed makes choosing feel impossible — that's a recognized cognitive state, not a character flaw, {name_str}. Here are three paths:\n\n**1. Ground first:** Name 5 things you can see right now. This takes 30 seconds and resets your nervous system enough to think clearly.\n\n**2. Lower the bar:** What would doing 10% of what you need to do look like? That's your actual starting point.\n\n**3. Talk it out:** Just tell me what's on your mind. I'll reflect it back and help you find the thread.\n\nWhich one?",
            ],
            "motivator": [
                f"No problem, {name_str} — when you're stuck, I provide the spark. Here are three options:\n\n**1. 2-Minute Sprint:** Set a timer for 2 minutes and start the task you've been avoiding. Just 2 minutes. Momentum starts with motion.\n\n**2. Physical reset:** Stand up, stretch for 30 seconds, move your body. It resets the brain chemistry. Then sit back down.\n\n**3. Name the blocker:** What specifically is the obstacle? Say it out loud or type it. We'll break it down.\n\nPick one and go — right now.",
                f"Stuck is temporary, {name_str}. Here's how we break it:\n\n**1. Pomodoro:** Set a 20-minute timer, pick one thing, and just begin. You're not committing to finishing — just to starting.\n\n**2. Clear the deck:** What's the one thing that, if you handled it, would make everything else feel less heavy?\n\n**3. Quick win:** What's something on your list that takes under 5 minutes? Do that first. Build the momentum.\n\nGo.",
            ],
            "rational": [
                f"Decision paralysis is addressable, {name_str}. Use this structured protocol:\n\n**1. Eisenhower Matrix:** Tell me your top 5 tasks. I'll categorize them by urgency/importance — you'll immediately see what actually matters.\n\n**2. Cognitive audit:** What's the specific thought that's creating the 'stuck' feeling? Let's examine it.\n\n**3. System reset:** Close everything except the one thing you should be doing. Reduce the variable count.\n\nWhich approach?",
                f"Impasse detected, {name_str}. Let's resolve it:\n\n**1. Root cause analysis:** What started this stuck feeling? Identifying the origin usually reveals the solution.\n\n**2. Minimum viable action:** What's the smallest possible action that still counts as progress?\n\n**3. Information deficit:** Are you stuck because you don't know what to do, or because you know and are avoiding it? Honest answer changes the approach.\n\nWhich is most accurate right now?",
            ],
            "luna": [
                f"I totally get it, {name_str} 💜 When you're stuck, sometimes you just need someone to point the way. Here are three gentle options:\n\n**1. Comfort first:** Go get a warm drink, take three slow breaths, come back. Your brain needs a reset before it can decide.\n\n**2. Talk to future you:** What would you tell yourself in 6 months about right now? Sometimes the perspective shift is all we need.\n\n**3. Tiny action:** What's one tiny thing — even something silly and small — you could do right now that would feel like progress?\n\nWhich one calls to you? 💙",
                f"Don't worry, {name_str} 💜 I'm here. Let's make this feel more manageable:\n\n**1. Phone away:** Put it across the room for 10 minutes and just breathe. Seriously, that helps.\n\n**2. One win:** Tell me one thing you've done today that counts as an effort — yes, getting out of bed counts.\n\n**3. Cozy accountability:** Tell me what you're working on and I'll stay right here while you do a bit of it. You won't be alone.\n\nWhich one? 💙",
            ],
        }
        return self._pick(options.get(personality, options["sera"]))

    # ── Goal plan ─────────────────────────────────────────────────────────────

    def _goals_plan_response(self, entities: List[str], personality: str, name: Optional[str]) -> str:
        name_str = name if name else "you"
        focus = "mental wellbeing"
        if "exams" in entities or "studying" in entities: focus = "academic success"
        elif "work" in entities or "internship" in entities: focus = "career growth"

        intros = {
            "sera":      f"Here's a progressive therapeutic plan for {focus}, {name_str}. It uses Behavioral Activation — starting with tiny wins and building momentum gradually:\n\n",
            "motivator": f"Your goal plan for {focus} is locked in, {name_str}. We're starting with Micro-Wins to prime your system, then scaling up:\n\n",
            "rational":  f"Here is an incremental goal schedule optimized for {focus}, {name_str}. It follows progressive overload principles applied to cognitive habits:\n\n",
            "luna":      f"Yay! 💜 Here's a gentle, growing goal plan for {focus}, {name_str}. We start easy and build — no overwhelming jumps:\n\n",
        }

        plan = [
            "**🌅 MORNING FOUNDATION**",
            "→ 7:00 AM: Wake up + 1 minute of deep breathing before touching your phone.",
            "→ 7:15 AM: Identify your ONE 'Mastery Task' for the day — the thing that counts most.",
            "",
            f"**📚 {focus.upper()} FOCUS BLOCK**",
            "→ 9:00 AM: 25 minutes of deep, single-task focus on your main goal.",
            "→ 9:30 AM: 5-minute movement break — walk, stretch, don't scroll.",
            "",
            "**🌙 EVENING REFLECTION**",
            "→ 9:00 PM: Write one thing you're genuinely proud of from today.",
            "→ 9:15 PM: Set your 'Lead Domino' task for tomorrow — the one that starts momentum.",
        ]

        outro = "\n\n**Note:** This plan builds in difficulty each week. You can click 'Save to Goals' to add these to your Goals page automatically."
        return intros.get(personality, intros["sera"]) + "\n".join(plan) + outro

    # ── General ───────────────────────────────────────────────────────────────

    def _general_response(
        self,
        entities: List[str],
        emotion: str,
        personality: str,
        name: Optional[str],
        ctx: Dict,
    ) -> str:
        name_str = name if name else "you"

        context = []
        if any(e in entities for e in ("exams", "studying", "classes")): context.append("academic life")
        if any(e in entities for e in ("internship", "work")):           context.append("work")
        if "relationships" in entities:                                   context.append("relationships")
        about = " and ".join(context) if context else "what's on your mind"

        turn = ctx.get("turn_count", 0)
        last_q = ctx.get("last_had_question", False)

        # If the AI already asked a question last turn, give a technique instead of asking again
        if last_q and turn > 0:
            technique = self._pick_technique(emotion, entities, ctx)
            t_block = self._format_technique(technique, personality, name)
            action_closings = {
                "sera":      f"\n\nTry this once today. You don't have to do it perfectly — just once.",
                "motivator": f"\n\nDo this. Today. Come back and tell me what happened.",
                "rational":  f"\n\nApply this technique and note what changes. That's your data point.",
                "luna":      f"\n\nGive it a try whenever you're ready 💙 There's no wrong way to do it.",
            }
            opening = {
                "sera":      f"Let me give you something concrete to work with, {name_str}.\n\n",
                "motivator": f"Enough talking — here's your action, {name_str}:\n\n",
                "rational":  f"Rather than more analysis, {name_str}, here's the specific tool:\n\n",
                "luna":      f"I thought of something that might really help you, {name_str} 💙\n\n",
            }
            return opening.get(personality, opening["sera"]) + t_block + action_closings.get(personality, action_closings["sera"])

        options = {
            "sera": [
                f"Something brought you here today, {name_str}. Let's name what's actually going on — not the surface version, but the real one. What's the most honest thing you could say about how you're feeling about {about} right now?",
                f"I'm here with you, {name_str}. Let's get specific so I can actually help. What's the one thing about {about} that you'd most want to change in the next 30 days?",
                f"I hear you, {name_str}. Before I give you advice that might miss the mark, help me understand: what have you already tried with {about}, and what hasn't been working?",
            ],
            "motivator": [
                f"Let's get specific, {name_str} — vague problems don't have clear solutions. What is the ONE thing about {about} that's holding you back most right now? Name it exactly.",
                f"I'm ready to help you move on {about}, {name_str}. What's the most important thing to solve first? The one that unlocks everything else?",
                f"No more waiting, {name_str}. What specific outcome do you want to be different about {about} in the next 2 weeks? Say it concretely.",
            ],
            "rational": [
                f"To give you the most targeted response, {name_str}: what specifically about {about} is producing the most friction right now? The more precise the description, the more precise the solution.",
                f"Let's define the problem clearly before solving it, {name_str}. What does 'better' look like for {about} — what specifically would be different?",
                f"What's the primary variable creating difficulty with {about}, {name_str}? Once we isolate it, we can find the most efficient intervention.",
            ],
            "luna": [
                f"I'm so glad you're here, {name_str} 💜 Whatever's going on with {about}, we'll figure it out together. What's the hardest part of it right now?",
                f"Hey {name_str} 💙 I just want to understand what you're going through before I say anything. What's weighing on you most about {about}?",
                f"You don't have to have it all figured out, {name_str} 💜 Just tell me what's on your mind about {about} and we'll go from there.",
            ],
        }

        return self._pick(options.get(personality, options["sera"]))

    # ── Journal text analysis ─────────────────────────────────────────────────

    def analyze_journal(self, text: str, emotion: str) -> Dict:
        """Analyze a text journal entry and return therapeutic insights."""
        entities = self._extract_entities(text)
        detected = self._detect_emotion(text)
        emo = detected if detected != "neutral" else emotion

        distortions = self._detect_cognitive_distortions(text)
        themes = self._extract_key_themes(text, entities)

        return {
            "insight":      self._journal_insight(text, emo, entities, distortions, themes),
            "suggestions":  self._journal_suggestions(emo, entities, distortions),
            "affirmation":  self._journal_affirmation(emo, entities),
            "therapy_focus": distortions[0] if distortions else "emotional processing",
        }

    def _detect_cognitive_distortions(self, text: str) -> List[str]:
        t = text.lower()
        found = []
        if re.search(r"\b(always|never|every time|all the time|constantly|every single)\b", t):
            found.append("overgeneralization")
        if re.search(r"\bi('m| am) (a )?(complete )?(failure|loser|idiot|stupid|worthless|useless|pathetic)\b", t):
            found.append("labeling")
        if re.search(r"\b(should|must|have to|supposed to|ought to)\b", t):
            found.append("should statements")
        if re.search(r"\b(everyone|nobody|no one|they all|people think|they think|everyone knows)\b", t):
            found.append("mind reading")
        if re.search(r"\b(will never|won'?t work|can'?t do|it'?s impossible|nothing will|hopeless)\b", t):
            found.append("fortune telling")
        if re.search(r"\b(my fault|i caused|because of me|i ruined|i'm the reason)\b", t):
            found.append("personalization")
        if re.search(r"\b(completely|totally|utterly|absolute(ly)?|disaster|catastrophe|terrible|horrible|worst)\b", t):
            found.append("catastrophizing")
        if re.search(r"\b(i feel like (a )?(failure|fraud|fake|burden|problem))\b", t):
            found.append("emotional reasoning")
        return list(dict.fromkeys(found))[:2]  # preserve order, cap at 2

    def _extract_key_themes(self, text: str, entities: List[str]) -> List[str]:
        themes = []
        if any(e in entities for e in ("exams", "studying", "classes")): themes.append("academic pressure")
        if any(e in entities for e in ("internship", "work")):           themes.append("work stress")
        if "relationships" in entities:                                   themes.append("relationships")
        if "sleep" in entities:                                           themes.append("exhaustion")
        if "self_esteem" in entities:                                     themes.append("self-doubt")
        if "anxiety" in entities:                                         themes.append("anxiety")
        if "money" in entities:                                           themes.append("financial stress")
        if "health" in entities:                                          themes.append("physical wellbeing")
        return themes or ["what you're processing"]

    def _journal_insight(
        self,
        text: str,
        emotion: str,
        entities: List[str],
        distortions: List[str],
        themes: List[str],
    ) -> str:
        theme_str = " and ".join(themes[:2])

        distortion_clause = ""
        if "overgeneralization" in distortions:
            distortion_clause = (
                " I also noticed your mind using 'always' or 'never' language — "
                "a very common cognitive pattern when we're overwhelmed that makes temporary situations feel permanent. "
                "It's worth asking: is this actually true every time, or does it just feel that way right now?"
            )
        elif "catastrophizing" in distortions:
            distortion_clause = (
                " Your language suggests your mind is running worst-case scenarios. "
                "This is your threat-detection system working overtime — "
                "it's protecting you, but it's treating possibilities as certainties. "
                "The worst case is almost never the most likely case."
            )
        elif "labeling" in distortions:
            distortion_clause = (
                " I noticed you may be applying global labels to yourself — words like 'failure' or 'useless'. "
                "These are almost always inaccurate: you're a person who had a hard experience, "
                "not a fixed category. That distinction matters enormously."
            )
        elif "should statements" in distortions:
            distortion_clause = (
                " There are 'should' and 'must' statements in what you wrote. "
                "These create invisible pressure by holding you to rigid standards — "
                "often ones you wouldn't hold anyone else to. "
                "Where did this 'should' come from, and is it actually yours?"
            )
        elif "fortune telling" in distortions:
            distortion_clause = (
                " I noticed some future-predicting thoughts — your mind is treating uncertain possibilities as facts. "
                "This kind of thinking amplifies anxiety because it skips over the evidence "
                "and goes straight to the conclusion. What's the actual evidence for that prediction?"
            )
        elif "personalization" in distortions:
            distortion_clause = (
                " There's a pattern of taking responsibility for things that may not be yours to carry. "
                "Personalizing — assuming outcomes are caused by you — "
                "is a sign of someone who cares deeply, but it often assigns more control than you actually had."
            )
        elif "emotional reasoning" in distortions:
            distortion_clause = (
                " I noticed some emotional reasoning — using how you feel as proof of what's true. "
                "'I feel like a failure' is very different from 'I am a failure'. "
                "Feelings are real, but they're not always accurate reports about reality."
            )

        templates = {
            "stressed": (
                f"Reading your entry, I can see a mind that's carrying a genuinely heavy load around {theme_str}. "
                f"This level of stress almost always points to someone who cares deeply about the outcome — "
                f"your nervous system isn't malfunctioning, it's responding to real demands. "
                f"The key question is: which part of this is actually in your control right now, and which part are you borrowing worry for?"
                f"{distortion_clause}"
            ),
            "anxious": (
                f"Your entry reveals an anxious mind doing what anxious minds do — "
                f"scanning ahead for threats around {theme_str} to prevent them before they happen. "
                f"This is your brain trying to protect you. The problem is, it can't distinguish between a real danger and an imagined one — "
                f"so it treats every 'what if' as an emergency. "
                f"The physical sensations you're feeling are the result of that alarm system firing, not evidence that the threat is real."
                f"{distortion_clause}"
            ),
            "sad": (
                f"There's real grief in what you wrote about {theme_str}. "
                f"Sadness almost always signals that something meaningful to you has been lost, changed, or feels out of reach. "
                f"That pain deserves to be felt, not bypassed — it's your emotional system processing something that actually mattered. "
                f"The goal isn't to feel better immediately; it's to understand what you're mourning and what that reveals about what you value."
                f"{distortion_clause}"
            ),
            "angry": (
                f"The frustration in your entry about {theme_str} is communicating something important. "
                f"Anger is almost never just anger — beneath it is usually a violated expectation, an unmet need, or something that felt unfair or disrespectful. "
                f"Your anger is telling you that your values or boundaries were crossed. "
                f"The therapeutic question is: what specifically was the unmet need? Naming that is what moves things forward."
                f"{distortion_clause}"
            ),
            "tired": (
                f"What you wrote makes it clear that you've been running well past your capacity around {theme_str}. "
                f"This kind of exhaustion isn't weakness or laziness — it's what happens when a person has been outputting more than they've been receiving for too long. "
                f"Your body and mind aren't failing you; they're sending an invoice for ignored self-care. "
                f"The hard truth is that no amount of willpower recovers from this — only genuine rest does."
                f"{distortion_clause}"
            ),
            "lost": (
                f"Reading your entry, you seem to be between versions of yourself around {theme_str} — "
                f"uncertain of which direction is yours. "
                f"This feeling of being 'lost' is often the uncomfortable space between who you were and who you're becoming. "
                f"It's disorienting, but it's not empty — there's something being renegotiated inside you, "
                f"and the confusion is usually a signal that old answers no longer fit."
                f"{distortion_clause}"
            ),
            "hopeless": (
                f"Your entry carries the weight of someone who has been trying hard around {theme_str} "
                f"and hasn't yet seen the results they were hoping for. "
                f"Hopelessness almost always arrives when sustained effort hasn't yet produced visible change — "
                f"not when things are actually impossible. "
                f"The brain at this point is predicting based on past data, not future potential. "
                f"What would it mean if you were actually closer than you think?"
                f"{distortion_clause}"
            ),
            "neutral": (
                f"Your entry reflects a period of processing around {theme_str}. "
                f"Sometimes the most significant emotional work happens in this quieter register — "
                f"not in peaks of distress, but in the steady undercurrent of thoughts we don't usually examine. "
                f"Reading between the lines, it seems like something is being weighed, even if it hasn't fully surfaced yet."
                f"{distortion_clause}"
            ),
        }
        return templates.get(emotion, templates["neutral"])

    def _journal_suggestions(
        self,
        emotion: str,
        entities: List[str],
        distortions: List[str],
    ) -> List[str]:
        pool = self._TECHNIQUES.get(emotion, self._TECHNIQUES["neutral"])
        technique = random.choice(pool)

        distortion_suggestion = None
        if "overgeneralization" in distortions or "fortune telling" in distortions or "catastrophizing" in distortions:
            distortion_suggestion = (
                "**Thought Record (CBT):** Write the specific thought, then answer: "
                "What evidence do I have FOR this? What evidence AGAINST it? "
                "What would I tell a close friend who had this thought? "
                "Re-rate how true it feels after writing it out — the number almost always drops."
            )
        elif "labeling" in distortions or "emotional reasoning" in distortions:
            distortion_suggestion = (
                "**Cognitive Defusion (ACT):** Instead of 'I am a failure', say out loud: "
                "'I notice I'm having the thought that I am a failure.' "
                "This tiny shift creates distance — the thought becomes something you observe, not something you are."
            )
        elif "should statements" in distortions:
            distortion_suggestion = (
                "**'Should' Audit:** Write down every 'should' or 'must' in your thinking today. "
                "For each one, ask: where did this rule come from? Is it actually mine? "
                "What would I replace it with if I could choose freely? "
                "'I choose to' is very different from 'I should'."
            )
        elif "personalization" in distortions:
            distortion_suggestion = (
                "**Responsibility Pie:** Draw a pie chart of everything that contributed to the outcome you're blaming yourself for. "
                "Include external factors, other people, timing, context. "
                "Your slice is almost always smaller than it feels — this exercise makes that visible."
            )

        entity_suggestion = None
        if any(e in entities for e in ("exams", "studying")):
            entity_suggestion = "**For exam stress specifically:** Switch from re-reading to active recall — close the book and test yourself. Testing beats re-reading by 50% for retention and also reduces exam anxiety by building actual confidence, not just familiarity."
        elif any(e in entities for e in ("internship", "work")):
            entity_suggestion = "**For work pressure:** Start each day by identifying your ONE key deliverable. Most work stress comes from ambiguity, not workload. Knowing your single most important task eliminates the background hum of 'what should I be doing?'"
        elif "relationships" in entities:
            entity_suggestion = "**For relationship stress:** Before your next conversation with this person, write out: what do I actually need here? Not what I want them to do differently — what do I need? Conversations that start from needs rather than complaints produce very different outcomes."
        elif "sleep" in entities:
            entity_suggestion = "**For sleep:** A consistent wake time — even on weekends — is the single most powerful intervention for sleep quality. Not bedtime. Wake time. Your circadian rhythm anchors to when you wake up, not when you lie down."

        suggestions = [f"**{technique['name']}** ({technique['frame']}): {technique['steps']}"]
        if distortion_suggestion:
            suggestions.append(distortion_suggestion)
        elif entity_suggestion:
            suggestions.append(entity_suggestion)
        if entity_suggestion and distortion_suggestion:
            suggestions.append(entity_suggestion)

        return suggestions[:3]

    def _journal_affirmation(self, emotion: str, entities: List[str]) -> str:
        affirmations = {
            "stressed":  "The fact that you're feeling this much means you're in something that matters. Your stress is not a defect — it's a signal from a person who gives a damn.",
            "anxious":   "Your anxiety is not your enemy. It's an overprotective guard that needs to be shown you're safe, not silenced. You've survived every anxious moment so far.",
            "sad":       "Letting yourself feel sadness is one of the most courageous things a person can do. You're not weak for hurting — you're human for caring.",
            "angry":     "Your anger is valid information. It's pointing at something that matters to you. Feeling it doesn't make you a bad person — it makes you someone with values.",
            "tired":     "Exhaustion is not a character flaw. You've been carrying a lot, probably for longer than you've acknowledged. You're allowed to need rest — that's not giving up.",
            "lost":      "Feeling uncertain about direction isn't the same as having no direction. Sometimes we have to stop moving to figure out where we actually want to go.",
            "hopeless":  "You wrote this entry. That means something in you still believes it's worth saying. That part of you is right.",
            "neutral":   "Showing up to process your inner life — even on ordinary days — is an act of self-respect. Not every entry needs to be a breakthrough.",
        }
        return affirmations.get(emotion, affirmations["neutral"])


# ── Singleton ─────────────────────────────────────────────────────────────────
custom_ai = CustomAIEngine()
