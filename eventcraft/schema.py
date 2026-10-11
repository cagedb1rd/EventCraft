"""The event is the only source of campaign facts; unknowns remain unknown."""

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .security import valid_url


class Evidence(BaseModel):
    source: str
    excerpt: str = ""
    confidence: float = Field(default=1, ge=0, le=1)
    status: Literal["provided", "extracted", "inferred", "confirmed"] = "provided"


class Brand(BaseModel):
    colors: list[str] = Field(default_factory=list)
    forbidden_colors: list[str] = Field(default_factory=list)
    forbidden_styles: list[str] = Field(default_factory=list)
    high_contrast: bool = False
    preserve_logo: bool = True

    @field_validator("colors", "forbidden_colors")
    @classmethod
    def hex_colors(cls, values: list[str]) -> list[str]:
        import re
        if any(not re.fullmatch(r"#[0-9a-fA-F]{6}", v) for v in values):
            raise ValueError("Brand colors must use #RRGGBB")
        return [v.lower() for v in values]


class Assets(BaseModel):
    logo: str | None = None
    hero_image: str | None = None
    speaker_photo: str | None = None
    qr_image: str | None = None
    style_reference: list[str] = Field(default_factory=list)


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: str = "1.0"
    title: str = Field(default="", max_length=500)
    subtitle: str = Field(default="", max_length=800)
    category: str = "general"
    subtype: str = ""
    start: str | None = None
    end: str | None = None
    timezone: str | None = None
    venue: str | None = Field(default=None, max_length=800)
    online_platform: str | None = None
    venue_mode: Literal["unknown", "online", "indoor", "outdoor", "hybrid"] = "unknown"
    organizer: str | None = None
    audience: list[str] = Field(default_factory=list)
    formality: Literal["unknown", "casual", "professional", "ceremonial"] = "unknown"
    atmosphere: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list, max_length=20)
    speakers: list[str] = Field(default_factory=list, max_length=20)
    teams: list[str] = Field(default_factory=list, max_length=12)
    fee: str | None = None
    registration: str | None = None
    registration_url: str | None = None
    deadline: str | None = None
    contact: str | None = None
    recipient: str | None = None
    language: Literal["zh", "en", "bilingual"] = "zh"
    style: str | None = None
    style_description: str = ""
    brand: Brand = Field(default_factory=Brand)
    assets: Assets = Field(default_factory=Assets)
    sources: dict[str, Evidence] = Field(default_factory=dict)
    confirmed_fields: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    demo: bool = False

    @field_validator("start", "end", "deadline")
    @classmethod
    def iso_datetime(cls, value: str | None) -> str | None:
        if value:
            datetime.fromisoformat(value)
            if "T" not in value and " " not in value:
                raise ValueError("A date needs an explicit time")
        return value

    @field_validator("timezone")
    @classmethod
    def iana_timezone(cls, value: str | None) -> str | None:
        if value:
            try:
                ZoneInfo(value)
            except ZoneInfoNotFoundError as exc:
                raise ValueError("Timezone must be an IANA zone") from exc
        return value


def issues(event: Event) -> list[str]:
    problems = []
    for field, question in {
        "title": "请确认准确活动名称 / Confirm the event title",
        "start": "请提供含年份的日期和准确时间 / Provide date, year and time",
        "timezone": "请确认 IANA 时区 / Confirm the IANA timezone",
    }.items():
        if not getattr(event, field):
            problems.append(question)
    if not (event.venue or event.online_platform):
        problems.append("请提供具体地点或线上平台 / Provide a venue or online platform")
    if not (event.registration or event.registration_url):
        problems.append("请确认报名方式或无需报名 / Confirm registration or no registration")
    if event.registration_url and not valid_url(event.registration_url):
        problems.append("报名链接无效（仅做语法检查，未联网验证） / Invalid registration URL")
    if event.venue_mode == "online" and event.venue and not event.online_platform:
        problems.append("线上模式与实体地点冲突 / Online mode conflicts with physical venue")
    if event.start and event.timezone:
        zone = ZoneInfo(event.timezone)
        start = datetime.fromisoformat(event.start)
        if start.tzinfo:
            if start.utcoffset() != start.astimezone(zone).utcoffset():
                problems.append("日期偏移量与指定时区不一致 / UTC offset conflicts with timezone")
        else:
            aware = start.replace(tzinfo=zone)
            from datetime import timezone
            if aware.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != start:
                problems.append("夏令时跳变导致该时间不存在 / Local time does not exist")
            elif aware.utcoffset() != start.replace(tzinfo=zone, fold=1).utcoffset():
                problems.append("夏令时重复时段需要明确偏移量 / Ambiguous local time requires UTC offset")
        if event.end:
            finish = datetime.fromisoformat(event.end)
            finish = finish if finish.tzinfo else finish.replace(tzinfo=zone)
            start_aware = start if start.tzinfo else start.replace(tzinfo=zone)
            if finish <= start_aware:
                problems.append("结束时间必须晚于开始时间 / End must follow start")
    problems.extend(event.uncertainties)
    return list(dict.fromkeys(problems))


def facts(event: Event) -> dict[str, str]:
    english = event.language == "en"
    date = ""
    if event.start:
        start = datetime.fromisoformat(event.start)
        if start.tzinfo and event.timezone:
            start = start.astimezone(ZoneInfo(event.timezone))
        date = start.strftime("%Y.%m.%d  %H:%M")
        if event.end:
            end = datetime.fromisoformat(event.end)
            if end.tzinfo and event.timezone:
                end = end.astimezone(ZoneInfo(event.timezone))
            date += " – " + end.strftime("%H:%M" if end.date() == start.date() else "%Y.%m.%d %H:%M")
        if event.timezone:
            date += f"  ({event.timezone})"
    return {
        "title": event.title or ("Title pending" if english else "活动名称待确认"),
        "when": date or ("Date pending" if english else "日期时间待确认"),
        "where": " · ".join(filter(None, [event.venue, event.online_platform])) or ("Venue pending" if english else "地点待确认"),
        "registration": event.registration_url or event.registration or ("Registration pending" if english else "报名方式待确认"),
        "fee": event.fee or "",
        "organizer": event.organizer or "",
    }
