import { CanvasImage, staticFile, useVideoConfig } from "remotion";
import { Evidence, FilmFrame, Note, palette, Title } from "./visual";

export const Analysis = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="05 / EDGE AI SPERIMENTALE">
      <Title
        style={{ position: "absolute", left: 112, top: 155, fontSize: 124 }}
      >
        Confronto con la <span style={{ color: palette.mint }}>baseline.</span>
      </Title>
      <CanvasImage
        src={staticFile("social-v2/crop-real-score.png")}
        premountFor={fps}
        style={{
          position: "absolute",
          left: 112,
          top: 410,
          width: 790,
          height: 272,
          borderRadius: 8,
        }}
      />
      <div style={{ position: "absolute", left: 1020, top: 360, width: 790 }}>
        <Title style={{ fontSize: 98 }}>
          Soglia <span style={{ color: palette.amber }}>0,3000</span>
        </Title>
        <Note style={{ marginTop: 40 }}>Superata in questa prova.</Note>
        <Note style={{ marginTop: 32, fontSize: 44 }}>
          Lo score non è una probabilità
          <br />o una percentuale di danno.
        </Note>
      </div>
      <Evidence style={{ position: "absolute", left: 112, top: 740 }}>
        SCORE REALE REGISTRATO · FERMOIMMAGINE AUTENTICO
      </Evidence>
      <Note
        style={{ position: "absolute", left: 112, bottom: 100, fontSize: 38 }}
      >
        Esempio del percorso di allerta. Validazione fisica ancora da
        completare.
      </Note>
    </FilmFrame>
  );
};
