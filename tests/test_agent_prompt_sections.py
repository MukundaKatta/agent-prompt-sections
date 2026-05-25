"""Tests for agent_prompt_sections."""

from __future__ import annotations

import pytest

from agent_prompt_sections import AgentPromptSections, SectionError

# ---------------------------------------------------------------------------
# Constructor / repr
# ---------------------------------------------------------------------------


def test_repr():
    p = AgentPromptSections()
    assert "count=0" in repr(p)
    assert "enabled=0" in repr(p)


def test_repr_after_add():
    p = AgentPromptSections()
    p.add("a", "text")
    assert "count=1" in repr(p)
    assert "enabled=1" in repr(p)


def test_initial_empty():
    p = AgentPromptSections()
    assert p.is_empty() is True
    assert p.count() == 0
    assert p.names() == []


def test_custom_separator():
    p = AgentPromptSections(separator=" | ")
    p.add("a", "A").add("b", "B")
    assert p.render() == "A | B"


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------


def test_add_single():
    p = AgentPromptSections()
    p.add("role", "You are helpful.")
    assert p.get("role") == "You are helpful."


def test_add_returns_self():
    p = AgentPromptSections()
    assert p.add("a", "x") is p


def test_add_duplicate_raises():
    p = AgentPromptSections()
    p.add("a", "x")
    with pytest.raises(SectionError, match="already exists"):
        p.add("a", "y")


def test_add_before():
    p = AgentPromptSections()
    p.add("first", "F").add("third", "T")
    p.add("second", "S", before="third")
    assert p.names() == ["first", "second", "third"]


def test_add_after():
    p = AgentPromptSections()
    p.add("first", "F").add("third", "T")
    p.add("second", "S", after="first")
    assert p.names() == ["first", "second", "third"]


def test_add_before_unknown_raises():
    p = AgentPromptSections()
    with pytest.raises(SectionError):
        p.add("a", "x", before="nonexistent")


def test_add_metadata():
    p = AgentPromptSections()
    p.add("a", "x", metadata={"priority": 1})
    assert p.metadata("a") == {"priority": 1}


def test_add_metadata_deepcopy():
    meta = {"k": [1, 2]}
    p = AgentPromptSections()
    p.add("a", "x", metadata=meta)
    meta["k"].append(3)
    assert p.metadata("a") == {"k": [1, 2]}


def test_add_disabled():
    p = AgentPromptSections()
    p.add("a", "text", enabled=False)
    assert p.is_enabled("a") is False
    assert "text" not in p.render()


# ---------------------------------------------------------------------------
# set / upsert
# ---------------------------------------------------------------------------


def test_set_updates_content():
    p = AgentPromptSections()
    p.add("a", "old")
    p.set("a", "new")
    assert p.get("a") == "new"


def test_set_returns_self():
    p = AgentPromptSections()
    p.add("a", "x")
    assert p.set("a", "y") is p


def test_set_unknown_raises():
    with pytest.raises(SectionError):
        AgentPromptSections().set("nope", "x")


def test_upsert_adds_if_missing():
    p = AgentPromptSections()
    p.upsert("a", "val")
    assert p.get("a") == "val"


def test_upsert_updates_if_present():
    p = AgentPromptSections()
    p.add("a", "old")
    p.upsert("a", "new")
    assert p.get("a") == "new"


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y")
    p.remove("a")
    assert p.names() == ["b"]


def test_remove_returns_self():
    p = AgentPromptSections()
    p.add("a", "x")
    assert p.remove("a") is p


def test_remove_unknown_raises():
    with pytest.raises(SectionError):
        AgentPromptSections().remove("nope")


# ---------------------------------------------------------------------------
# enable / disable
# ---------------------------------------------------------------------------


def test_disable():
    p = AgentPromptSections()
    p.add("a", "visible").add("b", "hidden")
    p.disable("b")
    assert "visible" in p.render()
    assert "hidden" not in p.render()


def test_enable():
    p = AgentPromptSections()
    p.add("a", "text", enabled=False)
    p.enable("a")
    assert "text" in p.render()


def test_disable_enable_returns_self():
    p = AgentPromptSections()
    p.add("a", "x")
    assert p.disable("a") is p
    assert p.enable("a") is p


def test_disabled_names():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y", enabled=False).add("c", "z", enabled=False)
    assert p.disabled_names() == ["b", "c"]


def test_enabled_names():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y", enabled=False)
    assert p.enabled_names() == ["a"]


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def test_render_basic():
    p = AgentPromptSections()
    p.add("a", "Hello").add("b", "World")
    assert p.render() == "Hello\n\nWorld"


def test_render_strips_whitespace():
    p = AgentPromptSections()
    p.add("a", "  Hello  ")
    assert p.render() == "Hello"


def test_render_skips_empty():
    p = AgentPromptSections()
    p.add("a", "Hello").add("empty", "   ").add("b", "World")
    assert p.render() == "Hello\n\nWorld"


def test_render_include_disabled():
    p = AgentPromptSections()
    p.add("a", "On").add("b", "Off", enabled=False)
    assert "Off" in p.render(include_disabled=True)


def test_render_empty():
    assert AgentPromptSections().render() == ""


# ---------------------------------------------------------------------------
# move_to / reorder
# ---------------------------------------------------------------------------


def test_move_to():
    p = AgentPromptSections()
    p.add("a", "A").add("b", "B").add("c", "C")
    p.move_to(0, "c")
    assert p.names() == ["c", "a", "b"]


def test_move_to_end():
    p = AgentPromptSections()
    p.add("a", "A").add("b", "B").add("c", "C")
    p.move_to(2, "a")
    assert p.names() == ["b", "c", "a"]


def test_move_to_invalid_index():
    p = AgentPromptSections()
    p.add("a", "A")
    with pytest.raises(ValueError):
        p.move_to(5, "a")


def test_reorder_full():
    p = AgentPromptSections()
    p.add("a", "A").add("b", "B").add("c", "C")
    p.reorder(["c", "b", "a"])
    assert p.names() == ["c", "b", "a"]


def test_reorder_partial():
    p = AgentPromptSections()
    p.add("a", "A").add("b", "B").add("c", "C")
    p.reorder(["c"])
    assert p.names()[0] == "c"
    assert set(p.names()) == {"a", "b", "c"}


def test_reorder_unknown_raises():
    p = AgentPromptSections()
    p.add("a", "A")
    with pytest.raises(SectionError):
        p.reorder(["a", "unknown"])


# ---------------------------------------------------------------------------
# clear
# ---------------------------------------------------------------------------


def test_clear():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y")
    p.clear()
    assert p.is_empty()


def test_clear_returns_self():
    p = AgentPromptSections()
    assert p.clear() is p


# ---------------------------------------------------------------------------
# introspection
# ---------------------------------------------------------------------------


def test_has():
    p = AgentPromptSections()
    p.add("a", "x")
    assert p.has("a") is True
    assert p.has("z") is False


def test_is_enabled_unknown():
    assert AgentPromptSections().is_enabled("nope") is False


def test_count_enabled():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y", enabled=False).add("c", "z")
    assert p.count_enabled() == 2


def test_index_of():
    p = AgentPromptSections()
    p.add("a", "x").add("b", "y").add("c", "z")
    assert p.index_of("b") == 1


def test_index_of_unknown_raises():
    with pytest.raises(SectionError):
        AgentPromptSections().index_of("nope")


def test_summary():
    p = AgentPromptSections()
    p.add("a", "hello").add("b", "world", enabled=False)
    s = p.summary()
    assert len(s) == 2
    assert s[0]["name"] == "a"
    assert s[0]["enabled"] is True
    assert s[1]["name"] == "b"
    assert s[1]["enabled"] is False


def test_metadata_returns_copy():
    p = AgentPromptSections()
    p.add("a", "x", metadata={"k": 1})
    m = p.metadata("a")
    m["k"] = 999
    assert p.metadata("a") == {"k": 1}
