import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import signal from "./data/signal.json";
export const C = {
  bg: "#06151a",
  ink: "#eff8f4",
  muted: "#91acae",
  mint: "#74e3c4",
  amber: "#f5bb70",
  blue: "#81aafa",
};
export const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
export const Backdrop: React.FC<{ warm?: boolean }> = ({ warm = false }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        overflow: "hidden",
        color: C.ink,
        fontFamily: "SolarText,sans-serif",
      }}
    >
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at ${65 + Math.sin(f / 170) * 6}% 38%,${warm ? "#49352866" : "#164a4355"} 0%,transparent 52%),radial-gradient(ellipse at 15% 90%,#12384366,transparent 52%)`,
        }}
      />
      <AbsoluteFill
        style={{
          opacity: 0.13,
          backgroundImage:
            "linear-gradient(#8ec7bb20 1px,transparent 1px),linear-gradient(90deg,#8ec7bb20 1px,transparent 1px)",
          backgroundSize: "96px 96px",
          maskImage: "linear-gradient(transparent,black)",
        }}
      />
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", opacity: 0.4 }}
      >
        {Array.from({ length: 40 }, (_, i) => (
          <circle
            key={i}
            cx={(i * 467 + 127) % 1920}
            cy={(i * 233 + 119) % 960}
            r={i % 5 === 0 ? 2 : 1}
            fill={i % 4 === 0 ? C.amber : C.mint}
            opacity={0.2 + (0.5 * (1 + Math.sin(f / 65 + i))) / 2}
          />
        ))}
      </svg>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center,transparent 40%,#020b1060 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
export const Title: React.FC<{
  children: React.ReactNode;
  delay?: number;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, size = 116, color = C.ink, style }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        fontFamily: "SolarDisplay,sans-serif",
        fontWeight: 600,
        fontSize: size,
        letterSpacing: -3.8,
        lineHeight: 1.04,
        color,
        ...style,
        opacity: interpolate(
          f,
          [delay * fps, (delay + 0.75) * fps],
          [0, 1],
          clamp,
        ),
        translate: `0px ${interpolate(f, [delay * fps, (delay + 1.1) * fps], [65, 0], { ...clamp, easing: ease })}px`,
        filter: `blur(${interpolate(f, [delay * fps, (delay + 0.65) * fps], [9, 0], clamp)}px)`,
      }}
    >
      {children}
    </div>
  );
};
export const Copy: React.FC<{
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0.75, style }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        fontFamily: "SolarText,sans-serif",
        fontSize: 38,
        lineHeight: 1.45,
        color: C.muted,
        ...style,
        opacity: interpolate(
          f,
          [delay * fps, (delay + 0.65) * fps],
          [0, 1],
          clamp,
        ),
        translate: `0px ${interpolate(f, [delay * fps, (delay + 0.8) * fps], [24, 0], { ...clamp, easing: ease })}px`,
      }}
    >
      {children}
    </div>
  );
};
export const Eyebrow: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div
    style={{
      color: C.mint,
      fontFamily: "SolarDisplay,sans-serif",
      fontSize: 24,
      fontWeight: 600,
      letterSpacing: 4,
      ...style,
    }}
  >
    {children}
  </div>
);
export const EchoMark: React.FC<{ size?: number }> = ({ size = 52 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
    <circle cx="50" cy="50" r="36" stroke={C.mint} strokeWidth="3" />
    <circle
      cx="50"
      cy="50"
      r="23"
      stroke={C.mint}
      strokeWidth="2"
      opacity=".5"
    />
    <path
      d="M13 50H29L36 35L44 65L53 25L62 59L69 44L75 50H87"
      stroke={C.mint}
      strokeWidth="5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
export const Waveform: React.FC<{
  width?: number;
  height?: number;
  progress?: number;
  light?: boolean;
}> = ({ width = 1660, height = 270, progress = 1, light = false }) => {
  const max = 0.46,
    pad = 18,
    base = height / 2;
  const paths = signal.axes.map((a) =>
    a
      .map(
        (v, i) =>
          `${i ? "L" : "M"}${(pad + (i / (a.length - 1)) * (width - 2 * pad)).toFixed(2)},${(base - (v / max) * (height / 2 - 30)).toFixed(2)}`,
      )
      .join(" "),
  );
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {[0.15, 0.5, 0.85].map((y, i) => (
        <line
          key={i}
          x1="0"
          x2={width}
          y1={height * y}
          y2={height * y}
          stroke={light ? "#d7e4e2" : "#ffffff15"}
          strokeDasharray={i === 1 ? "0" : "5 10"}
        />
      ))}
      <line
        x1={pad + (0.2 / 2.2) * (width - 2 * pad)}
        x2={pad + (0.2 / 2.2) * (width - 2 * pad)}
        y1="0"
        y2={height}
        stroke={light ? "#dc964c" : C.amber}
        strokeDasharray="5 8"
        opacity=".5"
      />
      {paths.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="none"
          stroke={
            [
              light ? "#078d88" : C.mint,
              light ? "#d38a36" : C.amber,
              light ? "#687ad5" : C.blue,
            ][i]
          }
          strokeWidth={light ? 2.5 : 3.5}
          strokeLinejoin="round"
          pathLength="1"
          strokeDasharray="1"
          strokeDashoffset={1 - progress}
          opacity={i === 2 ? 1 : 0.6}
        />
      ))}
    </svg>
  );
};
export const SolarPanel: React.FC<{ width?: number }> = ({ width = 820 }) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        width,
        height: width * 0.7,
        position: "relative",
        translate: `0px ${Math.sin(f / 70) * 9}px`,
      }}
    >
      <svg
        width={width}
        height={width * 0.7}
        viewBox="0 0 900 630"
        style={{ overflow: "visible" }}
      >
        <defs>
          <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#d4e8df" />
            <stop offset=".35" stopColor="#64928d" />
            <stop offset=".75" stopColor="#192f39" />
            <stop offset="1" stopColor="#95b8ae" />
          </linearGradient>
          <linearGradient id="cell" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#224850" />
            <stop offset=".45" stopColor="#0b2734" />
            <stop offset="1" stopColor="#14333d" />
          </linearGradient>
          <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
            <stop stopColor="#d2fff5" stopOpacity="0" />
            <stop offset=".48" stopColor="#d2fff5" stopOpacity=".21" />
            <stop offset=".55" stopColor="#d2fff5" stopOpacity=".07" />
            <stop offset="1" stopColor="#d2fff5" stopOpacity="0" />
          </linearGradient>
        </defs>
        <ellipse
          cx="463"
          cy="540"
          rx="350"
          ry="55"
          fill="#020a11"
          opacity=".65"
        />
        <path d="M37 403L420 149L874 368L487 623Z" fill="#13282f" />
        <path d="M37 383L420 129L874 348L487 603Z" fill="url(#frame)" />
        <g transform="matrix(.72,.35,-.62,.41,420,144)">
          <rect width="600" height="590" fill="#081b27" />
          {Array.from({ length: 30 }, (_, i) => {
            const x = i % 5,
              y = Math.floor(i / 5);
            return (
              <g key={i}>
                <rect
                  x={x * 120 + 5}
                  y={y * 98 + 5}
                  width="110"
                  height="88"
                  rx="7"
                  fill="url(#cell)"
                  stroke="#417575"
                  strokeWidth="1.3"
                />
                {[22, 44, 66, 88].map((v) => (
                  <line
                    key={v}
                    x1={x * 120 + v}
                    x2={x * 120 + v}
                    y1={y * 98 + 6}
                    y2={y * 98 + 92}
                    stroke="#709b9d"
                    strokeWidth=".6"
                    opacity=".55"
                  />
                ))}
                <line
                  x1={x * 120 + 5}
                  x2={x * 120 + 115}
                  y1={y * 98 + 49}
                  y2={y * 98 + 49}
                  stroke="#bcd3ce"
                  strokeWidth="1"
                  opacity=".35"
                />
              </g>
            );
          })}
          <rect width="600" height="590" fill="url(#shine)" />
          <rect
            width="600"
            height="590"
            fill="none"
            stroke={C.mint}
            strokeWidth="2"
          />
        </g>
        {[0, 1, 2].map((i) => (
          <ellipse
            key={i}
            cx="493"
            cy="363"
            rx={80 + ((f + i * 50) % 160) * 1.7}
            ry={30 + ((f + i * 50) % 160) * 0.6}
            stroke={C.mint}
            strokeWidth="1.8"
            fill="none"
            opacity={(1 - ((f + i * 50) % 160) / 160) * 0.55}
          />
        ))}
        <circle cx="493" cy="363" r="6" fill={C.mint} />
      </svg>
    </div>
  );
};
