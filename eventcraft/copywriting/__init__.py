"""Fact-only Chinese/English campaign copy; no invented claims."""

from ..schema import Event, facts


def campaign(event: Event) -> dict[str, str]:
    f = facts(event)
    en = event.language == "en"
    labels = ["When", "Where", "Registration", "Fee", "Organizer"] if en else ["时间", "地点", "报名", "费用", "主办方"]
    rows = [f"{label}：{f[key]}" for label, key in zip(labels, ["when", "where", "registration", "fee", "organizer"], strict=True) if f[key]]
    if event.deadline:
        rows.append(("Deadline: " if en else "报名截止：") + event.deadline)
    if event.contact:
        rows.append(("Contact: " if en else "联系方式：") + event.contact)
    body = "\n".join(rows)
    highlights = "\n".join("- " + h for h in event.highlights)
    speakers = (("Speakers: " if en else "主讲人：") + "、".join(event.speakers) + "\n") if event.speakers else ""
    demo = "DEMO · Fictional event\n" if event.demo and en else "DEMO · 虚构活动示例\n" if event.demo else ""
    short_title = event.title if len(event.title) <= 90 else event.title[:89] + "…"
    greeting = event.recipient or ("Dear guest" if en else "尊敬的来宾")
    return {
        "short.txt": demo + f"{short_title}\n{f['when']}\n{f['where']}\n{f['registration']}\n",
        "social.md": demo + f"# {event.title}\n\n{event.subtitle}\n\n{highlights}\n\n{speakers}{body}\n",
        "formal.md": demo + ("# Event notice\n\n" if en else "# 活动通知\n\n") + f"{event.title}\n\n{event.subtitle}\n\n{speakers}{body}\n\n{highlights}\n",
        "invitation.txt": demo + f"{greeting}：\n\n" + (f"You are invited to {event.title}.\n\n" if en else f"诚邀您参加「{event.title}」。\n\n") + body + "\n\n" + ("We look forward to seeing you.\n" if en else "期待与您相见。\n"),
    }
