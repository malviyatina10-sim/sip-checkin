import json
import time

import pandas as pd
import streamlit as st

import os

import core
from taxonomy import TRIGGERS


def data_path(name):
    """Works whether the CSVs sit in data/ or next to app.py."""
    p = os.path.join("data", name)
    return p if os.path.exists(p) else name

st.set_page_config(page_title="SIP Check-in | Groww concept", page_icon="🧭", layout="centered")

DISCLAIMER = ("**Not investment advice.** SIP Check-in explains your situation and your options in plain language. "
              "It never recommends funds or stocks. For personal advice, talk to a SEBI-registered investment adviser.")

tab_mvp, tab_engine, tab_quality, tab_about = st.tabs(
    ["🧭 SIP Check-in (MVP)", "🔎 Discovery Engine", "✅ Quality & Evals", "ℹ️ About"])

# =====================================================================================
# TAB 1 - MVP
# =====================================================================================
with tab_mvp:
    st.title("SIP Check-in")
    st.caption("A concept for Groww: a calm helper for the moment a SIP feels hard to continue.")
    st.info(DISCLAIMER, icon="ℹ️")

    st.markdown("**What's going on with your SIP?** Describe it in your own words, or tap an example.")
    examples = [
        "My SIP date is the 1st but salary comes on the 7th",
        "Autopay failed and I got charged by my bank",
        "I started 3 months ago and it's showing negative",
        "What is XIRR? My returns % says something else",
        "Unexpected expense this month, what happens if I miss my SIP?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex{i}", width="stretch"):
            st.session_state["msg"] = ex

    msg = st.text_area("Your situation", key="msg", height=90,
                       placeholder="e.g. Rent and a family expense came together this month and my SIP is due on the 5th…")
    with st.expander("Optional: add your dates (helps spot a date clash). No account details needed."):
        c1, c2 = st.columns(2)
        sip_date = c1.number_input("SIP debit day of month", 0, 31, 0, help="0 = skip")
        salary_date = c2.number_input("Salary credit day of month", 0, 31, 0, help="0 = skip")
    st.caption("Please don't enter PAN, account numbers or screenshots.")

    if st.button("Check in", type="primary", disabled=not msg.strip()):
        with st.spinner("Reading your situation…"):
            try:
                res = core.check_in(msg, sip_date or None, salary_date or None)
            except Exception as e:
                res = {"route": "error", "error": str(e)}
        st.session_state["last"] = res

    res = st.session_state.get("last")
    if res:
        st.divider()
        route = res["route"]
        if res.get("date_hint"):
            st.warning("📅 " + res["date_hint"])

        if route == "answer":
            a = res["answer"]
            st.subheader("What's happening")
            st.write(a.get("what_is_happening", ""))
            st.subheader("Your options")
            for o in a.get("options", []):
                with st.container(border=True):
                    st.markdown(f"**{o.get('option', '')}**")
                    st.write(o.get("what_it_means", ""))
                    st.caption("Worth knowing: " + o.get("worth_knowing", ""))
            st.markdown("**Where to look:** " + a.get("where_to_look", ""))
            st.caption("The choice is yours, including stopping. This is general information, not advice.")

        elif route == "decline":
            st.subheader("I can't help pick or rate funds")
            st.write("Choosing, switching or rating specific funds or stocks is investment advice, which SIP Check-in "
                     "doesn't give. If you'd like personal advice, a SEBI-registered investment adviser can help. "
                     "I can still explain things like missed instalments, XIRR, or how to skip / pause / change a SIP.")
            st.link_button("Find a SEBI-registered adviser", core.OFFICIAL_LINKS["SEBI-registered Investment Advisers (list)"])

        elif route == "fallback":
            st.subheader("I'm not sure about this one")
            st.write(res.get("reason", "") + " Rather than guess, here are official sources:")
            for name, url in core.OFFICIAL_LINKS.items():
                st.markdown(f"- [{name}]({url})")

        else:
            st.error("The AI service isn't reachable right now, so nothing was generated. "
                     "Official sources: [AMFI](https://www.amfiindia.com/investor-corner) · "
                     "[SEBI Investor](https://investor.sebi.gov.in/)")
            with st.expander("Technical detail (for the builder)"):
                st.code(res.get("error", "unknown"))

        # visible quality gate
        with st.expander("🛡️ Quality check for this answer", expanded=(route != "answer")):
            c = res.get("classification", {})
            st.markdown(f"- Understood as: **{c.get('intent', '-')}** (confidence {c.get('confidence', 0):.2f})"
                        + (" · rule override: fund-advice request" if c.get("rule_override") else ""))
            st.markdown(f"- Route taken: **{route}**  (answer · decline · fallback)")
            for name, ok in (res.get("checks") or {}).items():
                st.markdown(f"- {'✅' if ok else '❌'} {name}")
            if route != "answer" and not res.get("checks"):
                st.markdown("- Answer not generated: the request was routed away before drafting.")

        st.markdown("**Was this helpful?**")
        f1, f2, _ = st.columns([1, 1, 4])
        if f1.button("👍 Yes"):
            st.toast("Thanks for the feedback!")
        if f2.button("👎 No"):
            st.toast("Thanks, noted for the next iteration.")

# =====================================================================================
# TAB 2 - DISCOVERY ENGINE
# =====================================================================================
with tab_engine:
    st.title("Discovery Engine")
    st.caption("Why do first-time SIP investors' SIPs break? An AI pass over public reviews and forum posts.")

    vol = pd.read_csv(data_path("volume_by_source.csv"))
    df = pd.read_csv(data_path("tagged_sample.csv"))
    rel = df[df.relevant == 1].copy()
    rel["is_break"] = rel.action.isin(list("MPRSK"))

    m1, m2, m3 = st.columns(3)
    m1.metric("Items collected", f"{int(vol.collected.sum()):,}")
    m2.metric("SIP-related", f"{int(vol.sip_related.sum()):,}")
    m3.metric("AI-tagged sample (relevant)", f"{len(df)} ({len(rel)})")

    with st.expander("Pipeline: how it works"):
        st.markdown("""
1. **Collect:** Python scraper → Play Store (Groww, INDmoney, Zerodha Coin), App Store (Groww), TradingQ&A forum. Reddit was attempted but blocked (HTTP 403).
2. **Filter:** keyword filter keeps SIP / mandate / autopay / XIRR / pause talk.
3. **Sample:** 300 items stratified by source.
4. **Tag (AI):** each item tagged with a fixed taxonomy: SIP action, reasons (up to 3), severity 1–3.
5. **Score:** opportunity = how often × how often it coincides with a broken SIP × severity.
6. **Validate:** 20-item golden set labelled by hand; agreement reported in the Evidence Log.
""")
        st.dataframe(vol, hide_index=True, width="stretch")

    long = rel.assign(t=rel.triggers.fillna("").str.split("|")).explode("t")
    long = long[long.t != ""]
    opp = long.groupby("t").agg(mentions=("sid", "nunique"), breaks=("is_break", "sum"),
                                severity=("severity", "mean")).reset_index()
    opp["reason"] = opp.t.map(TRIGGERS)
    opp["% of items"] = (opp.mentions / len(rel) * 100).round(1)
    opp["% linked to a broken SIP"] = (opp.breaks / opp.mentions * 100).round(0)
    opp["avg severity"] = opp.severity.round(2)
    opp["opportunity score"] = (opp["% of items"] / 100 * opp["% linked to a broken SIP"] / 100
                                * opp.severity / 3 * 100).round(1)
    opp = opp.sort_values("opportunity score", ascending=False)

    st.subheader("Ranked opportunity areas")
    st.bar_chart(opp.set_index("reason")["opportunity score"], horizontal=True)
    st.dataframe(opp[["reason", "% of items", "% linked to a broken SIP", "avg severity", "opportunity score"]],
                 hide_index=True, width="stretch")

    st.subheader("What people did with their SIP")
    st.bar_chart(rel.action_label.value_counts(), horizontal=True)

    st.subheader("Read the evidence")
    pick = st.selectbox("Show items tagged with:", opp.reason.tolist())
    code = {v: k for k, v in TRIGGERS.items()}[pick]
    sub = rel[rel.triggers.fillna("").str.split("|").apply(lambda x: code in x)].sort_values("severity", ascending=False)
    for _, r in sub.head(8).iterrows():
        st.markdown(f"> {r.text[:350]}{'…' if len(r.text) > 350 else ''}  \n"
                    f"<small>{r.source} · action: {r.action_label} · severity {r.severity}</small>", unsafe_allow_html=True)

    st.subheader("Try it: tag a new review")
    txt = st.text_area("Paste any app review or forum post about SIPs", key="tagtxt")
    if st.button("Tag with AI", disabled=not txt.strip()):
        with st.spinner("Tagging…"):
            try:
                st.json(core.tag_review(txt, list(TRIGGERS.values())))
            except Exception as e:
                st.error(f"AI service unavailable: {e}")

# =====================================================================================
# TAB 3 - QUALITY
# =====================================================================================
with tab_quality:
    st.title("Quality & Evals")
    st.markdown("""
**The eval gate (every answer):**
1. **Classify:** the AI routes the message to a situation type, with a confidence score. A rule backstop catches fund-pick requests.
2. **Route:** fund or stock advice → **decline**; unclear, off-topic or low confidence → **fallback** to official sources.
3. **Draft:** the AI explains using a fixed fact sheet only.
4. **Check:** the draft is scanned for fund names or recommendations, urgency or fear words, return promises and "you should stop/continue". Any failure → **fallback**.
""")
    g = pd.read_csv("golden_queries.csv")
    st.subheader(f"Golden set: {len(g)} hand-labelled test questions")
    st.dataframe(g, hide_index=True, width="stretch")

    def route_ok(expected, got):
        return got == expected or (expected == "fallback" and got == "decline")

    if st.button("▶ Run the golden-set evaluation (about 2 min)"):
        rows, bar = [], st.progress(0.0)
        for i, r in g.iterrows():
            try:
                out = core.check_in(r.query)
                got, intent = out["route"], out["classification"]["intent"]
                checks = all((out.get("checks") or {"n/a": True}).values())
            except Exception as e:
                got, intent, checks = "error", str(e)[:40], False
            rows.append(dict(id=r.id, query=r.query, expected=r.expected_route, got=got,
                             route_pass=route_ok(r.expected_route, got), intent_expected=r.expected_intent,
                             intent_got=intent, intent_pass=(intent == r.expected_intent), safety_pass=checks))
            bar.progress((i + 1) / len(g))
            time.sleep(4)  # stay inside free-tier rate limits
        res = pd.DataFrame(rows)
        st.session_state["eval"] = res

    res = st.session_state.get("eval")
    if res is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Correct route", f"{res.route_pass.mean() * 100:.0f}%")
        c2.metric("Correct situation type", f"{res.intent_pass.mean() * 100:.0f}%")
        c3.metric("Passed safety check", f"{res.safety_pass.mean() * 100:.0f}%")
        st.metric("Unsafe answers shown (fund-advice question answered)",
                  int(((res.expected == "decline") & (res.got == "answer")).sum()))
        st.dataframe(res, hide_index=True, width="stretch")
        st.download_button("Download results CSV", res.to_csv(index=False), "eval_results.csv")

# =====================================================================================
# TAB 4 - ABOUT
# =====================================================================================
with tab_about:
    st.title("About this prototype")
    st.markdown("""
**Problem.** First-time salaried investors rarely drop a SIP because of the market. It usually breaks around the
**debit date**: the money isn't in the account yet, the mandate fails, the bank charges a bounce fee, and the only
easy move in the app is *Cancel*. People then turn to Google, friends or ChatGPT for help.

**What SIP Check-in does.** At that moment it explains what is happening and lays out the options (skip, pause,
move the date, reduce, cancel, restart) with the trade-offs. The user decides.

**Where AI earns its place.** People describe their situation in messy, emotional words ("salary late, rent due,
charged ₹295, should I quit?"). A static FAQ makes them find the right article and work out how it applies to them.
The AI reads the situation, picks the relevant facts and explains them in their context. A plain rule (not AI)
handles the date-clash maths.

**Guardrails.** No fund or stock advice, no fear, FOMO or urgency, no return promises, and stopping is shown as a valid
option. If unsure → official sources (AMFI, SEBI).

*Student project concept. Not affiliated with Groww. Not investment advice.*
""")
