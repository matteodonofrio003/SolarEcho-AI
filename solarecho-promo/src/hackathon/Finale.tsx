import { AbsoluteFill } from "remotion";
import { Stage, Kicker, Head, Photo, P, Tag } from "./visual";
export const Finale = () => (
  <Stage>
    <Photo
      file="panel"
      style={{ left: 1030, top: -20, width: 1080, height: 1080 }}
      zoom={1.09}
    />
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(90deg,#040b19 30%,#040b19b0 60%,transparent)",
      }}
    />
    <div style={{ position: "absolute", left: 112, top: 235, width: 1200 }}>
      <Kicker>ASCOLTARE IL PANNELLO. GUIDARE LA MANUTENZIONE.</Kicker>
      <Head size={145}>
        SolarEcho <span style={{ color: P.cyan }}>AI</span>
      </Head>
      <div
        style={{
          fontFamily: "SolarDisplay",
          fontSize: 46,
          lineHeight: 1.2,
          marginTop: 32,
        }}
      >
        Il pannello che riconosce
        <br />i propri danni.
      </div>
      <div style={{ marginTop: 62 }}>
        <Tag color={P.amber}>PROTOTIPO SPERIMENTALE</Tag>
      </div>
    </div>
  </Stage>
);
