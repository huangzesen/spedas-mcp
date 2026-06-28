---
name: spice-conjunction-finder
description: Find times when two spacecraft/bodies are close (a conjunction) over an interval — scan ephemerides, compute pairwise separation coarse-then-fine, apply a distance threshold, and render separation vs time. Pure SPICE geometry; composes existing tools and needs no data fetch or [analysis] extra.
---

# Multi-spacecraft / body conjunction finder

A guided version of the SPEDAS conjunction crib: locate the times in a window when two
objects (two spacecraft, or a spacecraft and a planet) are within some separation. The
value is the **scan-and-refine procedure with kernel handling** — no single tool finds
conjunctions; this composes the geometry tools with judgment between steps.

## When to use
- "When were PSP and Solar Orbiter closest in <year>?"
- "Find conjunctions between <A> and <B> under <N> million km."
- "Is spacecraft X near planet Y during this interval?"

## Tool chain (all already exist, geometry-only)
`list_spice_missions` → `list_coordinate_frames` → `manage_spice_kernels` (availability)
→ `compute_distance` (coarse, then refined) → `get_ephemeris` (context) → `render_tplot`,
wrapped in `create_spedas_analysis_bundle`.

## Procedure

1. **Bundle.** `create_spedas_analysis_bundle(study_name, output_dir, science_goal, start, stop)`.

2. **Confirm both objects are supported.** `list_spice_missions()` — verify both targets resolve to SPICE bodies (unsupported names return a structured error with alternatives). Pick a common observer/frame from `list_coordinate_frames()` (e.g. `ECLIPJ2000` heliocentric, or `SUN`-centered).

3. **Handle kernels deliberately.** Geometry calls gate large kernel downloads. Either pre-load with `manage_spice_kernels(action="load", mission=...)`, or pass `allow_kernel_download=true` once you accept the (possibly 100 MB+) download. Do this knowingly — don't let it surprise you mid-scan.

4. **Coarse scan.** `compute_distance(target1, target2, time_start, time_end, step="1d")` (or `"6h"` for short windows) over the whole interval. Read the returned `min_distance_km`/`max_distance_km`/sample summary to locate candidate minima — the day(s) where separation dips.

5. **Refine around candidates.** Re-run `compute_distance` with a **fine step** (`"1h"`/`"10m"`) over each narrow sub-window around a coarse minimum to pin the true closest-approach time and distance. (This coarse→fine pattern is the whole point: one fine-step scan over a year is wasteful; the coarse pass tells you where to look.)

6. **Apply the threshold & report.** Keep candidates under the user's separation cutoff. For each conjunction report: time of closest approach, min separation (km and AU/Re as appropriate), and — via `get_ephemeris` — each object's heliocentric distance/position at that time for context (e.g. "both near 0.3 AU").

7. **Render.** Write a separation-vs-time series (from the refined scan) to CSV and `render_tplot(input_files=[<sep.csv>], output_file=<bundle>/plots/separation.png, panel_types=["line"], ylog=true)`. Mark/annotate the conjunction(s) in `notes/`.

## Guardrails
- Artifact-first: report closest-approach times + distances + the PNG path, not full sampled tables.
- Coarse-then-fine: never do a fine-step scan over a long interval; localize first.
- Kernel cost: a wide multi-mission scan can need several large kernels — state which you loaded; respect the download gate.
- Frame/observer must be the same for both objects' positions to be comparable.

## Example (verified primitives)
`compute_distance(PSP, SUN, ...)` returns min/max/mean km over a sampled window (I used this live: PSP–Sun min 6.86e6 km at the E24 perihelion, matching the instrument's onboard SUN_DIST to ~90 km — a clean cross-check that the geometry tools are trustworthy for conjunction work).
