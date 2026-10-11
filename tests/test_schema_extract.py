import json
from pathlib import Path

import pytest
from docx import Document
from pydantic import ValidationError

from eventcraft.copywriting import campaign
from eventcraft.extractors import extract, parse_text
from eventcraft.schema import Event, facts, issues
from eventcraft.security import MAX_FILE_BYTES, image_uri, local_file, slugify, valid_url


def test_required_and_optional():
    assert len(issues(Event())) == 5
    event = Event(title="a", start="2026-01-01T14:00", timezone="Asia/Shanghai", online_platform="Example", registration="No RSVP")
    assert issues(event) == []
    assert "organizer" not in " ".join(issues(event))


def test_dates_and_timezone(event):
    with pytest.raises(ValidationError):
        Event(start="2026-02-30T10:00")
    with pytest.raises(ValidationError):
        Event(timezone="Mars/Olympus")
    event.end = "2026-10-25T14:00"
    assert any("结束" in s for s in issues(event))
    event.end = "2026-10-27T14:00"
    assert "2026.10.27" in facts(event)["when"]


def test_dst(event):
    event.timezone = "Australia/Sydney"
    event.end = None
    event.start = "2026-10-04T02:30"
    assert any("不存在" in s for s in issues(event))
    event.start = "2026-04-05T02:30"
    assert any("偏移" in s for s in issues(event))
    event.start = "2026-04-05T02:30+11:00"
    assert not issues(event)


def test_offset_conflict(event):
    event.start = "2026-10-26T14:00+00:00"
    assert any("时区不一致" in s for s in issues(event))


def test_extraction_conflicts_and_no_invention():
    result = parse_text("# 校园 AI 分享会\n地点：A\n地点：B\n下个月举办，免费")
    assert result.title == "校园 AI 分享会"
    assert result.fee == "免费"
    assert result.audience == [] and result.organizer is None
    assert len(result.uncertainties) == 2
    assert result.sources["category"].status == "inferred"
    assert result.start is None


def test_labelled_docx_txt_md_json(tmp_path):
    text = "活动名称：示例工坊\n开始时间：2026-11-02T10:30\n时区：Asia/Shanghai\n地点：示例楼\n报名方式：无需报名"
    for suffix in [".txt", ".md"]:
        path = tmp_path / ("event" + suffix)
        path.write_text(text, encoding="utf-8")
        assert extract(path).title == "示例工坊"
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    path = tmp_path / "event.docx"
    doc.save(path)
    event = extract(path)
    assert not issues(event)
    j = tmp_path / "event.json"
    j.write_text(json.dumps(event.model_dump()), encoding="utf-8")
    assert extract(j).start == event.start


def test_copy_single_source_and_omission(event):
    for text in campaign(event).values():
        for field in ["when", "where", "registration"]:
            assert facts(event)[field] in text
        assert event.title in text
    event.organizer = None
    event.fee = None
    event.speakers = []
    event.recipient = None
    result = campaign(event)
    assert "主办方：" not in result["formal.md"]
    assert "费用：" not in result["formal.md"]
    assert "尊敬的来宾" in result["invitation.txt"]
    event.language = "en"
    assert "Dear guest" in campaign(event)["invitation.txt"]
    assert "When：" in campaign(event)["formal.md"]


@pytest.mark.parametrize("url", ["javascript:alert(1)", "https://", "https://user:pass@example.org", "https://example.org/a b", "http://localhost:1"])
def test_invalid_url(url):
    assert not valid_url(url)


def test_path_and_size_limits(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("ok")
    other = tmp_path / "sub"
    other.mkdir()
    with pytest.raises(ValueError, match="escapes"):
        local_file(other / "../source.txt", other)
    with source.open("wb") as stream:
        stream.seek(MAX_FILE_BYTES)
        stream.write(b"a")
    with pytest.raises(ValueError, match="limit"):
        local_file(source)
    assert "/" not in slugify("../../escape")
    assert slugify("CON").startswith("event-")


def test_image_missing_and_ocr_limit(tmp_path):
    with pytest.raises(ValueError):
        image_uri(tmp_path / "missing.png")
    from PIL import Image
    path = tmp_path / "private.png"
    Image.new("RGB", (50, 50)).save(path)
    with pytest.raises(ValueError, match="requires --ocr"):
        extract(path)
    assert Path(path).is_file()
