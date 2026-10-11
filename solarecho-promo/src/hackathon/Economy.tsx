import { Sequence, useCurrentFrame } from "remotion";
import { Stage, Kicker, Head, Text, Photo, Tag, P, enter } from "./visual";
const Calendar = () => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(7,1fr)",
        gap: 9,
        width: 370,
        marginTop: 25,
      }}
    >
      {Array.from({ length: 28 }, (_, i) => (
        <div
          key={i}
          style={{
            height: 31,
            border: "1px solid #60758c50",
            background: i % 7 === 4 ? "#73839a45" : "#122035",
            opacity: enter(f, 20 + i * 2),
          }}
        />
      ))}
    </div>
  );
};
const Priority = () => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(7,1fr)",
        gap: 9,
        width: 370,
        marginTop: 25,
      }}
    >
      {Array.from({ length: 28 }, (_, i) => (
        <div
          key={i}
          style={{
            height: 31,
            border: `1px solid ${[6, 14, 23].includes(i) ? P.amber : "#50e4ee40"}`,
            background: [6, 14, 23].includes(i) ? "#ffbf583f" : "#0a292f",
            opacity: enter(f, 20 + i * 2),
          }}
        />
      ))}
    </div>
  );
};
export const Economy = () => (
  <Stage>
    <Photo
      file="sunlight"
      style={{ left: 1150, top: -40, width: 800, height: 800, opacity: 0.12 }}
    />
    <div style={{ position: "absolute", left: 112, top: 95 }}>
      <Kicker>VALORE PER CHI GESTISCE UN IMPIANTO</Kicker>
      <Head size={83}>
        Dove intervenire <span style={{ color: P.cyan }}>prima?</span>
      </Head>
    </div>
    <div
      style={{
        position: "absolute",
        left: 112,
        top: 270,
        fontFamily: "SolarDisplay",
        fontSize: 21,
        letterSpacing: 1.5,
        color: P.muted,
      }}
    >
      SCHEMA ILLUSTRATIVO · BENEFICI POTENZIALI
    </div>
    <Sequence name="Confronto / manutenzione" durationInFrames={420}>
      <div
        style={{
          position: "absolute",
          left: 112,
          top: 340,
          width: 810,
          padding: "30px 35px",
          background: "#0b1729cc",
          borderTop: "2px solid #697b91",
          height: 460,
        }}
      >
        <Kicker>CONTROLLI PROGRAMMATI</Kicker>
        <Head size={50}>Seguire il calendario.</Head>
        <Calendar />
        <Text size={29}>
          Visite periodiche
          <br />
          Tempo e risorse per le ispezioni
          <br />
          Alcune anomalie emergono più tardi
        </Text>
      </div>
      <div
        style={{
          position: "absolute",
          left: 998,
          top: 340,
          width: 810,
          padding: "30px 35px",
          background: "#0c2632dd",
          borderTop: `2px solid ${P.cyan}`,
          height: 460,
        }}
      >
        <Kicker>CON SOLARECHO AI</Kicker>
        <Head size={50}>Dare una priorità.</Head>
        <Priority />
        <Text size={29}>
          Osservare eventi e variazioni
          <br />
          Approfondire le situazioni sospette
          <br />
          Organizzare interventi più mirati
        </Text>
      </div>
    </Sequence>
    <Sequence
      name="Beneficio economico / obiettivo"
      from={420}
      durationInFrames={255}
    >
      <div style={{ position: "absolute", left: 112, top: 335, width: 1696 }}>
        <Head size={87}>
          Meno controlli inutili.
          <br />
          Interventi <span style={{ color: P.cyan }}>più mirati.</span>
          <br />
          Costi <span style={{ color: P.amber }}>potenzialmente ridotti.</span>
        </Head>
        <div style={{ marginTop: 46 }}>
          <Tag color={P.amber}>
            BENEFICI PROSPETTICI · DA VALIDARE SUL CAMPO
          </Tag>
        </div>
        <Text size={27}>
          Confronto qualitativo: nessuna percentuale di risparmio misurata.
          <br />
          Il monitoraggio supporta le ispezioni e la loro pianificazione.
        </Text>
      </div>
    </Sequence>
  </Stage>
);
