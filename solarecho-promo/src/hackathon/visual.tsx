import React from "react";
import {
  AbsoluteFill,
  CanvasImage,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { Video } from "@remotion/media";

export const P = {
  bg: "#040b19",
  panel: "#0c192b",
  cyan: "#50e4ee",
  amber: "#ffbf58",
  white: "#f3f7fd",
  muted: "#a6b7cd",
};
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const enter = (f: number, d = 0) =>
  interpolate(f, [d, d + 22], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
export const Stage = ({ children }: { children: React.ReactNode }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: P.bg,
        color: P.white,
        fontFamily: "SolarText",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at ${65 + Math.sin(f / 200) * 10}% 25%,#123a503b,transparent 62%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.15,
          backgroundImage:
            "linear-gradient(#5fe2f110 1px,transparent 1px),linear-gradient(90deg,#5fe2f110 1px,transparent 1px)",
          backgroundSize: "100px 100px",
        }}
      />
      {children}
    </AbsoluteFill>
  );
};
export const Kicker = ({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        color: P.cyan,
        fontFamily: "SolarDisplay",
        fontSize: 24,
        letterSpacing: 4,
        opacity: enter(f, delay),
      }}
    >
      {children}
    </div>
  );
};
export const Head = ({
  children,
  size = 96,
  delay = 8,
}: {
  children: React.ReactNode;
  size?: number;
  delay?: number;
}) => {
  const f = useCurrentFrame();
  const e = enter(f, delay);
  return (
    <div
      style={{
        fontFamily: "SolarDisplay",
        fontSize: size,
        fontWeight: 650,
        lineHeight: 1.06,
        letterSpacing: -3,
        opacity: e,
        transform: `translateY(${(1 - e) * 30}px)`,
        marginTop: 26,
      }}
    >
      {children}
    </div>
  );
};
export const Text = ({
  children,
  delay = 20,
  size = 34,
}: {
  children: React.ReactNode;
  delay?: number;
  size?: number;
}) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        fontSize: size,
        lineHeight: 1.38,
        color: P.muted,
        opacity: enter(f, delay),
        marginTop: 30,
      }}
    >
      {children}
    </div>
  );
};
export const Tag = ({
  children,
  color = P.cyan,
}: {
  children: React.ReactNode;
  color?: string;
}) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 12,
      padding: "13px 20px",
      border: `1px solid ${color}55`,
      background: `${P.bg}dd`,
      borderRadius: 5,
      fontFamily: "SolarDisplay",
      fontSize: 22,
      letterSpacing: 1.5,
      color,
    }}
  >
    <span
      style={{ width: 7, height: 7, borderRadius: 50, background: color }}
    />
    {children}
  </div>
);
export const Photo = ({
  file,
  style,
  zoom = 1.06,
}: {
  file: string;
  style?: React.CSSProperties;
  zoom?: number;
}) => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const z = interpolate(f, [0, durationInFrames], [1, zoom], clamp);
  return (
    <div style={{ position: "absolute", overflow: "hidden", ...style }}>
      <CanvasImage
        src={staticFile("hackathon/" + file + ".jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${z})`,
          filter: "contrast(1.04) saturate(.93)",
        }}
      />
    </div>
  );
};
export const Shot = ({
  file,
  start = 0,
  rate = 1,
  style,
  fit = "cover",
  sound = false,
}: {
  file: string;
  start?: number;
  rate?: number;
  style?: React.CSSProperties;
  fit?: "cover" | "contain";
  sound?: boolean;
}) => {
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        overflow: "hidden",
        background: "#08121e",
        ...style,
      }}
    >
      <Video
        src={staticFile("hackathon/" + file + ".mp4")}
        trimBefore={Math.round(start * fps)}
        playbackRate={rate}
        muted={!sound}
        volume={sound ? 0.35 : 0}
        objectFit={fit}
        style={{
          width: "100%",
          height: "100%",
          filter: "contrast(1.025) saturate(.95) brightness(1.012)",
        }}
      />
    </div>
  );
};
// Crop the genuine recording using CSS only; all original data and labels stay unaltered.
export const Screen = ({
  start,
  x,
  y,
  w,
  h,
  style,
  snapshot,
  holdAfter = 0,
}: {
  start: number;
  x: number;
  y: number;
  w: number;
  h: number;
  style: React.CSSProperties;
  snapshot?: string;
  holdAfter?: number;
}) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const outWidth = Number(style.width ?? 1500);
  const scale = outWidth / w;
  return (
    <div
      style={{
        position: "absolute",
        overflow: "hidden",
        background: "#edf5f5",
        borderRadius: 12,
        boxShadow: "0 30px 80px #0008",
        ...style,
      }}
    >
      {snapshot && frame >= holdAfter * fps ? (
        <CanvasImage
          src={staticFile("hackathon/" + snapshot + ".png")}
          style={{
            position: "absolute",
            width: 1828 * scale,
            height: 924 * scale,
            left: -x * scale,
            top: -y * scale,
            maxWidth: "none",
          }}
        />
      ) : (
        <Video
          src={staticFile("hackathon/dashboard.mp4")}
          trimBefore={Math.round(start * fps)}
          muted
          style={{
            position: "absolute",
            width: 1828 * scale,
            height: 924 * scale,
            left: -x * scale,
            top: -y * scale,
            maxWidth: "none",
          }}
        />
      )}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: outWidth,
          height: h * scale,
          border: "1px solid #ffffff22",
          boxSizing: "border-box",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
export const Flow = ({
  active = 0,
  top = 760,
}: {
  active?: number;
  top?: number;
}) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        left: 110,
        right: 110,
        top,
        display: "flex",
        alignItems: "center",
        gap: 20,
      }}
    >
      {["IMPATTO", "VIBRAZIONE", "ANALISI AI", "SEGNALAZIONE"].map((s, i) => (
        <React.Fragment key={s}>
          {i > 0 ? (
            <div
              style={{ color: i <= active ? P.cyan : "#233750", fontSize: 44 }}
            >
              →
            </div>
          ) : null}
          <div
            style={{
              flex: 1,
              padding: "20px 16px",
              background: i === active ? "#13323f" : "#0b1729",
              borderTop: `2px solid ${i <= active ? P.cyan : "#21334b"}`,
              color: i <= active ? P.white : P.muted,
              opacity: enter(f, i * 4),
              fontFamily: "SolarDisplay",
              letterSpacing: 2,
              fontSize: 23,
            }}
          >
            <div style={{ fontSize: 15, color: P.cyan, marginBottom: 8 }}>
              0{i + 1}
            </div>
            {s}
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};
export const Ripple = ({ at = 35 }: { at?: number }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 350, top: 590 }}>
      {[0, 1, 2].map((i) => {
        const p = interpolate(f, [at + i * 6, at + 70 + i * 6], [0, 1], clamp);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 650 * p,
              height: 650 * p,
              marginLeft: -325 * p,
              marginTop: -325 * p,
              border: `2px solid ${P.cyan}`,
              borderRadius: "50%",
              opacity: (1 - p) * 0.6,
            }}
          />
        );
      })}
    </div>
  );
};
