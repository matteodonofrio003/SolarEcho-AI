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
  Eyebrow,
  SolarPanel,
  Title,
  clamp,
  ease,
} from "../design";
export const Opening = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Backdrop warm />
      <div
        style={{
          position: "absolute",
          width: 660,
          height: 660,
          right: 32,
          top: 110,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 37% 32%,#ffe3a5,#be7f36 36%,#493b22 63%,#11252a 73%)",
          opacity: 0.43,
          scale: interpolate(f, [0, 8 * fps], [0.85, 1.05], clamp),
        }}
      />
      <svg
        width="950"
        height="950"
        style={{ position: "absolute", right: -100, top: -5, opacity: 0.25 }}
      >
        <circle cx="475" cy="475" r="420" fill="none" stroke={C.amber} />
        <circle
          cx="475"
          cy="475"
          r="449"
          fill="none"
          stroke={C.amber}
          strokeDasharray="2 19"
        />
      </svg>
      <div style={{ position: "absolute", left: 112, top: 246, zIndex: 2 }}>
        <Eyebrow>IL FOTOVOLTAICO HA UNA NUOVA VOCE</Eyebrow>
        <Title delay={0.35} size={138} style={{ marginTop: 39 }}>
          Ogni pannello
          <br />
          ha una <span style={{ color: C.mint }}>voce.</span>
        </Title>
        <Copy delay={1.5} style={{ marginTop: 35, fontSize: 40 }}>
          SolarEcho AI la ascolta.
        </Copy>
        <div
          style={{
            width: 100,
            height: 3,
            marginTop: 42,
            background: C.amber,
            scale: interpolate(f, [2 * fps, 3 * fps], [0, 1], {
              ...clamp,
              easing: ease,
            }),
            transformOrigin: "left",
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          right: 5,
          top: 360,
          opacity: interpolate(f, [0.2 * fps, 1.6 * fps], [0, 1], clamp),
          scale: interpolate(f, [0, 8 * fps], [0.9, 1], {
            ...clamp,
            easing: ease,
          }),
        }}
      >
        <SolarPanel width={930} />
      </div>
      <Copy
        delay={3}
        style={{
          position: "absolute",
          left: 115,
          bottom: 155,
          fontSize: 26,
          letterSpacing: 2,
        }}
      >
        ENERGIA · VIBRAZIONI · DATI
      </Copy>
    </AbsoluteFill>
  );
};
