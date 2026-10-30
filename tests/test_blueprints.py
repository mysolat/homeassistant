"""Tests for the automation blueprints in blueprints/automation/solat_my/.

Each test loads a blueprint, substitutes its inputs, and sets up the resulting
automation. Home Assistant then validates the blueprint the same way as for a
user. The solat_my entities are plain states, so the integration does not load.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from homeassistant.components.automation.config import AUTOMATION_BLUEPRINT_SCHEMA
from homeassistant.components.blueprint import models
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
from homeassistant.util.yaml import load_yaml_dict
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

BLUEPRINTS = Path(__file__).parent.parent / "blueprints" / "automation" / "solat_my"
ALL_BLUEPRINTS = sorted(path.name for path in BLUEPRINTS.glob("*.yaml"))
assert ALL_BLUEPRINTS, f"no blueprints found in {BLUEPRINTS}"

SOURCE_URL_PREFIX = (
    "https://github.com/mysolat/homeassistant/blob/main/blueprints/automation/solat_my/"
)
MEDIA_PREFIX = "media-source://media_source/local/"

# Inputs that have no default.
REQUIRED_INPUTS = {
    "azan_multi_room.yaml": {"speakers": ["media_player.ruang_tamu"]},
}

# One second keeps the delays short. The tests advance the clock past them.
ONE_SECOND = {"hours": 0, "minutes": 0, "seconds": 1}
SHORT_DELAYS = {"subuh_delay": ONE_SECOND, "azan_delay": ONE_SECOND}

PLAYER_SERVICES = (
    "media_player.play_media",
    "media_player.volume_set",
    "persistent_notification.create",
)


def _load(name: str) -> models.Blueprint:
    """Load one blueprint with the schema the automation integration uses."""
    return models.Blueprint(
        load_yaml_dict(str(BLUEPRINTS / name)),
        path=name,
        expected_domain="automation",
        schema=AUTOMATION_BLUEPRINT_SCHEMA,
    )


def _automation_config(name: str, inputs: dict | None = None) -> dict:
    """Return the automation config a blueprint produces for these inputs."""
    blueprint_inputs = models.BlueprintInputs(
        _load(name), {"use_blueprint": {"path": name, "input": inputs or {}}}
    )
    blueprint_inputs.validate()
    config = blueprint_inputs.async_substitute()
    config["id"] = name
    config["alias"] = Path(name).stem
    return config


async def _setup(hass, config: dict) -> None:
    """Set up one automation from a substituted blueprint config."""
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()


async def _start(hass, freezer, name: str, inputs: dict | None, now: str) -> None:
    """Set the clock to now, then set up the blueprint's automation.

    A time trigger only arms for a sensor time that is still in the future.
    Start just before the prayer under test, so the earlier prayers stay idle.
    """
    freezer.move_to(now)
    await _setup(hass, _automation_config(name, inputs))


async def _settle() -> None:
    """Let the event loop run every ready callback.

    hass.async_block_till_done cannot do this here, because it waits for a run
    that sits in a delay and the delay only ends when the test moves the clock.
    """
    for _ in range(100):
        await asyncio.sleep(0)


async def _move_to(hass, freezer, now: str) -> None:
    """Move the clock to now and fire the timers that are due."""
    freezer.move_to(now)
    async_fire_time_changed(hass)
    await _settle()


async def _advance(hass, freezer, seconds: int) -> None:
    """Advance the clock one second at a time, so chained delays run out."""
    for _ in range(seconds):
        freezer.tick(1)
        async_fire_time_changed(hass)
        await _settle()


def _mock(hass, *names: str) -> dict[str, list]:
    """Record the calls to each service, named "domain.service"."""
    return {name: async_mock_service(hass, *name.split(".")) for name in names}


def _media_ids(play_calls: list) -> list[str]:
    """Return the media_content_id of each play_media call."""
    return [call.data["media"]["media_content_id"] for call in play_calls]


@pytest.fixture
async def solat_states(hass):
    """Create the solat_my states the blueprints read, in Malaysian time."""
    await hass.config.async_set_time_zone("Asia/Kuala_Lumpur")
    for prayer, at in {
        "imsak": "2026-10-29T21:38:00+00:00",
        "subuh": "2026-10-29T21:48:00+00:00",
        "zohor": "2026-10-30T05:00:00+00:00",
        "asar": "2026-10-30T08:19:00+00:00",
        "maghrib": "2026-10-30T10:59:00+00:00",
        "isyak": "2026-10-30T12:09:00+00:00",
    }.items():
        hass.states.async_set(
            f"sensor.waktu_solat_{prayer}", at, {"device_class": "timestamp"}
        )
    hass.states.async_set(
        "select.waktu_solat_pemain_media_azan", "media_player.ruang_tamu"
    )
    hass.states.async_set("select.waktu_solat_mod_pengumuman_azan", "audio")
    hass.states.async_set("number.waktu_solat_kelantangan_azan", "0.6")
    hass.states.async_set("text.waktu_solat_fail_audio_azan", "azan1.mp3,azan2.mp3")
    hass.states.async_set("text.waktu_solat_fail_audio_azan_subuh", "azan_subuh.mp3")
    hass.states.async_set(
        "text.waktu_solat_fail_doa_selepas_azan", "doa_selepas_azan.mp3"
    )
    hass.states.async_set(
        "media_player.ruang_tamu", "idle", {"supported_features": 4}
    )

    yield

    # A test must end with no run left waiting on a delay.
    for state in hass.states.async_all("automation"):
        assert state.attributes.get("current", 0) == 0, f"{state.entity_id} still runs"
    # Detach the time triggers, so no timer outlives the test.
    if hass.services.has_service("automation", "turn_off"):
        await hass.services.async_call(
            "automation", "turn_off", {"entity_id": "all"}, blocking=True
        )


@pytest.mark.parametrize("name", ALL_BLUEPRINTS)
async def test_all_blueprints_validate(hass, freezer, solat_states, name) -> None:
    """Home Assistant accepts each blueprint with only its required inputs."""
    freezer.move_to("2026-10-29T20:00:00+00:00")
    assert _load(name).validate() is None

    await _setup(hass, _automation_config(name, REQUIRED_INPUTS.get(name)))

    state = hass.states.get(f"automation.{Path(name).stem}")
    assert state is not None
    assert state.state != STATE_UNAVAILABLE


@pytest.mark.parametrize("name", ALL_BLUEPRINTS)
def test_source_urls_point_at_repo(name) -> None:
    """Each source_url points at the file in the mysolat/homeassistant repo."""
    source_url = _load(name).metadata["source_url"]

    assert source_url.startswith(SOURCE_URL_PREFIX)
    assert source_url.endswith(f"/{name}")


@pytest.mark.parametrize("name", ALL_BLUEPRINTS)
def test_min_version_set(name) -> None:
    """Each blueprint needs Home Assistant 2024.10, which has triggers: and actions:."""
    metadata = _load(name).metadata

    assert metadata["homeassistant"]["min_version"] == "2024.10.0"


async def test_harian_plays_subuh_azan(hass, freezer, solat_states) -> None:
    """At Subuh the Subuh azan plays, then the doa after the azan delay."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    await _start(
        hass, freezer, "azan_harian.yaml", SHORT_DELAYS, "2026-10-29T21:47:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    await _advance(hass, freezer, 10)

    ids = _media_ids(play)
    assert ids[-1].endswith("azan/azan_subuh.mp3")
    assert not any(i.endswith("azan/doa_selepas_azan.mp3") for i in ids)

    await _advance(hass, freezer, 2)

    assert _media_ids(play)[-1].endswith("azan/doa_selepas_azan.mp3")


async def test_harian_plays_without_notify(hass, freezer, solat_states) -> None:
    """The azan plays when the user sets no notify_actions and no notify service exists."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    assert not hass.services.has_service("notify", "notify")
    await _start(
        hass, freezer, "azan_harian.yaml", SHORT_DELAYS, "2026-10-29T21:47:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    await _advance(hass, freezer, 12)

    assert any(i.endswith("azan/azan_subuh.mp3") for i in _media_ids(play))


async def test_harian_runs_notify_actions_after_azan(
    hass, freezer, solat_states
) -> None:
    """The notify_actions run once the azan has started, not before."""
    calls = _mock(hass, *PLAYER_SERVICES, "notify.test")
    play = calls["media_player.play_media"]
    notify = calls["notify.test"]
    inputs = {
        **SHORT_DELAYS,
        "notify_actions": [{"action": "notify.test", "data": {"message": "x"}}],
    }
    await _start(
        hass, freezer, "azan_harian.yaml", inputs, "2026-10-29T21:47:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    assert notify == []

    await _advance(hass, freezer, 10)

    assert len(notify) == 1
    assert _media_ids(play)[-1].endswith("azan/azan_subuh.mp3")
    await _advance(hass, freezer, 2)


async def test_harian_tts_failure_still_plays_azan(
    hass, freezer, solat_states
) -> None:
    """An error from tts.speak does not stop the azan."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    speak = async_mock_service(
        hass, "tts", "speak", raise_exception=HomeAssistantError("TTS is down")
    )
    hass.states.async_set("select.waktu_solat_mod_pengumuman_azan", "tts")
    inputs = {**SHORT_DELAYS, "tts_entity": "tts.test"}
    await _start(
        hass, freezer, "azan_harian.yaml", inputs, "2026-10-29T21:47:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    await _advance(hass, freezer, 12)

    assert len(speak) == 1
    assert any(i.endswith("azan/azan_subuh.mp3") for i in _media_ids(play))


async def test_harian_tts_mode_without_entity_plays_azan(
    hass, freezer, solat_states
) -> None:
    """In tts mode with no TTS entity picked, the azan plays and tts.speak is not called."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    speak = async_mock_service(hass, "tts", "speak")
    hass.states.async_set("select.waktu_solat_mod_pengumuman_azan", "tts")
    await _start(
        hass, freezer, "azan_harian.yaml", SHORT_DELAYS, "2026-10-29T21:47:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    await _advance(hass, freezer, 12)

    assert speak == []
    assert any(i.endswith("azan/azan_subuh.mp3") for i in _media_ids(play))


@pytest.mark.parametrize(
    ("inputs", "expected_calls"),
    [({"skip_zohor_friday": True}, 0), ({}, 1)],
    ids=["skip_on", "default"],
)
async def test_harian_skips_zohor_on_friday(
    hass, freezer, solat_states, inputs, expected_calls
) -> None:
    """With skip_zohor_friday on, Zohor on Friday plays nothing. The default plays."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    await _start(
        hass,
        freezer,
        "azan_harian.yaml",
        {**SHORT_DELAYS, **inputs},
        "2026-10-30T04:59:00+00:00",
    )

    # 05:00 UTC on Friday 30 October 2026 is 13:00 on Friday in Malaysia.
    await _move_to(hass, freezer, "2026-10-30T05:00:00+00:00")

    assert len(play) == expected_calls

    await _advance(hass, freezer, 12)


@pytest.mark.parametrize(
    "filenames",
    ["azan1.mp3,azan2.mp3", "azan1.mp3, azan2.mp3", "azan1.mp3,azan2.mp3,"],
)
async def test_harian_splits_filenames_without_spaces(
    hass, freezer, solat_states, filenames
) -> None:
    """The azan file is one name from the list, however the list is spaced."""
    calls = _mock(hass, *PLAYER_SERVICES)
    play = calls["media_player.play_media"]
    hass.states.async_set("text.waktu_solat_fail_audio_azan", filenames)
    await _start(
        hass, freezer, "azan_harian.yaml", SHORT_DELAYS, "2026-10-30T04:59:00+00:00"
    )

    await _move_to(hass, freezer, "2026-10-30T05:00:00+00:00")
    await _advance(hass, freezer, 12)

    azan = [i for i in _media_ids(play) if "/azan/azan" in i]
    assert len(azan) == 1
    assert "," not in azan[0]
    assert azan[0] in (MEDIA_PREFIX + "azan/azan1.mp3", MEDIA_PREFIX + "azan/azan2.mp3")


async def test_sebelum_solat_fires_before_prayer(hass, freezer, solat_states) -> None:
    """The reminder runs 15 minutes before Maghrib and not a minute earlier."""
    calls = _mock(hass, "persistent_notification.create", "notify.test")
    notify = calls["notify.test"]
    inputs = {
        "prayer_sensor": "sensor.waktu_solat_maghrib",
        "time_before": {"hours": 0, "minutes": -15, "seconds": 0},
        "notify_actions": [{"action": "notify.test", "data": {"message": "x"}}],
    }
    await _start(
        hass,
        freezer,
        "peringatan_sebelum_solat.yaml",
        inputs,
        "2026-10-30T10:30:00+00:00",
    )

    await _move_to(hass, freezer, "2026-10-30T10:43:00+00:00")
    assert notify == []

    await _move_to(hass, freezer, "2026-10-30T10:44:00+00:00")
    assert len(notify) == 1


async def test_sebelum_solat_message_counts_minutes(
    hass, freezer, solat_states
) -> None:
    """The persistent notification names the prayer, the minutes left and the time."""
    calls = _mock(hass, "persistent_notification.create")
    created = calls["persistent_notification.create"]
    inputs = {"time_before": {"hours": 0, "minutes": -15, "seconds": 0}}
    await _start(
        hass,
        freezer,
        "peringatan_sebelum_solat.yaml",
        inputs,
        "2026-10-30T10:30:00+00:00",
    )

    await _move_to(hass, freezer, "2026-10-30T10:44:00+00:00")

    assert len(created) == 1
    # 10:59 UTC is 18:59 in Malaysia.
    assert created[0].data["message"].split() == (
        "Maghrib dalam masa 15 minit pada pukul 18:59.".split()
    )


async def test_jeda_sambung_resumes(hass, freezer, solat_states) -> None:
    """The blueprint pauses a playing player, plays the azan, then resumes it."""
    calls = _mock(
        hass,
        *PLAYER_SERVICES,
        "media_player.media_pause",
        "scene.create",
        "scene.turn_on",
    )
    play = calls["media_player.play_media"]
    pause = calls["media_player.media_pause"]
    resume = calls["scene.turn_on"]
    hass.states.async_set("media_player.dapur", "playing")
    await _start(
        hass,
        freezer,
        "azan_jeda_sambung.yaml",
        SHORT_DELAYS,
        "2026-10-29T21:47:00+00:00",
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")

    assert [call.data["entity_id"] for call in pause] == [["media_player.dapur"]]

    await _advance(hass, freezer, 2)
    assert _media_ids(play)[-1].endswith("azan/azan_subuh.mp3")

    # The azan is playing, so the blueprint waits for the player to go idle.
    hass.states.async_set(
        "media_player.ruang_tamu", "playing", {"supported_features": 4}
    )
    await _advance(hass, freezer, 5)
    assert _media_ids(play)[-1].endswith("azan/doa_selepas_azan.mp3")
    assert resume == []

    # Idle ends the wait. The resume comes long before the 2 minute timeout.
    hass.states.async_set(
        "media_player.ruang_tamu", "idle", {"supported_features": 4}
    )
    await _advance(hass, freezer, 3)

    assert len(resume) == 1
    assert resume[0].data["entity_id"] == ["scene.sebelum_azan"]


async def test_jeda_sambung_waits_for_doa_to_start(hass, freezer, solat_states) -> None:
    """The resume waits for the doa to start and then end, not for the first idle."""
    calls = _mock(
        hass,
        *PLAYER_SERVICES,
        "media_player.media_pause",
        "scene.create",
        "scene.turn_on",
    )
    play = calls["media_player.play_media"]
    resume = calls["scene.turn_on"]
    hass.states.async_set("media_player.dapur", "playing")
    await _start(
        hass,
        freezer,
        "azan_jeda_sambung.yaml",
        SHORT_DELAYS,
        "2026-10-29T21:47:00+00:00",
    )

    await _move_to(hass, freezer, "2026-10-29T21:48:00+00:00")
    await _advance(hass, freezer, 4)

    # The doa has started, but the player still reports idle.
    assert _media_ids(play)[-1].endswith("azan/doa_selepas_azan.mp3")
    await _advance(hass, freezer, 5)
    assert resume == []

    # The doa starts playing. The blueprint now waits for it to end.
    hass.states.async_set(
        "media_player.ruang_tamu", "playing", {"supported_features": 4}
    )
    await _advance(hass, freezer, 30)
    assert resume == []

    # Idle ends the second wait, long before its 2 minute timeout.
    hass.states.async_set(
        "media_player.ruang_tamu", "idle", {"supported_features": 4}
    )
    await _advance(hass, freezer, 3)

    assert len(resume) == 1
