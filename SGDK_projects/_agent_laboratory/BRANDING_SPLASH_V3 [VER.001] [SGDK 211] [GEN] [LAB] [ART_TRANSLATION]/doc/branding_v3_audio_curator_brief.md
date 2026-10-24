# Curator brief - Splash V3 sonic logo

## Authority and listening history

- Direction comes from the user's original 16-bit audio-branding brief and listening feedback. No recognizable melody, logo, recording, or patch from Capcom, Konami, SNK, or another publisher is copied.
- The user first described the sound as monophonic and muffled, with timbral layers that felt too similar. They later said the musical quality was still low, asked for a more crystalline color, then rejected a continuous, monotonous result that lacked the agreed animation and energy. Treat “monophonic” here as a perceptual criticism of the arrangement/timbre, not a request for stereo output.
- V010 was rejected for low musical quality. V011 was superseded after PSG notes overlapped PCM cues. V012 received positive feedback ("ficou bem melhor") and remains the musical reference.
- V013 and V014 were rejected by the user for sounding continuous and monotonous, without the agreed energy and animation. V014's short note gates did not create enough separation; its FM envelopes and accompanying voices still blurred the phrases.
- V015 is accepted for development by the user. This is not final musical-quality approval; schedule a focused listening review after the visual scene is integrated.

## V015 composition

- Preserve the eight-note V012 contour: C5-G5-E5-F5 | D5-G5-B5-C6.
- Use two 6/8 bars at 120 BPM (180 NTSC frames / 3 seconds), with syncopated pickups and sharply contrasting gaps. The call plays at score frames 0/8/16, then F5 at 42. The answer starts at 72 and rises through D5/G5/B5 to C6 at 102.
- The lead key gates occupy 52 of 180 score frames. FM patches use faster release; there is no sustained pad or continuous bass voice.
- Bass and harmony are short synchronized stabs at score frames 0/42/72/102. PSG remains silent.
- Additive FM glass pings E6/G6/C7 occur at score frames 26/88/106, each 3-4 frames. They decorate the rests and final landing without becoming a second sustained line.
- Start the stream at scene frame 60 after the energy-rise cue. Music notes finish by scene frame 174. The mark-lock cue occupies the deliberate breath at scene frames 118-129; the rising answer resumes at frame 132. Leave the sweep at 178-203 and tail at 210-233 free of music.

## Intended sound

Bright, heroic, animated, and rhythmically memorable. The brass states the familiar eight-note identity in clipped bursts. The bass gives four firm rhythmic anchors; the high additive voice adds brief crystal sparkles. Clear silence between phrases is part of the arrangement. Avoid long envelope release, sustained support, and a continuous monophonic line.

## Curatorial disposition

- Keep the positive, adventurous, premium opening energy: immediate attack, short rising call-and-response, clear rhythmic gaps, a firm major resolution, and a small number of memorable notes.
- Preserve the requested crystalline high end, but keep it as brief accents around the lead. The brightness must survive small-speaker playback without turning the whole mix into a continuous bell or pad.
- Keep FM layers distinct in register and envelope. Short bass/harmony stabs should support the lead; fast releases and real rests should keep phrases from blending into one sustained sound.
- Review the integrated scene on the exact ROM for melodic identity, rhythmic animation, crystal clarity, balance against PCM cues, triumphant resolution, and whether the ending has enough impact. Record new feedback before revising the score.
- Current status: V016/VGM4 is the current review candidate, built on the V015 arrangement with stereo refinements. A direct two-pass preview-ROM capture is now ready for listening; human musical approval, canonical capture, DAC budget, and sustained performance remain open.

## Cue alignment

| Scene frame | Event | Musical relationship |
|---:|---|---|
| 24-59 | energy rise | Digital reveal before music entry |
| 60 | music starts | Immediate C-major attack |
| 118-129 | mark lock | PCM occupies the musical breath; lead resumes at 132 |
| 174 | FM notes end | Four-frame clearance before the sweep |
| 178-203 | sweep | PCM sweep plays alone |
| 210-233 | tail | PCM tail reinforces the resolution after the music |
| 240 | scene exit | Stop XGM2 and PCM before handoff |

Score frames are relative to scene frame 60. The VGM stream is exactly 180 frames; all authored music notes end by score frame 114, leaving the remaining stream clear for the synchronized sound effects and final tail.

## Review gate

V016/VGM4 has both the earlier stereo/mono artifact derived from one captured cycle and the newer direct two-pass preview-ROM capture below. The direct capture supports listening to the score and cues; it does not replace review in the full visual scene on the project baseline ROM. Build success, ResComp, XGM2 conversion, loop structure, and playback counters prove technical execution only. The user decides whether the rhythm, energy, crystal color, cue mix, and resolution work.


## V016 two-pass audition — 2026-10-14

- Stereo review file: `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_stereo.wav`.
- Mono fold-down: `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_mono_fold.wav`.
- The 6-second artifact repeats one captured 3-second V016/VGM4 cycle twice. Source capture is the V012 visual-preview ROM; VGM4, cue and `audio.c` hashes match V017. The second pass is an offline duplicate for listening and seam inspection, not a second ROM scene execution.
- Source samples were cropped from the existing review WAV; no additional EQ, gain, crossfade or normalization. Review human approval, direct frame-marked capture from the current ROM, DAC budget and sustained performance remain open.
- Listen for short energetic call-and-answer, clean rests, crystalline accents that remain brief, a decisive landing, bass/harmony support, and clarity in both stereo and mono.

## V016 direct ROM audition — 2026-10-15

- A two-pass preview ROM was built in isolation and run in BlastEm. ROM SHA-256: `35af30bb5b0cfe52fb527858b9cd164ed496ee46f144e2396fd151841fb16e71`; the screen capture is linked to that exact binary and reports `MUSIC 358/358 DROP:0` across both authored listening windows.
- Stereo and mono WAVs in `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/` are an eight-second cut from the direct BlastEm audio output. They include both passes and their scene cues; no normalization or extra EQ was applied. The 20 Hz high-pass only removes captured DC. The capture run record and manifest bind the WAVs to the ROM, raw capture, screenshot and SRAM hashes.
- This is an unsealed, isolated preview ROM, not the V017 baseline `out/rom.bin`. A second run after moving the completion marker failed in the GTK warning dialog and produced no valid capture; the first direct audio capture remains valid for listening because the later source change only moved preview text and did not change score, cues or timing.
- Human review remains open. Judge whether the brass call-and-answer feels energetic and heroic, whether the high pings are clear and crystalline without forming a continuous wash, whether real rests remain audible, and whether the C-major landing and PCM cues resolve with enough impact. Do not infer musical approval from the 358/358 playback counter.
