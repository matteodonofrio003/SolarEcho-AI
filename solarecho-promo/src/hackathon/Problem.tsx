import { AbsoluteFill, Sequence, useCurrentFrame, interpolate } from "remotion";
import {
  Stage,
  Kicker,
  Head,
  Text,
  Photo,
  Shot,
  Tag,
  P,
  Ripple,
} from "./visual";
export const Problem = () => {
  const f = useCurrentFrame();
  return (
    <Stage>
      <Sequence name="Apertura / pannello in luce" durationInFrames={135}>
        <Photo
          file="sunlight"
          style={{ left: 620, top: -80, width: 1320, height: 1320 }}
          zoom={1.1}
        />
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(90deg,#040b19 20%,#040b19bb 45%,transparent 80%)",
          }}
        />
        <div style={{ position: "absolute", left: 112, top: 210, width: 860 }}>
          <Kicker>OGNI PANNELLO HA UNA STORIA</Kicker>
          <Head size={112}>
            Un impatto.
            <br />
            <span style={{ color: P.cyan }}>Un istante.</span>
          </Head>
          <Text>Le conseguenze possono durare anni.</Text>
        </div>
      </Sequence>
      <Sequence
        name="Prova fisica / apertura"
        from={135}
        durationInFrames={135}
      >
        <Shot
          file="impact-outdoor"
          start={1.45}
          rate={0.5}
          style={{ left: 1120, top: 70, width: 510, height: 820 }}
          fit="contain"
        />
        <Ripple at={30} />
        <div style={{ position: "absolute", left: 112, top: 240, width: 930 }}>
          <Kicker>GRANDINE · VENTO · URTI</Kicker>
          <Head>
            La sollecitazione
            <br />
            lascia una <span style={{ color: P.amber }}>traccia.</span>
          </Head>
          <Text>Alcune alterazioni sono difficili da vedere.</Text>
          <div style={{ marginTop: 45 }}>
            <Tag color={P.amber}>PROVA CONTROLLATA · REPLAY 0,5×</Tag>
          </div>
        </div>
      </Sequence>
      <Sequence name="Integrità e produzione" from={270} durationInFrames={285}>
        <Shot
          file="beauty"
          style={{ left: 910, top: 65, width: 810, height: 820 }}
          rate={0.57}
        />
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(90deg,#040b19 25%,#040b19aa 50%,transparent 75%)",
          }}
        />
        <div style={{ position: "absolute", left: 112, top: 225, width: 970 }}>
          <Kicker>VEDERE NON BASTA SEMPRE</Kicker>
          <Head>
            Quando serve
            <br />
            <span style={{ color: P.cyan }}>controllare?</span>
          </Head>
          <Text>
            Produzione. Tempo. Risorse.
            <br />
            La manutenzione parte da un segnale.
          </Text>
        </div>
      </Sequence>
      <div
        style={{
          position: "absolute",
          bottom: 220,
          left: 112,
          right: 112,
          height: 1,
          background: `linear-gradient(90deg,${P.cyan},transparent)`,
          opacity: interpolate(f, [20, 60], [0, 0.5], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
    </Stage>
  );
};
