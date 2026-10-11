import {
  AbsoluteFill,
  Composition,
  Folder,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Problem } from "./Problem";
import { Solution } from "./Solution";
import { Demo } from "./Demo";
import { Economy } from "./Economy";
import { Innovation } from "./Innovation";
import { Finale } from "./Finale";
import { Narration } from "./Narration";
import { P } from "./visual";
export const SolarEchoHackathon = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: P.bg }}>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="01 Il problema"
          durationInFrames={555}
          premountFor={fps}
        >
          <Problem />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />
        <TransitionSeries.Sequence
          name="02 La soluzione"
          durationInFrames={615}
          premountFor={fps}
        >
          <Solution />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />
        <TransitionSeries.Sequence
          name="03 Demo autentica"
          durationInFrames={1275}
          premountFor={fps}
        >
          <Demo />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />
        <TransitionSeries.Sequence
          name="04 Valore economico"
          durationInFrames={675}
          premountFor={fps}
        >
          <Economy />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />
        <TransitionSeries.Sequence
          name="05 Innovazione"
          durationInFrames={315}
          premountFor={fps}
        >
          <Innovation />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />
        <TransitionSeries.Sequence
          name="06 SolarEcho AI"
          durationInFrames={180}
          premountFor={fps}
        >
          <Finale />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Audio
        src={staticFile("hackathon/original-score.wav")}
        volume={(frame) =>
          interpolate(
            frame,
            [0, 18, 500, 540, 3320, 3360, 3480, 3539],
            [0.16, 0.23, 0.23, 0.23, 0.23, 0.34, 0.34, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )
        }
      />
      <Narration />
      <div
        style={{
          position: "absolute",
          left: 112,
          right: 112,
          bottom: 30,
          height: 2,
          background: "#9ab4d112",
        }}
      >
        <div
          style={{
            width: `${(f / 3539) * 100}%`,
            height: 2,
            background: `linear-gradient(90deg,${P.cyan},${P.amber})`,
            opacity: 0.65,
          }}
        />
      </div>
      <AbsoluteFill
        style={{
          background: "#000",
          opacity: interpolate(f, [0, 18, 3500, 3539], [1, 0, 0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
export const HackathonCompositions = () => (
  <>
    <Composition
      id="SolarEcho-Hackathon"
      component={SolarEchoHackathon}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={3540}
    />
    <Folder name="Hackathon-Scene">
      <Composition
        id="H-Problem"
        component={Problem}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={555}
      />
      <Composition
        id="H-Solution"
        component={Solution}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={615}
      />
      <Composition
        id="H-Demo"
        component={Demo}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={1275}
      />
      <Composition
        id="H-Economy"
        component={Economy}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={675}
      />
      <Composition
        id="H-Innovation"
        component={Innovation}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={315}
      />
      <Composition
        id="H-Finale"
        component={Finale}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={180}
      />
    </Folder>
  </>
);
