import { Sequence, useVideoConfig } from "remotion";
import {
  Evidence,
  FilmFrame,
  Note,
  palette,
  StillPhoto,
  Title,
} from "./visual";

export const Closing = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="08 / SOLARECHO AI">
      <StillPhoto
        file="panel"
        style={{
          left: 1050,
          top: 150,
          width: 770,
          height: 770,
          borderRadius: 8,
        }}
      />
      <Sequence
        name="Utilita per la manutenzione"
        durationInFrames={6 * fps}
        premountFor={fps}
      >
        <div style={{ position: "absolute", left: 112, top: 245, width: 930 }}>
          <Title style={{ fontSize: 134 }}>
            Ascoltare
            <br />
            <span style={{ color: palette.mint }}>il pannello.</span>
          </Title>
          <Note style={{ marginTop: 44, fontSize: 62 }}>
            Guidare la manutenzione.
          </Note>
          <Evidence style={{ marginTop: 48 }}>
            PROTOTIPO SPERIMENTALE · ARDUINO UNO Q
          </Evidence>
        </div>
      </Sequence>
      <Sequence
        name="Progetto e prossimo passo"
        from={6 * fps}
        premountFor={fps}
      >
        <div style={{ position: "absolute", left: 112, top: 240, width: 940 }}>
          <Title style={{ fontSize: 148 }}>
            SolarEcho
            <br />
            <span style={{ color: palette.mint }}>AI.</span>
          </Title>
          <Note style={{ marginTop: 36, fontSize: 52 }}>
            Prossimo passo:
            <br />
            validazione su modifiche
            <br />
            meccaniche reali.
          </Note>
        </div>
      </Sequence>
      <Evidence style={{ position: "absolute", left: 112, bottom: 100 }}>
        HACKTURIN 2026 · BEYOND SOLAR
      </Evidence>
    </FilmFrame>
  );
};
