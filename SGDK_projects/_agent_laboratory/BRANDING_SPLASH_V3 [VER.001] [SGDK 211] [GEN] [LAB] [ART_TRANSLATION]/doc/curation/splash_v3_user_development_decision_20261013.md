# Curatorial decision record — Splash V3 — 2026-10-13

## User decision

The user authorized promoting Splash V3 as **in development**, asked that it be reviewed later for improvement, requested that all curatorial points be recorded, and directed work to continue on the missing visual portion.

Scope: continue WIP assets and an isolated laboratory preview. This is not final approval of the music, visual direction, model sheet, pixels, ROM, or template promotion. FORJA V2, the canonical template, and consumer projects stay untouched until their separate gates pass.

## Curatorial brief

- Short audio identity, about 2–4 seconds, with a memorable 5–8 note rising idea and a confident major resolution.
- Emotional target: positive victory and heroism combined with crystalline technology and adventure. Capcom/Konami are emotional references only; do not copy their melodies or exact brand timbres. Aggressive SNK-like energy is outside the target.
- Start promptly. Use articulated phrases, rests, a clear lead, short harmonic stabs, and brief high crystalline accents. Keep the bass short and subordinate. Avoid a continuous monophonic bed, muffled layers, repetitive timbres, long reverb, and a dark or melancholic resolution.
- Visual beats should support the same energy: silence, blue energy expanding, a distinct convergence, SGDK outline and fill, FORGE as a subordinate signature, a brief left-to-right crystal sweep, then a clean fade.
- Avoid static glow as a substitute for motion, continuous sparkle, noisy crystal density under the mark, or an intro that feels like one sustained tone.

## User feedback history to preserve

1. The initial sound played, but felt muffled and monophonic, with layers that sounded like the same timbre.
2. A later version improved, but musical quality was still too low; the user requested a more crystalline color.
3. The next version was rejected because it became a continuous, monotonous sound without the agreed animation and energy.
4. V012 remains the positive musical reference. V013 and V014 remain rejected history. V015 may be used for development only; it has not received final musical approval.

The detailed revision-by-revision record remains in `doc/curation/splash_v3_curator_record_20261012.md` and the current visual record in `doc/curation/splash_v3_visual_curation_record_20261013.md`.

## Visual direction and hardware constraints

- Use composition V003 as a provisional development direction: a readable SGDK/FORGE lockup framed by blue crystalline energy, with a dark central field and a brief directional sweep.
- Keep the mark dominant, FORGE subordinate, and negative space around the lettering. Review the lower-corner density and the mark width at native 320×224.
- The H40 scene has 320×224 pixels, 8×8 tiles, no alpha blending, no partial alpha, and no more than 15 visible colors per palette. All visible colors must land on the 9-bit Mega Drive grid. Index 0 is transparent for imported plates and sprites.
- The measured 64-particle 8×8 profile is only a pressure candidate: 17 sprites and 136 sprite pixels on its worst line, 64 total links. Re-measure against the actual final positions and cells. This does not close total VRAM, DMA, CPU, DAC, or frame-rate budgets.
- Re-author the background as a small reusable tile vocabulary. Do not promote the 320×224 raster preview as-is: its measured 1,120 unique 8×8 tiles are outside the intended 20–40-tile target.

## Future review gate

Review the exact ROM hash after a full Splash V3 scene is assembled. Observe the animation at native scale and hear at least two consecutive full cycles. Judge visual hierarchy, crystal density, motion readability, articulation, timbral separation, crystalline accents, and the quality of the final resolution. Record the user's decision against the exact asset/ROM hashes.

Until that review and the technical gates are complete, statuses remain `em_desenvolvimento`, `needs_review`, or `placeholder` as applicable. Do not describe V3 as final, `ready_for_aaa`, or ready to replace the template splash.
