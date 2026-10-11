import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  Backdrop,
  C,
  Copy,
  EchoMark,
  Eyebrow,
  Title,
  clamp,
  ease,
} from "../design";
export const Closing = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Backdrop warm />
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", opacity: 0.3 }}
      >
        {[0, 1, 2, 3].map((i) => (
          <ellipse
            key={i}
            cx="960"
            cy="470"
            rx={260 + i * 100 + f * 0.25}
            ry={260 + i * 100 + f * 0.25}
            fill="none"
            stroke={i % 2 ? C.amber : C.mint}
            opacity={0.7 - i * 0.15}
          />
        ))}
      </svg>
      <div
        style={{
          position: "absolute",
          top: 206,
          left: 0,
          width: "100%",
          display: "flex",
          alignItems: "center",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            opacity: interpolate(f, [0.4 * fps, 1.3 * fps], [0, 1], clamp),
            scale: interpolate(f, [0.4 * fps, 1.8 * fps], [0.6, 1], {
              ...clamp,
              easing: ease,
            }),
          }}
        >
          <EchoMark size={118} />
        </div>
        <Title
          delay={0.65}
          size={154}
          style={{ marginTop: 20, letterSpacing: -5 }}
        >
          SolarEcho <span style={{ color: C.mint }}>AI</span>
        </Title>
        <Title
          delay={1.2}
          size={76}
          style={{ marginTop: 30, letterSpacing: -1.9, color: "#b5cfc8" }}
        >
          Ascolta l’energia.
        </Title>
        <Copy
          delay={2}
          style={{
            fontSize: 32,
            color: C.ink,
            marginTop: 58,
            border: "1px solid #74e3c45c",
            borderRadius: 50,
            padding: "18px 40px",
            background: "#0b2b2b",
          }}
        >
          Esplora il prototipo. &nbsp; ↗
        </Copy>
        <Eyebrow style={{ marginTop: 46, fontSize: 23, color: C.muted }}>
          BEYOND SOLAR / HACKTURIN 2026
        </Eyebrow>
      </div>
      <Copy
        delay={3}
        style={{
          position: "absolute",
          bottom: 130,
          width: "100%",
          textAlign: "center",
          fontSize: 27,
        }}
      >
        Prototipo sperimentale · Modello AI in sviluppo
      </Copy>
    </AbsoluteFill>
  );
};
