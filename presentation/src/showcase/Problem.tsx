import {
  Evidence,
  FilmFrame,
  Note,
  palette,
  StillPhoto,
  Title,
} from "./visual";

export const Problem = () => (
  <FilmFrame chapter="02 / MONITORARE PER INTERVENIRE">
    <StillPhoto
      file="sunlight"
      style={{ left: 1080, top: 150, width: 740, height: 760, borderRadius: 8 }}
    />
    <div style={{ position: "absolute", left: 112, top: 225, width: 940 }}>
      <Title>
        Quando serve
        <br />
        <span style={{ color: palette.mint }}>controllare?</span>
      </Title>
      <Note style={{ marginTop: 42 }}>
        Impatti e vibrazioni.
        <br />
        Segnali per la manutenzione.
      </Note>
      <Evidence style={{ marginTop: 50 }}>
        PER GESTORI E TECNICI DI IMPIANTI
      </Evidence>
    </div>
    <Note
      style={{ position: "absolute", left: 112, bottom: 100, fontSize: 34 }}
    >
      Un impatto rilevato non dimostra un danno.
    </Note>
  </FilmFrame>
);
