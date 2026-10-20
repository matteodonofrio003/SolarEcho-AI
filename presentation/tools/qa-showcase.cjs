// Visual checks for the new composition only. Does not export an MP4.
const { bundle } = require("@remotion/bundler");
const {
  selectComposition,
  renderStill,
  openBrowser,
} = require("@remotion/renderer");
const fs = require("node:fs");
const path = require("node:path");

(async () => {
  const requestedFrames = process.argv.slice(2).map(Number);
  if (requestedFrames.some((frame) => !Number.isInteger(frame) || frame < 0 || frame >= 3240)) {
    throw new Error("Fotogramma fuori dalla composizione di 3.240 frame");
  }
  const destination = path.resolve("../video_output/showcase_componenti_v4/qa");
  fs.mkdirSync(destination, { recursive: true });
  const serveUrl = await bundle({
    entryPoint: path.resolve("src/index.ts"),
    enableCaching: true,
    rspack: true,
  });
  const browser = await openBrowser("chrome");
  try {
    const composition = await selectComposition({
      serveUrl,
      id: "SolarEcho-Showcase-108",
      puppeteerInstance: browser,
    });
    console.log(
      JSON.stringify({
        id: composition.id,
        frames: composition.durationInFrames,
        width: composition.width,
        height: composition.height,
        fps: composition.fps,
      }),
    );
    for (const frame of requestedFrames.length ? requestedFrames : [
      45, 330, 600, 690, 840, 990, 1170, 1290, 1380, 1590, 1920, 2220, 2670, 3150,
    ]) {
      await renderStill({
        serveUrl,
        composition,
        frame,
        puppeteerInstance: browser,
        output: path.join(destination, `frame-${frame}.png`),
        logLevel: "warn",
      });
      console.log(`Fotogramma ${frame} (${frame / composition.fps} s)`);
    }
  } finally {
    await browser.close({ silent: true });
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
