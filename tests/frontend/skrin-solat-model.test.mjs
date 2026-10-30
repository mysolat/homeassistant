import { test } from "node:test";
import assert from "node:assert/strict";
import * as model from "../../custom_components/solat_my/frontend/skrin-solat-model.mjs";

const entities = {
  subuh: "sensor.s", syuruk: "sensor.sy", zohor: "sensor.z", asar: "sensor.a",
  maghrib: "sensor.m", isyak: "sensor.i", hijri: "sensor.h", current: "sensor.c",
};
const times = { s: "05:48", sy: "06:55", z: "13:00", a: "16:20", m: "18:58", i: "20:09" };
const states = {};
for (const [id, hhmm] of Object.entries(times)) {
  states[`sensor.${id}`] = { state: `2026-10-31T${hhmm}:00+08:00`, attributes: { zone_desc: "Selangor" } };
}
states["sensor.h"] = { state: "20 Jamadil Awwal 1448H" };
states["sensor.c"] = { state: "Isyak" };

test("formatCountdown formats 3661 seconds as 01:01:01", () => {
  assert.equal(model.formatCountdown(3661), "01:01:01");
});

test("formatCountdown clamps negative seconds to zero", () => {
  assert.equal(model.formatCountdown(-5), "00:00:00");
});

test("formatCountdown treats NaN as zero", () => {
  assert.equal(model.formatCountdown(NaN), "00:00:00");
});

test("isLocalAsset accepts a /local/ path", () => {
  assert.equal(model.isLocalAsset("/local/a.png"), true);
});

test("isLocalAsset rejects a remote URL", () => {
  assert.equal(model.isLocalAsset("https://x/a.png"), false);
});

test("isLocalAsset rejects a path with a newline", () => {
  assert.equal(model.isLocalAsset("/local/a\n.png"), false);
});

test("formatPrayerTime formats 24h by default", () => {
  assert.equal(model.formatPrayerTime(new Date("2026-10-30T05:48:00+08:00")), "05:48");
});

test("formatPrayerTime formats 12h with a day period", () => {
  assert.equal(model.formatPrayerTime(new Date("2026-10-30T13:00:00+08:00"), "12h"), "01:00 PM");
});

test("splitDayPeriod splits clock and period", () => {
  assert.deepEqual(model.splitDayPeriod("01:00 PM"), { clock: "01:00", period: "PM" });
});

test("assertSkrinSolatConfig throws when entities.subuh is missing", () => {
  assert.throws(
    () => model.assertSkrinSolatConfig({ entities: {} }),
    new Error("entities.subuh is required"),
  );
});

test("buildPrayerView points at tomorrow's subuh after Isyak", () => {
  const view = model.buildPrayerView({
    config: { entities },
    states,
    now: new Date("2026-10-31T21:00:00+08:00"),
  });
  assert.equal(view.status, "ready");
  assert.equal(view.next.key, "subuh");
  assert.equal(view.next.at.toISOString(), "2026-10-31T21:48:00.000Z");
  assert.equal(view.countdownSeconds, 31680);
});

test("buildPrayerView reports a fault when the times are from yesterday", () => {
  const view = model.buildPrayerView({
    config: { entities },
    states,
    now: new Date("2026-11-01T09:00:00+08:00"),
  });
  assert.equal(view.status, "fault");
  assert.equal(view.message, "Waktu tidak dikemas kini");
});
