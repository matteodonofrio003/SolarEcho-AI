import type React from "react";
import {
  AbsoluteFill,
  CanvasImage,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";

loadFont({
  family: "ShowcaseDisplay",
  url: staticFile("bahnschrift.ttf"),
  weight: "100 900",
});
loadFont({
  family: "ShowcaseText",
  url: staticFile("segoeui.ttf"),
  weight: "400",
});
loadFont({
  family: "ShowcaseText",
  url: staticFile("segoeuib.ttf"),
  weight: "700",
});

export const palette = {
  bg: "#07141d",
  ink: "#f4f6f1",
  mint: "#79f2cd",
  amber: "#ffcf76",
  muted: "#a9bec6",
};
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

export const FilmFrame = ({
  chapter,
  children,
}: {
  chapter: string;
  children: React.ReactNode;
}) => (
  <AbsoluteFill
    style={{
      background: palette.bg,
      color: palette.ink,
      fontFamily: "ShowcaseText",
      overflow: "hidden",
    }}
  >
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 70% 40%, #174a4438, transparent 70%)",
      }}
    />
    {children}
    <div
      style={{
        position: "absolute",
        top: 52,
        left: 90,
        right: 90,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontFamily: "ShowcaseDisplay",
        fontSize: 28,
        letterSpacing: 2,
        zIndex: 20,
      }}
    >
      <span style={{ color: palette.mint }}>{chapter}</span>
      <span
        style={{
          background: "#07141ddd",
          padding: "8px 14px",
          borderRadius: 5,
        }}
      >
        SolarEcho <span style={{ color: palette.mint }}>AI</span>
      </span>
    </div>
  </AbsoluteFill>
);

export const Title = ({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        fontFamily: "ShowcaseDisplay",
        fontSize: 148,
        fontWeight: 650,
        lineHeight: 1.04,
        letterSpacing: -5,
        opacity: interpolate(frame, [0, 15], [0, 1], clamp),
        translate: `0 ${interpolate(frame, [0, 20], [20, 0], { ...clamp, easing: Easing.out(Easing.cubic) })}px`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Note = ({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => (
  <div
    style={{ fontSize: 50, lineHeight: 1.34, color: palette.muted, ...style }}
  >
    {children}
  </div>
);

export const Evidence = ({
  children,
  amber = false,
  style,
}: {
  children: React.ReactNode;
  amber?: boolean;
  style?: React.CSSProperties;
}) => (
  <div
    style={{
      fontFamily: "ShowcaseDisplay",
      fontSize: 30,
      letterSpacing: 1.3,
      color: amber ? palette.amber : palette.mint,
      borderLeft: `4px solid ${amber ? palette.amber : palette.mint}`,
      paddingLeft: 18,
      ...style,
    }}
  >
    {children}
  </div>
);

export const StillPhoto = ({
  file,
  style,
}: {
  file: string;
  style: React.CSSProperties;
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <div style={{ position: "absolute", overflow: "hidden", ...style }}>
      <CanvasImage
        src={staticFile(`footage/${file}.jpg`)}
        premountFor={fps}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          scale: interpolate(frame, [0, durationInFrames], [1, 1.035], clamp),
        }}
      />
    </div>
  );
};
