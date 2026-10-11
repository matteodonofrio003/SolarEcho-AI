import { Sequence } from "remotion";
import {
  Stage,
  Kicker,
  Head,
  Text,
  Shot,
  Screen,
  Tag,
  Flow,
  P,
} from "./visual";
export const Demo = () => (
  <Stage>
    <Sequence name="01 / lancio autentico" durationInFrames={105}>
      <Shot
        file="demo"
        start={6.3}
        style={{ left: 1130, top: 50, width: 500, height: 835 }}
        fit="contain"
        sound
      />
      <div style={{ position: "absolute", left: 112, top: 215, width: 940 }}>
        <Kicker>01 / IMPATTO</Kicker>
        <Head>
          La prova.
          <br />
          <span style={{ color: P.cyan }}>È reale.</span>
        </Head>
        <Text>Una pallina. Il pannello. Il sistema in ascolto.</Text>
        <div style={{ marginTop: 38 }}>
          <Tag>RIPRESA DEL PROTOTIPO</Tag>
        </div>
      </div>
    </Sequence>
    <Sequence name="01 / contatto rallentato" from={105} durationInFrames={165}>
      <Shot
        file="demo"
        start={7.15}
        rate={0.5}
        style={{ left: 1130, top: 50, width: 500, height: 835 }}
        fit="contain"
      />
      <div style={{ position: "absolute", left: 112, top: 200, width: 950 }}>
        <Kicker>01 / IL CONTATTO</Kicker>
        <Head>
          Urto rilevato.
          <br />
          <span style={{ color: P.amber }}>Danno da verificare.</span>
        </Head>
        <Text>Un impatto non è una diagnosi.</Text>
        <div style={{ marginTop: 38 }}>
          <Tag color={P.amber}>REPLAY 0,5× · RIPRESA ORIGINALE</Tag>
        </div>
      </div>
    </Sequence>
    <Sequence name="02 / acquisizione XYZ" from={270} durationInFrames={300}>
      <div style={{ position: "absolute", left: 112, top: 60 }}>
        <Kicker>02 / ACQUISIZIONE</Kicker>
        <Head size={73}>
          La vibrazione diventa <span style={{ color: P.cyan }}>dato.</span>
        </Head>
      </div>
      <Screen
        start={19.3}
        snapshot="dash-acquisition"
        holdAfter={2.6}
        x={159}
        y={276}
        w={1515}
        h={580}
        style={{ left: 112, top: 256, width: 1696, height: 650 }}
      />
      <div style={{ position: "absolute", top: 215, left: 112 }}>
        <Tag>DASHBOARD REALE · POI FERMOIMMAGINE</Tag>
      </div>
    </Sequence>
    <Sequence name="03 / score reale" from={570} durationInFrames={105}>
      <div style={{ position: "absolute", left: 112, top: 80 }}>
        <Kicker>03 / ANALISI AI LOCALE</Kicker>
        <Head size={76}>
          Confrontare la <span style={{ color: P.cyan }}>firma.</span>
        </Head>
      </div>
      <Screen
        start={24}
        snapshot="dash-ai"
        x={188}
        y={790}
        w={349}
        h={120}
        style={{ left: 112, top: 435, width: 825, height: 284 }}
      />
      <div style={{ position: "absolute", left: 112, top: 325 }}>
        <Tag>FERMOIMMAGINE · SCORE REALE DELLA DEMO</Tag>
      </div>
      <div style={{ position: "absolute", left: 1050, top: 315, width: 720 }}>
        <Head size={95}>0,6035</Head>
        <Text size={32}>
          Soglia impostata: 0,3000.
          <br />
          Scostamento dal riferimento.
        </Text>
        <Text size={33}>Non è una probabilità di danno.</Text>
      </div>
    </Sequence>
    <Sequence
      name="03 / architettura del modello"
      from={675}
      durationInFrames={255}
    >
      <Shot
        file="demo"
        start={24.2}
        style={{ left: 1210, top: 65, width: 480, height: 710 }}
        fit="contain"
      />
      <div style={{ position: "absolute", left: 112, top: 165, width: 980 }}>
        <Kicker>03 / EDGE AI</Kicker>
        <Head size={94}>
          Dal segnale
          <br />
          al <span style={{ color: P.cyan }}>confronto.</span>
        </Head>
        <Text>
          Vibrazioni registrate → modello locale
          <br />→ score rispetto alla baseline.
        </Text>
        <div style={{ marginTop: 32 }}>
          <Tag>SCHEMA DEL FLUSSO</Tag>
        </div>
      </div>
      <Flow active={2} top={752} />
    </Sequence>
    <Sequence
      name="04 / segnalazione effettiva"
      from={930}
      durationInFrames={150}
    >
      <div style={{ position: "absolute", left: 112, top: 70 }}>
        <Kicker>04 / SEGNALAZIONE</Kicker>
        <Head size={75}>
          Ispezione <span style={{ color: P.amber }}>consigliata.</span>
        </Head>
      </div>
      <Screen
        start={44}
        snapshot="dash-alert"
        x={158}
        y={389}
        w={1516}
        h={354}
        style={{ left: 112, top: 325, width: 1150, height: 270 }}
      />
      <Shot
        file="demo"
        start={19.1}
        rate={0.2}
        style={{ left: 1285, top: 235, width: 525, height: 660 }}
        fit="cover"
      />
      <div style={{ position: "absolute", left: 112, top: 650, width: 1150 }}>
        <Tag color={P.amber}>ANOMALIA SPERIMENTALE · NESSUN DANNO CERTO</Tag>
        <Text size={31}>
          Dashboard: fermoimmagine autentico.
          <br />
          LED acceso: dettaglio reale, rallentato 0,2×.
        </Text>
      </div>
    </Sequence>
    <Sequence
      name="04 / test sintetico dichiarato"
      from={1080}
      durationInFrames={195}
    >
      <div style={{ position: "absolute", left: 112, top: 60 }}>
        <Kicker>VERIFICA SOFTWARE · TEST SEPARATO</Kicker>
        <Head size={76}>
          Firma alterata{" "}
          <span style={{ color: P.amber }}>artificialmente.</span>
        </Head>
      </div>
      <Screen
        start={29}
        snapshot="dash-synthetic"
        holdAfter={1}
        x={159}
        y={276}
        w={1515}
        h={550}
        style={{ left: 112, top: 280, width: 1696, height: 616 }}
      />
      <div style={{ position: "absolute", left: 112, top: 219 }}>
        <Tag color={P.amber}>
          TEST SINTETICO · FERMOIMMAGINE · NON DIMOSTRA DANNI FISICI
        </Tag>
      </div>
    </Sequence>
  </Stage>
);
