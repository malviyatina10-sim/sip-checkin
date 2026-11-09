"""AI core for the SIP Check-in MVP: classify -> gate -> answer -> output check.

Not investment advice. The assistant explains situations and options; it never
recommends funds or stocks and never uses fear / FOMO / urgency language.
"""
import json
import os
import re
import time

try:
    import streamlit as st
except Exception:  # allows running eval from the command line
    st = None

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"
BACKUP_MODELS = ["gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]

OFFICIAL_LINKS = {
    "AMFI Investor Corner": "https://www.amfiindia.com/investor-corner",
    "SEBI Investor Website": "https://investor.sebi.gov.in/",
    "SEBI-registered Investment Advisers (list)": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13",
}

INTENTS = {
    "cash_tight": "Money is short this month / SIP date comes before salary / unexpected expense",
    "payment_failed": "Autopay, mandate or instalment failed or is pending",
    "bounce_charge": "Bank or platform charged a penalty for a failed debit",
    "value_down": "Portfolio value or returns are down / negative / lower than expected",
    "metric_confusion": "Does not understand XIRR, NAV, units, absolute returns, current value",
    "change_sip": "Wants to know how to skip, pause, change date, reduce, cancel or restart a SIP",
    "fund_advice": "Asks which fund/stock to buy, sell, switch to, or whether a specific fund is good",
    "unclear": "Off-topic, too vague, or outside SIP continuation (tax filing, loans, trading, etc.)",
}

KNOWLEDGE = """
FACTS YOU MAY USE (general, platform rules vary - always tell the user to confirm in their own app):
- Missing one SIP instalment usually does not cancel the SIP; the next instalment is attempted on the next due date.
- Investment platforms usually do not charge for a missed SIP, but the BANK may charge a fee for a failed auto-debit / NACH / mandate (often a few hundred rupees; it depends on the bank).
- Some SIPs registered directly with the fund house (AMC SIPs) are cancelled automatically after several consecutive failed instalments (often 3). Check the SIP details in the app.
- Common options: SKIP one instalment (the SIP continues after); PAUSE for a set number of months (resumes automatically);
  CHANGE THE SIP DATE (e.g. to a few days after salary is credited); REDUCE the amount (sometimes means starting a new SIP);
  CANCEL (stops future instalments - units already bought stay invested); RESTART later by starting a new SIP.
- Not every app offers every option. Tell the user to look in the SIP's settings (often 'Manage', 'Edit', 'Skip', 'Pause').
- Early in a SIP the total value moves with the fund's NAV; with only a few instalments, a small market move shows as a large % change.
- Absolute return = (current value - amount invested) / amount invested. It ignores time.
- XIRR = an annualised return that accounts for the date of each instalment. For investments under about a year it can look extreme (very high or very low), so many apps show absolute return instead.
- NAV = price of one unit of the fund. Units = how many units you hold. Current value = units x latest NAV.
- Withdrawing (redeeming) units may attract an exit load if done within the fund's exit-load period, and may have tax implications. Details are in the fund's scheme documents.
"""

CLASSIFY_PROMPT = """You route messages from first-time SIP investors in India.
Pick ONE intent from this list:
{intents}

Return JSON: {{"intent": "<key>", "confidence": <0.0-1.0>, "sip_date": <day number or null>, "salary_date": <day number or null>, "summary": "<one short line restating the user's situation>"}}
Rules: if the message asks for any specific fund/stock pick, buy/sell/switch recommendation, or 'is fund X good', intent MUST be fund_advice even if other things are mentioned.
Use low confidence (<0.6) if the message is vague.

User message: <<<{msg}>>>"""

ANSWER_PROMPT = """You are "SIP Check-in", a calm, plain-language helper inside an investing app, for first-time SIP investors in India.
Your job: help the person understand what is happening and what their options are, so THEY can decide. You do NOT decide for them.

HARD RULES:
- Never name, recommend or rate any fund, AMC, stock or category to buy/sell/switch. Never say a fund is good or bad.
- Never use fear, FOMO or urgency (no "act now", "don't miss", "you'll regret", "before it's too late", "you will lose").
- Never promise or predict returns. Never say "you should continue" or "you should stop" - present options neutrally, including stopping.
- Use only the facts below; if something depends on their app/bank, say "check in your app" rather than guessing.
- Simple English, short sentences, no jargon without a one-line explanation. Max ~180 words total.

{knowledge}

Situation type: {intent}
{date_hint}
User message: <<<{msg}>>>

Return JSON:
{{"what_is_happening": "<2-3 sentences explaining their situation in plain words>",
  "options": [{{"option": "<short name>", "what_it_means": "<1 sentence>", "worth_knowing": "<1 sentence trade-off>"}}],  (2 to 4 options)
  "where_to_look": "<1 sentence on where in the app or what to check>",
  "confidence": <0.0-1.0 how sure you are this answer fits their situation>}}"""

# ---------- Output safety check (the visible eval gate) ----------
FUND_WORDS = r"(hdfc|sbi|icici|axis|nippon|kotak|parag parikh|ppfas|mirae|quant|motilal|tata|uti|aditya birla|dsp|franklin|canara robeco|bandhan|edelweiss|invesco|hsbc|nifty ?50 index fund|small ?cap fund|mid ?cap fund|large ?cap fund|elss fund)"
CHECKS = {
    "No fund or stock recommendation": re.compile(
        r"(\b(buy|sell|switch to|invest in|go for|choose)\b.{0,40}\b(fund|stock|share)s?\b)|" + FUND_WORDS, re.I),
    "No fear / FOMO / urgency": re.compile(
        r"(act now|hurry|don'?t miss|last chance|before it'?s too late|you will lose|you'?ll lose|regret|crash is coming)", re.I),
    "No return promises": re.compile(r"(guarantee|assured return|will definitely|risk[- ]free|sure shot)", re.I),
    "Doesn't decide for the user": re.compile(r"(you should (definitely )?(continue|stop|keep|cancel))|(you must (continue|stop))", re.I),
}


def _key():
    if st is not None:
        try:
            return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    return os.getenv("GEMINI_API_KEY")


def _model():
    if st is not None:
        try:
            return st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
        except Exception:
            pass
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


_CLIENTS = {}


def _client():
    """Keep one client alive (a throwaway client gets closed mid-request)."""
    k = _key()
    if not k:
        raise RuntimeError("No GEMINI_API_KEY configured")
    if k not in _CLIENTS:
        _CLIENTS[k] = genai.Client(api_key=k)
    return _CLIENTS[k]


def _secret(name, default=None):
    if st is not None:
        try:
            return st.secrets[name]
        except Exception:
            pass
    return os.getenv(name, default)


GROQ_BACKUPS = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]


def _ask_groq(prompt, key, temperature):
    import requests
    first = _secret("GROQ_MODEL", GROQ_BACKUPS[0])
    last_err = None
    for m in [first] + [x for x in GROQ_BACKUPS if x != first]:
        for attempt in range(2):
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": m, "temperature": temperature, "response_format": {"type": "json_object"},
                      "messages": [{"role": "system", "content": "Reply with one valid JSON object only."},
                                   {"role": "user", "content": prompt}]},
                timeout=40,
            )
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"].strip()
                try:
                    return json.loads(text[text.find("{"): text.rfind("}") + 1])
                except json.JSONDecodeError as e:
                    last_err = e
                    continue
            last_err = RuntimeError(f"Groq {r.status_code}: {r.text[:200]}")
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2)
                continue
            if r.status_code in (400, 404) and ("model" in r.text.lower()):
                break  # model not available - try next
            raise last_err
    raise last_err


def ask_json(prompt, temperature=0.2):
    # Provider order: Groq (if GROQ_API_KEY set) -> Claude (if ANTHROPIC_API_KEY set) -> Gemini.
    gkey = _secret("GROQ_API_KEY")
    if gkey:
        return _ask_groq(prompt, gkey, temperature)
    akey = _secret("ANTHROPIC_API_KEY")
    if akey:
        import anthropic
        msg = anthropic.Anthropic(api_key=akey).messages.create(
            model=_secret("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1200,
            system="Reply with a single valid JSON object only, no other text.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        return json.loads(text[text.find("{"): text.rfind("}") + 1])
    client = _client()
    # Try the chosen model first, then lighter backups if Google says it is busy (503) or rate-limited (429).
    models = [_model()] + [m for m in BACKUP_MODELS if m != _model()]
    last_err = None
    for m in models:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=m, contents=prompt,
                    config=types.GenerateContentConfig(temperature=temperature, response_mime_type="application/json"),
                )
                text = resp.text.strip()
                text = text[text.find("{"): text.rfind("}") + 1] if "{" in text else text
                return json.loads(text)
            except json.JSONDecodeError as e:
                last_err = e
            except Exception as e:
                last_err = e
                msg = str(e)
                if any(c in msg for c in ("503", "UNAVAILABLE", "overloaded", "429", "RESOURCE_EXHAUSTED")):
                    time.sleep(1.5)
                    continue
                if any(c in msg for c in ("404", "NOT_FOUND")):
                    break  # model name not available - try next model
                raise
    raise last_err


def classify(msg):
    intents = "\n".join(f"- {k}: {v}" for k, v in INTENTS.items())
    out = ask_json(CLASSIFY_PROMPT.format(intents=intents, msg=msg), temperature=0)
    if out.get("intent") not in INTENTS:
        out["intent"] = "unclear"
    out["confidence"] = float(out.get("confidence") or 0)
    # rule backstop: explicit fund/stock-pick requests always route to decline, whatever the model said
    if out["intent"] != "fund_advice" and re.search(ADVICE_ASK, msg, re.I):
        out["intent"], out["rule_override"] = "fund_advice", True
    return out


ADVICE_ASK = (r"((which|best|good|suggest|recommend|top)\b.{0,30}\b(funds?|stocks?|shares?))|"
              r"(\b(switch|buy|sell)\b.{0,40}\b(funds?|units|stocks?|shares?)\b)|(\b(tip|tips)\b.{0,20}(trading|stock|intraday))|"
              r"(intraday.{0,20}\btips?\b)")


def date_hint(sip_date, salary_date):
    """Deterministic (non-AI) helper: spots a SIP date that falls before salary day."""
    try:
        s, p = int(sip_date), int(salary_date)
    except (TypeError, ValueError):
        return None
    if 1 <= s <= 31 and 1 <= p <= 31 and s < p:
        new = min(p + 3, 28)
        return (f"The SIP date ({s}) comes {p - s} days BEFORE salary day ({p}). "
                f"A SIP date around the {new}th would fall after salary is credited.")
    return None


def safety_check(answer):
    blob = json.dumps(answer, ensure_ascii=False)
    return {name: (pat.search(blob) is None) for name, pat in CHECKS.items()}


def check_in(msg, sip_date=None, salary_date=None):
    """Full pipeline. Returns dict with route = answer | decline | fallback."""
    c = classify(msg)
    sip_date = sip_date or c.get("sip_date")
    salary_date = salary_date or c.get("salary_date")
    hint = date_hint(sip_date, salary_date)
    result = {"classification": c, "date_hint": hint}

    if c["intent"] == "fund_advice":
        result["route"] = "decline"
        return result
    if c["intent"] == "unclear" or c["confidence"] < 0.6:
        result["route"] = "fallback"
        result["reason"] = "I'm not confident I understood your situation."
        return result

    ans = ask_json(ANSWER_PROMPT.format(knowledge=KNOWLEDGE, intent=INTENTS[c["intent"]],
                                        date_hint=("Date check: " + hint) if hint else "", msg=msg), temperature=0.3)
    checks = safety_check(ans)
    result.update(answer=ans, checks=checks)
    if not all(checks.values()):
        result["route"] = "fallback"
        result["reason"] = "My draft answer did not pass the safety check, so I'm not showing it."
    elif float(ans.get("confidence") or 0) < 0.5:
        result["route"] = "fallback"
        result["reason"] = "I'm not sure my answer fits your situation."
    else:
        result["route"] = "answer"
    return result


# ---------- Discovery engine: live tagging with the same taxonomy ----------
TAG_PROMPT = """You tag Indian investor feedback about SIPs for user research. Only tag what the text says.
Return JSON: {{"relevant": true/false (about someone's SIP / mutual fund experience),
"action": one of [continuing, missed (involuntary), paused, reduced / withdrew, stopped / left, considering stopping, starting / setup, no action stated],
"main_reason": one of {reasons},
"other_reasons": [up to 2 more from the same list],
"severity": 1 (annoyance) | 2 (affects investing) | 3 (made them stop/pause/leave),
"unmet_need": "<max 12 words>",
"evidence_quote": "<max 20 words copied exactly from the text>"}}
Text: <<<{text}>>>"""


def tag_review(text, reasons):
    return ask_json(TAG_PROMPT.format(text=text[:2000], reasons=json.dumps(reasons)), temperature=0)
