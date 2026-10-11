import React from "react";
import {
  AbsoluteFill,
  Composition,
  Folder,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { wipe } from "@remotion/transitions/wipe";
import { Opening } from "./scenes/Opening";
import { Capture } from "./scenes/Capture";
import { Hardware } from "./scenes/Hardware";
import { Dashboard } from "./scenes/Dashboard";
import { Research } from "./scenes/Research";
import { Closing } from "./scenes/Closing";
import { C, EchoMark, clamp } from "./design";

loadFont({
  family: "SolarDisplay",
  url: staticFile("bahnschrift.ttf"),
  weight: "100 900",
});
loadFont({
  family: "SolarText",
  url: staticFile("segoeui.ttf"),
  weight: "400",
});
loadFont({
  family: "SolarText",
  url: staticFile("segoeuib.ttf"),
  weight: "700",
});

export const SolarEchoPromo: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{ background: C.bg, color: C.ink, fontFamily: "SolarText" }}
    >
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="Ogni pannello ha una voce"
          durationInFrames={8 * fps}
          premountFor={fps}
        >
          <Opening />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: fps })}
        />
        <TransitionSeries.Sequence
          name="La firma vibrazionale"
          durationInFrames={9 * fps}
          premountFor={fps}
        >
          <Capture />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-right" })}
          timing={linearTiming({ durationInFrames: fps })}
        />
        <TransitionSeries.Sequence
          name="Hardware e involucro"
          durationInFrames={8 * fps}
          premountFor={fps}
        >
          <Hardware />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: fps })}
        />
        <TransitionSeries.Sequence
          name="La dashboard locale"
          durationInFrames={9 * fps}
          premountFor={fps}
        >
          <Dashboard />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-left" })}
          timing={linearTiming({ durationInFrames: fps })}
        />
        <TransitionSeries.Sequence
          name="Ricerca AI"
          durationInFrames={8 * fps}
          premountFor={fps}
        >
          <Research />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: fps })}
        />
        <TransitionSeries.Sequence
          name="Ascolta l'energia"
          durationInFrames={8 * fps}
          premountFor={fps}
        >
          <Closing />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Audio
        src={staticFile("solarecho-original-score.wav")}
        premountFor={fps}
        volume={0.85}
      />
      <div
        style={{
          position: "absolute",
          top: 85,
          left: 111,
          display: "flex",
          alignItems: "center",
          gap: 14,
          opacity: interpolate(
            f,
            [0, fps, 37 * fps, 38 * fps],
            [0, 1, 1, 0],
            clamp,
          ),
        }}
      >
        <EchoMark size={43} />
        <span
          style={{
            fontFamily: "SolarDisplay",
            fontSize: 29,
            letterSpacing: -0.3,
          }}
        >
          SolarEcho <span style={{ color: C.mint }}>AI</span>
        </span>
      </div>
      <div
        style={{
          position: "absolute",
          top: 96,
          right: 112,
          fontFamily: "SolarDisplay",
          fontSize: 20,
          letterSpacing: 3,
          color: C.muted,
          opacity: interpolate(
            f,
            [0, fps, 37 * fps, 38 * fps],
            [0, 0.85, 0.85, 0],
            clamp,
          ),
        }}
      >
        ASCOLTA L’ENERGIA
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 65,
          left: 112,
          right: 112,
          height: 2,
          background: "#ffffff0c",
        }}
      >
        <div
          style={{
            height: 2,
            width: `${(f / 1349) * 100}%`,
            background: `linear-gradient(90deg,${C.mint},${C.amber})`,
            opacity: 0.6,
          }}
        />
      </div>
      <AbsoluteFill
        style={{
          background: "#020a0d",
          opacity: interpolate(
            f,
            [0, 0.6 * fps, 43.8 * fps, 45 * fps - 1],
            [1, 0, 0, 1],
            clamp,
          ),
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="SolarEcho-Promo"
      component={SolarEchoPromo}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1350}
    />
    <Folder name="Scene">
      <Composition
        id="Opening"
        component={Opening}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={240}
      />
      <Composition
        id="Capture"
        component={Capture}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={270}
      />
      <Composition
        id="Hardware"
        component={Hardware}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={240}
      />
      <Composition
        id="Dashboard"
        component={Dashboard}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={270}
      />
      <Composition
        id="Research"
        component={Research}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={240}
      />
      <Composition
        id="Closing"
        component={Closing}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={240}
      />
    </Folder>
  </>
);
