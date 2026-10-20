import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  Composition,
  Folder,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Hook } from "./Hook";
import { Problem } from "./Problem";
import { Hardware } from "./Hardware";
import { Capture } from "./Capture";
import { Analysis } from "./Analysis";
import { Synthetic } from "./Synthetic";
import { Action } from "./Action";
import { Closing } from "./Closing";
import { clamp, palette } from "./visual";

export const SolarEchoShowcase = () => {
  const { fps, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: palette.bg }}>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="01 - Impatto subito"
          durationInFrames={190}
          premountFor={fps}
        >
          <Hook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="02 - Il problema"
          durationInFrames={310}
          premountFor={fps}
        >
          <Problem />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="03 - Arduino UNO Q"
          durationInFrames={910}
          premountFor={fps}
        >
          <Hardware />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="04 - Acquisizione"
          durationInFrames={430}
          premountFor={fps}
        >
          <Capture />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="05 - Inferenza reale"
          durationInFrames={340}
          premountFor={fps}
        >
          <Analysis />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="06 - Test sintetico dichiarato"
          durationInFrames={370}
          premountFor={fps}
        >
          <Synthetic />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="07 - LED e Telegram"
          durationInFrames={400}
          premountFor={fps}
        >
          <Action />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence
          name="08 - SolarEcho AI"
          durationInFrames={360}
          premountFor={fps}
        >
          <Closing />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Audio
        name="Musica originale - 120 BPM - nessuna voce"
        src={staticFile("exploded/score-hardware-v4.wav")}
        premountFor={fps}
        volume={0.72}
      />
      <AbsoluteFill
        style={{
          background: "#000",
          pointerEvents: "none",
          opacity: interpolate(
            frame,
            [durationInFrames - 26, durationInFrames - 1],
            [0, 1],
            clamp,
          ),
        }}
      />
    </AbsoluteFill>
  );
};

export const ShowcaseCompositions = () => (
  <>
    <Composition
      id="SolarEcho-Showcase-108"
      component={SolarEchoShowcase}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={3240}
    />
    <Folder name="Showcase-Scene">
      <Composition
        id="S-Hook"
        component={Hook}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={190}
      />
      <Composition
        id="S-Problem"
        component={Problem}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={310}
      />
      <Composition
        id="S-Hardware"
        component={Hardware}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={910}
      />
      <Composition
        id="S-Capture"
        component={Capture}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={430}
      />
      <Composition
        id="S-Analysis"
        component={Analysis}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={340}
      />
      <Composition
        id="S-Synthetic"
        component={Synthetic}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={370}
      />
      <Composition
        id="S-Action"
        component={Action}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={400}
      />
      <Composition
        id="S-Closing"
        component={Closing}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={360}
      />
    </Folder>
  </>
);
