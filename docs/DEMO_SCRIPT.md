# GuardianVisa — 3-Minute Demo Script

---

## Recording Checklist

- [ ] Screen resolution set to **1920×1080**
- [ ] Browser zoom at **125%** (Chrome: ⌘ + twice)
- [ ] System font size: Normal — do NOT increase OS font scale (it breaks layouts)
- [ ] GuardianVisa frontend open at `http://localhost:5173` (or live Cloud Run URL)
- [ ] Backend running and responsive (`curl http://localhost:8000/health` returns `{"status":"ok"}`)
- [ ] MongoDB seeded (`make seed` completed successfully)
- [ ] **All other tabs closed** — no accidental notifications
- [ ] Microphone tested — use a headset or external mic, not laptop mic
- [ ] **Do a 30-second practice run** before recording
- [ ] Screen recording software ready (QuickTime, OBS, or Loom)
- [ ] Record at 60fps if possible
- [ ] Silence notifications: macOS → Focus → Do Not Disturb ON

---

## Screen Layout Recommendations

- Use **Chrome** in full-screen mode (F11 or ⌘+Shift+F)
- Keep the browser DevTools **closed**
- Have all three demo inputs pre-typed in a separate text editor — copy/paste during recording to avoid typos
- If showing architecture: open `docs/01_system_architecture.md` rendered in a Markdown preview, or export it as an image beforehand

---

## Pre-Typed Demo Inputs (copy-paste during recording)

**Flow 1 — Visa Hours:**
```
Hi Priya, can you cover extra weekend shifts this Saturday and Sunday? About 4 hours each day so 8 hours total. We're really short-staffed!
```

**Flow 2 — Scam Scanner:**
```
Beautiful 2-bed flat in Manchester city centre, only £400/month! I'm currently overseas so can't show the property. Please send 3 months rent in cash upfront to secure it. Decision needed today!
```

**Flow 3 — Emergency Plan:**
```
I just lost my job at the café. I don't know what to do.
```

---

## Scene-by-Scene Script with Timestamps

---

### [0:00 – 0:15] Opening Hook

**Screen:** GuardianVisa homepage, hero section visible  
**Action:** No clicks — let the UI breathe  

**Narration:**
> "Priya is a student in Manchester on a Tier 4 visa. She can work 20 hours a week. Her manager just texted asking her to cover extra weekend shifts. She has no idea that saying yes would get her deported. GuardianVisa catches that — before she replies."

*Tip: Pause 1 second after "deported." Let it land.*

---

### [0:15 – 0:25] App Introduction

**Screen:** Full app UI — show all three tabs: Visa Guard, Scam Scanner, Emergency Plan  
**Action:** Slowly move mouse across the three tab labels  

**Narration:**
> "GuardianVisa is a proactive AI agent with three protective flows. Not a chatbot — a guardian. Let's start with Flow One."

---

### [0:25 – 0:55] Flow 1 Setup — Visa Hours Guard

**Screen:** Click **"Visa Guard"** tab  
**Action:** Click tab, pause 1 second, then paste the manager's message into the input field  

**Narration:**
> "This is the exact message Priya's manager just sent. She's already working 18 hours this week. The request is for 8 more hours over the weekend."  
> *(paste message)*  
> "She hits submit."  
**Action:** Click the Submit / Analyse button  

**Narration:**
> "The agent calls MongoDB to retrieve Priya's current hours and visa type. It fetches the UKVI rules for Tier 4. It runs the numbers."

*Tip: During the loading spinner, let the narration fill the silence — don't rush.*

---

### [1:00 – 1:30] 🚨 THE WOW MOMENT — RED ALERT Appears

**Screen:** RED RISK ALERT result card fills the screen  
**Action:** Pause. Let the red alert sit on screen for 3 full seconds before speaking.  

**Narration:**
> *(pause — 3 seconds of silence for visual impact)*  
> "Red alert. 18 plus 8 equals 26 hours. Tier 4 limit is 20. Violation confirmed."  
> *(pause 1 second)*  
> "But look — GuardianVisa doesn't just tell her she's in trouble. It hands her a safe reply she can send to her manager right now."

**Action:** Scroll down slowly to show the safe response draft  

**Narration:**
> "One tap to copy. No legal knowledge needed. No panic. Just protection."

*This is the climax of the demo. Speak slowly. The silence before you speak is intentional.*

---

### [1:40 – 2:00] Flow 2 — Scam Scanner (Fast Demo)

**Screen:** Click **"Scam Scanner"** tab  
**Action:** Click tab, immediately paste the housing listing, click submit  

**Narration:**
> "Flow Two — the Scam Scanner. This is a real housing listing circulating on student Facebook groups."  
> *(paste text and submit)*  
> "£400 a month in Manchester city centre. Landlord 'overseas.' Cash upfront. Decide today."

**Screen:** DANGER result with red flags highlighted  

**Narration:**
> "Four red flags. DANGER score. Below-market rent. No property viewing. Cash-only demand. Artificial urgency. Students from overseas are the primary target for this exact scam. GuardianVisa sees it instantly."

*Keep this section brisk — 20 seconds total.*

---

### [2:00 – 2:25] Flow 3 — Emergency Plan (Fast Demo)

**Screen:** Click **"Emergency Plan"** tab  
**Action:** Type (or paste) the emergency message, click submit  

**Narration:**
> "Flow Three. A student just lost their job. They're terrified. They type it in plain English."  
> *(submit)*  
> "GuardianVisa generates a 7-day action plan — university international office, UKCISA helpline, food banks, a draft email to send today. Calm. Structured. Actionable."

**Action:** Scroll through the action plan  

**Narration:**
> "Not a list of links. A plan."

---

### [2:25 – 2:45] Architecture Overview

**Screen:** Switch to architecture diagram (screenshot of `docs/01_system_architecture.md` or a slide)  
**Action:** Point to each layer as you name it  

**Narration:**
> "Under the hood: React frontend on Cloud Run. FastAPI backend, also Cloud Run. Vertex AI Agent with Gemini 1.5 Pro — doing real function calls, not just text generation. MongoDB Atlas via the MongoDB MCP Server — the agent queries the database as a tool, not a retrieval corpus. Four sequential tool calls per visa check. The agent decides the sequence."

*Keep moving — don't linger on the architecture. 20 seconds maximum.*

---

### [2:45 – 2:55] Closing Line

**Screen:** Return to the GuardianVisa homepage hero  
**Action:** Let the tagline fill the screen: **"Not a chatbot. A guardian."**  
**Action:** Slowly zoom the mouse to rest under the tagline  

**Narration:**
> "600,000 international students in the UK alone. Every single one with a visa they could accidentally violate. GuardianVisa gives them something they've never had before — a guardian that's always watching."

*Pause 2 seconds.*

> "Not a chatbot. A guardian."

**Action:** Stop recording.

---

## Narration Script (Word-for-Word)

For ease of reference, the complete narration in order:

1. *"Priya is a student in Manchester on a Tier 4 visa. She can work 20 hours a week. Her manager just texted asking her to cover extra weekend shifts. She has no idea that saying yes would get her deported. GuardianVisa catches that — before she replies."*

2. *"GuardianVisa is a proactive AI agent with three protective flows. Not a chatbot — a guardian. Let's start with Flow One."*

3. *"This is the exact message Priya's manager just sent. She's already working 18 hours this week. The request is for 8 more hours over the weekend. She hits submit."*

4. *"The agent calls MongoDB to retrieve Priya's current hours and visa type. It fetches the UKVI rules for Tier 4. It runs the numbers."*

5. *(3 seconds silence)* *"Red alert. 18 plus 8 equals 26 hours. Tier 4 limit is 20. Violation confirmed."* *(1 second pause)* *"But look — GuardianVisa doesn't just tell her she's in trouble. It hands her a safe reply she can send to her manager right now."*

6. *"One tap to copy. No legal knowledge needed. No panic. Just protection."*

7. *"Flow Two — the Scam Scanner. This is a real housing listing circulating on student Facebook groups. £400 a month in Manchester city centre. Landlord 'overseas.' Cash upfront. Decide today."*

8. *"Four red flags. DANGER score. Below-market rent. No property viewing. Cash-only demand. Artificial urgency. Students from overseas are the primary target for this exact scam. GuardianVisa sees it instantly."*

9. *"Flow Three. A student just lost their job. They're terrified. They type it in plain English. GuardianVisa generates a 7-day action plan — university international office, UKCISA helpline, food banks, a draft email to send today. Calm. Structured. Actionable."*

10. *"Not a list of links. A plan."*

11. *"Under the hood: React frontend on Cloud Run. FastAPI backend, also Cloud Run. Vertex AI Agent with Gemini 1.5 Pro — doing real function calls, not just text generation. MongoDB Atlas via the MongoDB MCP Server — the agent queries the database as a tool, not a retrieval corpus. Four sequential tool calls per visa check. The agent decides the sequence."*

12. *"600,000 international students in the UK alone. Every single one with a visa they could accidentally violate. GuardianVisa gives them something they've never had before — a guardian that's always watching."* *(2 second pause)* *"Not a chatbot. A guardian."*

---

## Post-Recording Checklist

- [ ] Watch the full recording before uploading — check audio levels, no background noise
- [ ] Confirm the RED ALERT moment at ~1:30 is clearly visible on screen
- [ ] Confirm the tagline **"Not a chatbot. A guardian."** is legible at the end
- [ ] Trim dead silence at the start and end (keep ≤ 1 second of lead-in)
- [ ] Export at 1080p minimum — Devpost accepts YouTube, Vimeo, or direct upload
- [ ] Add captions if possible (YouTube auto-captions work, review for accuracy)
- [ ] Upload to YouTube/Vimeo as **Unlisted** and paste the link into the Devpost submission
- [ ] Test the link in an incognito window before submitting
