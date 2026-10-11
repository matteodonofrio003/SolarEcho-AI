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
  Title,
  Waveform,
  clamp,
  ease,
} from "../design";
export const Capture = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Backdrop />
      <div style={{ position: "absolute", left: 112, top: 206 }}>
        <Eyebrow>01 / ASCOLTARE</Eyebrow>
        <Title delay={0.4} size={122} style={{ marginTop: 31 }}>
          Un impatto.
          <br />
          Una <span style={{ color: C.mint }}>firma.</span>
        </Title>
        <Copy delay={1.2} style={{ marginTop: 26 }}>
          La risposta del pannello, catturata su tre assi.
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          right: 180,
          top: 260,
          opacity: interpolate(f, [1.1 * fps, 2 * fps], [0, 1], clamp),
        }}
      >
        <div
          style={{
            fontFamily: "SolarDisplay",
            fontSize: 134,
            letterSpacing: -6,
            color: C.ink,
          }}
        >
          2,2
          <span style={{ fontSize: 67, color: C.mint, marginLeft: 13 }}>s</span>
        </div>
        <Copy delay={1.3} style={{ fontSize: 29 }}>
          finestra di acquisizione
        </Copy>
        <div style={{ color: C.muted, fontSize: 25, marginTop: 25 }}>
          200 ms prima · 2 s dopo
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 112,
          top: 610,
          width: 1696,
          padding: "22px 18px",
          borderTop: "1px solid #74e3c438",
          borderBottom: "1px solid #74e3c425",
          opacity: interpolate(f, [1.5 * fps, 2 * fps], [0, 1], clamp),
        }}
      >
        <Waveform
          width={1660}
          height={242}
          progress={interpolate(f, [1.7 * fps, 5.4 * fps], [0, 1], {
            ...clamp,
            easing: ease,
          })}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontFamily: "SolarText",
            fontSize: 24,
            color: C.muted,
            marginTop: 14,
          }}
        >
          <span>−200 ms</span>
          <span style={{ color: C.amber }}>TRIGGER PIEZO</span>
          <span>+2.000 ms</span>
        </div>
      </div>
      <Copy
        delay={3.5}
        style={{ position: "absolute", left: 130, bottom: 88, fontSize: 25 }}
      >
        <span style={{ color: C.mint }}>X</span> &nbsp;{" "}
        <span style={{ color: C.amber }}>Y</span> &nbsp;{" "}
        <span style={{ color: C.blue }}>Z</span> &nbsp; / &nbsp; Acquisizione
        reale dal prototipo
      </Copy>
    </AbsoluteFill>
  );
};
