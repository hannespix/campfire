# Playing with Fire · Campfire V2

Open [the launcher](index.html) for the schedule, demo cues and tools. The English talk runs from minute 00 to 60. Allow another 15 minutes for Booth Builder and the PixiNotes MCP demo, then 15 minutes for questions and one possible next test.

- Open [the standalone deck](talk.html) in a browser tab. Press **S** for the Reveal speaker window and **T** for the light theme.
- Keep [the presentation PDF](talk.pdf) within reach. Slide 15 shows the prepared booth comparison if the live simulation is unavailable.
- Drag [the demo board](campfire-v2.pixiboard.json) into PixiNotes. Rehearse the MCP write in a local test copy with a sync folder. The first route through the board leads from Booth Builder to **MCP example**, **Your questions** and **Next test**. The other tools are available below the route. [PixiNotes MCP setup](https://github.com/hannespix/pixinotes/blob/HEAD/docs/MCP.md)
- Test any guest QR with a phone on the venue network. The stage run supports taking questions aloud.

The capacity case uses an illustrated spreadsheet reconstruction and a crop of the actual vave.log interface running with a controlled example fixture. Both use the same fictional assignments. [Capacity plan project notes](https://github.com/hannespix/vave.log/blob/f0447dd67dd67f7b06e948faee2fb41fbdd35937/STATE.md#L495-L525) · [Example fixture](https://github.com/hannespix/vave.log/blob/f0447dd67dd67f7b06e948faee2fb41fbdd35937/tests/e2e/capacity-plan.spec.ts#L5-L74)

## Regenerate

Edit the slides in [talk.slides.html](src/talk.slides.html), the layouts in [talk.css](src/talk.css) or the standalone pages in [modules](modules/). Run the builder from the repository root.

```sh
python3 v2/build.py
python3 -m http.server 8767
```

The builder regenerates `talk.html` and the PixiNotes export using the existing Reveal runtime and pixel kit. It embeds the images in the deck and the eight tools in the export. After updating the slides, open `http://localhost:8767/v2/talk.html?print-pdf` in Chromium and print with background graphics to update `talk.pdf`.

Campfire artwork and runtime credits are in the [original README](../README.md).
