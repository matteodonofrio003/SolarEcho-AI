import { Sequence } from "remotion";
import { Stage, Kicker, Head, Text, Photo, Shot, Tag, P } from "./visual";
export const Innovation = () => (
  <Stage>
    <Sequence name="Innovazione / sensori" durationInFrames={105}>
      <Photo
        file="sensor"
        style={{ left: 1000, top: 70, width: 810, height: 810 }}
      />
      <div style={{ position: "absolute", left: 112, top: 190, width: 875 }}>
        <Kicker>INNOVAZIONE CONCRETA</Kicker>
        <Head>
          Sensori
          <br />
          <span style={{ color: P.cyan }}>accessibili.</span>
        </Head>
        <Text>La fisica del pannello incontra l’AI.</Text>
      </div>
    </Sequence>
    <Sequence name="Innovazione / hardware" from={105} durationInFrames={105}>
      <Photo
        file="electronics"
        style={{ left: 1000, top: 70, width: 810, height: 810 }}
      />
      <div style={{ position: "absolute", left: 112, top: 190, width: 875 }}>
        <Kicker>FIRMA VIBRAZIONALE + EDGE AI</Kicker>
        <Head>
          Analisi locale.
          <br />
          <span style={{ color: P.cyan }}>Utilità reale.</span>
        </Head>
        <Text>Supporto alla manutenzione predittiva.</Text>
      </div>
    </Sequence>
    <Sequence name="Ricerca / prossimo passo" from={210} durationInFrames={105}>
      <Shot
        file="outdoor"
        start={5.5}
        style={{ left: 1100, top: 60, width: 560, height: 820 }}
        fit="contain"
      />
      <div style={{ position: "absolute", left: 112, top: 190, width: 950 }}>
        <Kicker>IL PROSSIMO PASSO</Kicker>
        <Head size={89}>
          Validare.
          <br />
          <span style={{ color: P.amber }}>Sul campo.</span>
        </Head>
        <Text>Verificare il modello su alterazioni fisiche.</Text>
        <div style={{ marginTop: 38 }}>
          <Tag>PROTOTIPO SPERIMENTALE</Tag>
        </div>
      </div>
    </Sequence>
  </Stage>
);
