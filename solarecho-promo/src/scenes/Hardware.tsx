import {
  AbsoluteFill,
  CanvasImage,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Backdrop, C, Copy, Eyebrow, Title, clamp, ease } from "../design";
export const Hardware = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Backdrop />
      <div style={{ position: "absolute", left: 112, top: 206 }}>
        <Eyebrow>02 / CONNETTERE</Eyebrow>
        <Title delay={0.3} size={112} style={{ marginTop: 31 }}>
          Il mondo fisico.
          <br />
          Diventa <span style={{ color: C.mint }}>dato.</span>
        </Title>
        <Copy delay={1.1} style={{ marginTop: 35, fontSize: 36 }}>
          Sensori e acquisizione sulla Arduino UNO Q.
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          left: 116,
          top: 597,
          width: 690,
          display: "flex",
          flexDirection: "column",
          gap: 35,
        }}
      >
        <Copy
          delay={1.4}
          style={{
            fontSize: 35,
            color: C.ink,
            display: "flex",
            alignItems: "center",
            gap: 26,
          }}
        >
          <span
            style={{ color: C.mint, fontSize: 23, letterSpacing: 2, width: 70 }}
          >
            IMU
          </span>{" "}
          Vibrazioni X / Y / Z
        </Copy>
        <Copy
          delay={1.9}
          style={{
            fontSize: 35,
            color: C.ink,
            display: "flex",
            alignItems: "center",
            gap: 26,
          }}
        >
          <span
            style={{
              color: C.amber,
              fontSize: 23,
              letterSpacing: 1,
              width: 70,
            }}
          >
            PIEZO
          </span>{" "}
          Trigger dell’impatto
        </Copy>
        <Copy
          delay={2.4}
          style={{
            fontSize: 35,
            color: C.ink,
            display: "flex",
            alignItems: "center",
            gap: 26,
          }}
        >
          <span style={{ color: C.blue, fontSize: 22, width: 70 }}>INA219</span>{" "}
          Misure elettriche
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          right: 52,
          top: 292,
          width: 925,
          height: 590,
          background: "radial-gradient(ellipse,#174a4260,transparent 64%)",
          borderRadius: "50%",
          opacity: interpolate(f, [0.6 * fps, 1.6 * fps], [0, 1], clamp),
        }}
      />
      <CanvasImage
        src={staticFile("housing.png")}
        premountFor={fps}
        style={{
          position: "absolute",
          width: 900,
          height: 500,
          objectFit: "contain",
          right: 85,
          top: 350,
          opacity: interpolate(f, [0.6 * fps, 1.6 * fps], [0, 1], clamp),
          scale: interpolate(f, [0, 8 * fps], [0.89, 1.04], {
            ...clamp,
            easing: ease,
          }),
          translate: `0px ${Math.sin(f / 65) * 9}px`,
          filter: "drop-shadow(0px 38px 24px #01090e80)",
        }}
      />
      <Copy
        delay={3}
        style={{
          position: "absolute",
          right: 250,
          bottom: 126,
          fontSize: 27,
          letterSpacing: 1,
        }}
      >
        Involucro del prototipo
      </Copy>
    </AbsoluteFill>
  );
};
