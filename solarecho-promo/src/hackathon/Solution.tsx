import { Sequence } from "remotion";
import { Stage, Kicker, Head, Text, Photo, Shot, Tag, P, Flow } from "./visual";
export const Solution = () => (
  <Stage>
    <Sequence name="SolarEcho / reveal" durationInFrames={150}>
      <Photo
        file="panel"
        style={{ left: 930, top: 95, width: 800, height: 800 }}
      />
      <div style={{ position: "absolute", left: 112, top: 210, width: 850 }}>
        <Kicker>IL PANNELLO DIVENTA UN SENSORE</Kicker>
        <Head size={122}>
          SolarEcho
          <br />
          <span style={{ color: P.cyan }}>AI.</span>
        </Head>
        <Text>Ascoltiamo la sua firma vibrazionale.</Text>
      </div>
    </Sequence>
    <Sequence
      name="Sensori / prototipo reale"
      from={150}
      durationInFrames={180}
    >
      <Shot
        file="orbit"
        start={0.3}
        style={{ left: 1030, top: 80, width: 640, height: 820 }}
        rate={1}
      />
      <div style={{ position: "absolute", left: 112, top: 190, width: 875 }}>
        <Kicker>DALLA FISICA AL DATO</Kicker>
        <Head size={86}>
          Due funzioni.
          <br />
          <span style={{ color: P.cyan }}>Un sistema.</span>
        </Head>
        <Text size={37}>
          <span style={{ color: P.amber }}>PIEZO</span> — rileva l’impatto
          <br />
          <span style={{ color: P.cyan }}>IMU</span> — misura vibrazioni X · Y ·
          Z
        </Text>
        <div style={{ marginTop: 35 }}>
          <Tag>HARDWARE REALE · PROTOTIPO</Tag>
        </div>
      </div>
    </Sequence>
    <Sequence
      name="UNO Q / dettaglio hardware"
      from={330}
      durationInFrames={285}
    >
      <Photo
        file="electronics"
        style={{ left: 1050, top: 60, width: 700, height: 825 }}
        zoom={1.09}
      />
      <div style={{ position: "absolute", left: 112, top: 155, width: 850 }}>
        <Kicker>ARDUINO UNO Q</Kicker>
        <Head size={94}>
          L’intelligenza.
          <br />
          <span style={{ color: P.cyan }}>Sul dispositivo.</span>
        </Head>
        <Text>
          Edge AI: analisi locale dei segnali.
          <br />
          Dal sensore alla segnalazione.
        </Text>
        <div style={{ marginTop: 38, display: "flex", gap: 16 }}>
          <Tag>ACQUISIZIONE</Tag>
          <Tag color={P.amber}>ANALISI LOCALE</Tag>
        </div>
      </div>
      <svg
        width="1920"
        height="1080"
        style={{ position: "absolute", inset: 0 }}
      >
        <path
          d="M 992 598 L 1080 598 L 1355 512"
          stroke={P.cyan}
          strokeWidth="2"
          fill="none"
        />
        <circle cx="1355" cy="512" r="8" fill={P.cyan} />
      </svg>
      <Flow active={2} top={740} />
    </Sequence>
  </Stage>
);
