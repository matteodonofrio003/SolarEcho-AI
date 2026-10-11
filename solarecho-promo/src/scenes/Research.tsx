import {
  AbsoluteFill,
  CanvasImage,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Backdrop, C, Copy, Eyebrow, Title, clamp, ease } from "../design";
export const Research = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Backdrop />
      <div style={{ position: "absolute", left: 112, top: 220 }}>
        <Eyebrow>04 / ESPLORARE</Eyebrow>
        <Title delay={0.4} size={113} style={{ marginTop: 31 }}>
          Dai segnali.
          <br />
          Alla ricerca <span style={{ color: C.mint }}>AI.</span>
        </Title>
        <Copy delay={1.2} style={{ marginTop: 35, fontSize: 38 }}>
          Dataset reali per studiare
          <br />
          le anomalie del pannello.
        </Copy>
        <Copy
          delay={2.3}
          style={{
            marginTop: 45,
            fontSize: 26,
            letterSpacing: 2,
            color: C.amber,
            border: "1px solid #f5bb7060",
            borderRadius: 30,
            padding: "14px 24px",
            display: "inline-block",
          }}
        >
          MODELLO IN SVILUPPO
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          right: 110,
          top: 266,
          width: 790,
          border: "1px solid #ffffff30",
          borderRadius: 20,
          overflow: "hidden",
          boxShadow: "0 36px 70px #00000060",
          opacity: interpolate(f, [0.7 * fps, 1.7 * fps], [0, 1], clamp),
          scale: interpolate(f, [0.7 * fps, 8 * fps], [0.9, 1], {
            ...clamp,
            easing: ease,
          }),
          translate: `0px ${Math.sin(f / 75) * 7}px`,
        }}
      >
        <div
          style={{
            padding: "22px 27px",
            background: "#18343d",
            fontFamily: "SolarText",
            color: C.ink,
            display: "flex",
            justifyContent: "space-between",
            fontSize: 27,
          }}
        >
          <span>Anomaly explorer</span>
          <span style={{ color: C.mint, fontSize: 22 }}>EDGE IMPULSE</span>
        </div>
        <CanvasImage
          src={staticFile("training-plot.png")}
          premountFor={fps}
          style={{
            width: 790,
            height: 560,
            objectFit: "fill",
            display: "block",
          }}
        />
      </div>
      <Copy
        delay={3.2}
        style={{ position: "absolute", right: 170, bottom: 135, fontSize: 24 }}
      >
        Visualizzazione dai materiali di training del progetto
      </Copy>
    </AbsoluteFill>
  );
};
