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
  Waveform,
  clamp,
  ease,
} from "../design";
const Metric = ({
  label,
  unit,
  highlight = false,
}: {
  label: string;
  unit: string;
  highlight?: boolean;
}) => (
  <div
    style={{
      flex: 1,
      background: highlight ? "#e4f4ee" : "white",
      border: "1px solid #dbe7e5",
      borderRadius: 12,
      padding: "22px 28px",
    }}
  >
    <div style={{ color: "#637b80", fontSize: 22, letterSpacing: 1.5 }}>
      {label}
    </div>
    <div
      style={{
        color: highlight ? "#126651" : "#17303a",
        fontSize: 55,
        fontFamily: "SolarDisplay",
        marginTop: 10,
      }}
    >
      — <span style={{ fontSize: 29, color: "#6b8083" }}>{unit}</span>
    </div>
  </div>
);
export const Dashboard = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Backdrop />
      <div style={{ position: "absolute", left: 112, top: 191 }}>
        <Eyebrow>03 / OSSERVARE</Eyebrow>
        <Title delay={0.35} size={119} style={{ marginTop: 26 }}>
          Tutto. <span style={{ color: C.mint }}>A vista.</span>
        </Title>
        <Copy delay={0.95} style={{ marginTop: 19, fontSize: 37 }}>
          Misure, vibrazioni e storico. Nella dashboard locale.
        </Copy>
      </div>
      <div
        style={{
          position: "absolute",
          left: 112,
          top: 460,
          width: 1696,
          height: 467,
          borderRadius: 18,
          overflow: "hidden",
          background: "#f2f7f5",
          fontFamily: "SolarText",
          boxShadow: "0px 30px 70px #00000070",
          opacity: interpolate(f, [0.6 * fps, 1.3 * fps], [0, 1], clamp),
          translate: `0px ${interpolate(f, [0.6 * fps, 1.8 * fps], [120, 0], { ...clamp, easing: ease })}px`,
          scale: interpolate(f, [0.6 * fps, 2 * fps], [0.96, 1], {
            ...clamp,
            easing: ease,
          }),
        }}
      >
        <div
          style={{
            height: 68,
            background: "#142e36",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 30px",
            fontSize: 27,
            color: "#eff8f5",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 15 }}>
            <EchoMark size={40} />
            SolarEcho <strong style={{ color: C.mint }}>AI</strong>
          </div>
          <span style={{ fontSize: 22, color: "#c4d8d4" }}>
            Monitoraggio del pannello &nbsp; / &nbsp; AI non attiva
          </span>
        </div>
        <div style={{ padding: "22px 30px" }}>
          <div style={{ display: "flex", gap: 20 }}>
            <Metric label="TENSIONE" unit="V" />
            <Metric label="CORRENTE" unit="mA" />
            <Metric label="POTENZA" unit="mW" highlight />
            <div
              style={{
                flex: 1,
                borderRadius: 12,
                background: "#e3eeeb",
                padding: "22px 28px",
              }}
            >
              <div
                style={{ color: "#637b80", fontSize: 22, letterSpacing: 1.5 }}
              >
                ACQUISIZIONE REALE
              </div>
              <div
                style={{
                  fontSize: 55,
                  color: "#17303a",
                  fontFamily: "SolarDisplay",
                  marginTop: 10,
                }}
              >
                230 <span style={{ fontSize: 26 }}>campioni</span>
              </div>
            </div>
          </div>
          <div
            style={{
              background: "white",
              border: "1px solid #dbe7e5",
              borderRadius: 12,
              marginTop: 17,
              padding: "16px 23px",
              display: "flex",
              gap: 25,
              alignItems: "center",
            }}
          >
            <div style={{ width: 390, color: "#17303a" }}>
              <div style={{ fontSize: 30, fontWeight: 700 }}>
                Risposta all’impatto
              </div>
              <div style={{ fontSize: 22, color: "#71878a", marginTop: 9 }}>
                Accelerazione X / Y / Z
              </div>
              <div style={{ fontSize: 24, color: "#087e79", marginTop: 25 }}>
                Archivio CSV + JSON ↗
              </div>
            </div>
            <Waveform
              width={1162}
              height={158}
              progress={interpolate(f, [1.3 * fps, 4.5 * fps], [0, 1], clamp)}
              light
            />
          </div>
        </div>
      </div>
      <Copy
        delay={3}
        style={{ position: "absolute", left: 120, bottom: 97, fontSize: 25 }}
      >
        Dati sul dispositivo. Storico consultabile ed esportabile.
      </Copy>
    </AbsoluteFill>
  );
};
