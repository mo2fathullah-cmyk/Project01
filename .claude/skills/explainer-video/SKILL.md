---
name: explainer-video
description: Make short vertical (9:16, 1080x1920) animated explainer videos for UniMAP lectures in Dr Fathullah's "Every kWh Counts" style - flat illustration + kinetic typography, simple-English voice-over (young female or male), original bass-heavy background music, burned-in subtitles, UniMAP logo and "DrFath" watermark, rendered sharp so it does not blur after upload. Use whenever the user asks for a video explainer, video pengajaran, lecture reel/TikTok, motion graphic or "video macam EP1" from slides (PPTX/PDF) or a topic, asks to split a lecture into a video series, or asks to continue, re-voice (suara lelaki/perempuan) or fine-tune an episode - even if they do not name the style.
---

# Explainer video (Every kWh Counts style)

Code-built videos: each episode is one HTML page animated with GSAP, captured frame by frame
with Playwright at 2x, then voiced, scored and encoded with ffmpeg. The user is a lecturer
(AP Ir Dr Mohd Fathullah Ghazali, FKTM UniMAP). Talk to him in casual Malay ("bro", short
sentences); he does not read code, so describe results in plain words and send the MP4.

## The user's standing preferences (learned, do not re-ask)

- **Language of the video: 100% simple English** (CEFR ~B1) for Malay students. No Malay lines
  unless he asks. Short sentences, everyday words, explain a term the first time it appears.
- **No self-introduction** ("I'm Dr Fathullah") - go straight to teaching. Outro shows
  "<course code> · <course name> · UniMAP".
- **Voice: young female by default (`af_heart`)**; he sometimes wants male (`am_michael`).
  Offline Kokoro voices cannot speak fluent Malay - do not offer Malay-accent hacks again.
  He declined paid TTS that needs a bank card (Azure/Google). ElevenLabs free tier (email
  only) or his own recording are the only upgrade paths; offer them only if he complains.
- **Pronunciation**: "ringgit" = ring-GIT (hard g), never "ring-jit". Fixed words live in
  `LEXICON` in `tts.py`; add any new word he corrects there. EP1's final MP4 still has the
  old "ring-jit" (he chose not to re-render) - fix it if EP1 is ever re-produced.
- **Music: original, bass-heavy lo-fi trap** made by `music.py` (no samples, no copyright
  issue). He dislikes "boring polyphonic" orchestral beds. Music ducks ~9 dB under the voice.
- **Brand**: UniMAP logo on a white plate top-left; "DrFath" watermark bottom-right, raised
  above the Reels/TikTok button zone (top 1748px), 55% opacity. Series pill top-centre,
  course tag pill under it.
- **Pacing he approved**: hook in the first 3 s, one idea per scene, ~3-8 s per scene,
  60-90 s per episode. "Tak laju sangat, tak slow sangat."
- **Anti-blur is mandatory** (he complained earlier videos looked "pecah"): capture at 2x and
  Lanczos-downscale, x264 CRF 16 `-tune animation`, 30 fps, static grain over gradients,
  bold fonts, no hairlines. `render.js` already does all of this.
- **Workflow etiquette**: propose, then wait. Never start the next episode until he says so.
  Deliver every finished MP4 with SendUserFile (he cannot find files in the repo; MP4s are
  git-ignored except `final/`). Commit sources and push after each step.

## Workflow

1. **Read the source.** For a PPTX use the pptx skill's `slide_text.py` (includes speaker
   notes - they hold the worked numbers). Note every number; videos must match slides exactly.
2. **Propose the series breakdown** (table: #, title, slides, length), grouped by lecture
   section. Rules: common misconceptions get their own episode; worked examples the
   assignment depends on are split into steps; units before formulas. See
   `references/w6-series-plan.md` for the approved Week 6 plan as a model.
3. **Script one episode** as a table: scene · time · visual · on-screen text · voice-over.
   Fixed flow: Hook (real scene) → Idea → Build (formula appears term by term) →
   KEY POINT card → Pause & Try (5 s countdown, then answer) → Outro with "NEXT · EP n".
   Wait for approval.
4. **Scaffold**: `scripts/new_episode.sh <series_dir> <epNN>` (series dir e.g.
   `videos/w6-every-kwh`). It copies the engine into `<series>/shared` and the EP1 page as the
   starting point.
5. **Build the page** (`<ep>/index.html`). Keep the frame (brand, meters, captions, grain,
   seek/warp code); replace the scenes. Read `references/style-guide.md` for layout zones,
   palette and components. Write captions in `CAPS` ([start, end, html] on the base
   timeline) and the matching voice lines in `audio/lines.json` (same ids/times; spell numbers
   and units the way they should be spoken: "nine hundred kilowatt hours"). Set music cues in
   `audio/cues_base.json` on the base timeline (`base` = DUR, `lift` = energy up,
   `break` = drums out under KEY POINT, `riser`/`drop` = countdown into the answer).
6. **Check stills before any full render**:
   `node shared/render.js <ep>/index.html stills <dir> 3,9.5,19,...` then hstack them into a
   contact sheet and look at it. Typical bugs: text wrapping/overflow, a label hidden behind
   an SVG shape (draw connectors after the shape), badges overlapping grids, missing spaces
   between caption spans (captions must be wrapped in an inner `<div>`, already done).
7. **Produce** (voice → time-warp → music → mix → render, ~6 min, run in background):
   `shared/produce.sh <ep_dir> af_heart none EN-female` (or `am_michael ... EN-male`).
   The voice sets the pace: `build_vo.py` stretches any caption segment the voice needs more
   room for and writes `timing.js` (the page maps voiced time → base time), so animations,
   subtitles and music cues stay in sync without hand-retiming.
8. **Verify**: ffprobe (1080x1920, h264 + aac), `ebur128` ≈ -14 LUFS / peak ≤ -1.3 dBFS,
   grab 5 frames from the MP4 and look at them. You cannot hear audio: say so, and ask him
   to check with earphones.
9. **Deliver**: SendUserFile the MP4, short Malay summary, copy the approved final to
   `<series>/final/` (force-add, it is allowed in git), commit + push.

## Engine reference (`scripts/`)

| File | What it does |
|---|---|
| `render.js` | `stills` mode (1x PNGs for review) and `video` mode (4 parallel 2x workers → ffmpeg segments → concat + audio). Page must expose `window.ready` (resolves to duration) and `window.seek(t)` |
| `tts.py` | Kokoro TTS per line. `accent my` = Malaysian-English phoneme reshaping (kept for reference; the user rejected it) |
| `build_vo.py` | Places clips, computes the time-warp, writes `timing.js`, `voice.wav`, mapped `cues.json` |
| `music.py` | Synthesises the 88 BPM A-minor bed (kick, saturated 808 following Am9-Fmaj7-Cmaj7-G6, clap, swung hats, FM keys, 4-note pluck hook, riser, impacts) from cue times |
| `produce.sh` | Runs everything above + the mix (voice EQ/comp, sidechain duck, loudnorm -14 LUFS) |
| `new_episode.sh` | Scaffolds a series/episode |

Environment notes: needs Node + Playwright Chromium, ffmpeg, Python with
`kokoro-onnx soundfile scipy numpy` (`pip install` them if missing). Kokoro model files
(~350 MB) are fetched from GitHub releases into `~/.cache/kokoro` on first use.
Fonts: Inter / Inter Display must be installed locally (they are in Claude Code cloud images).

## Fine-tuning requests and where to change them

| He says | Change |
|---|---|
| "versi lelaki / perempuan" | rerun `produce.sh` with another voice (female `af_heart`, `af_bella`, `bf_emma`; male `am_michael`, `am_fenrir`, `bm_lewis`) |
| "laju sangat / slow sangat" | `speed` in `produce.sh`'s tts call (0.9-1.1) or per line `"speed"` in `lines.json`; scene gaps in `CAPS` |
| "bass kuat/kurang", "muzik perlahan" | `volume=0.58` in the mix; instrument gains in `music.py` |
| "pecah lagi" | check he sent it as a WhatsApp *Document*, FB "Upload HD"; raise CRF quality (lower number) in `render.js` |
| "buang watermark/logo" | `#wm` / `#logo` in the page |
