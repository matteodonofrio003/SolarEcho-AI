import { Video } from "@remotion/media";
import { CanvasImage, Sequence, staticFile, useVideoConfig } from "remotion";
import { Evidence, FilmFrame, Note, palette, Title } from "./visual";

export const Action = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="07 / DAL SEGNALE ALL’AZIONE">
      <Sequence
        name="Indicatore rosso del prototipo"
        durationInFrames={Math.round(5.5 * fps)}
        premountFor={fps}
      >
        <Video
          name="LED reale - replay 0,5x"
          src={staticFile("footage/demo.mp4")}
          trimBefore={Math.round(19.1 * fps)}
          playbackRate={0.5}
          premountFor={fps}
          muted
          objectFit="cover"
          style={{
            position: "absolute",
            left: 1120,
            top: 145,
            width: 690,
            height: 780,
          }}
        />
        <div style={{ position: "absolute", left: 112, top: 260, width: 940 }}>
          <Title>
            Una luce.
            <br />
            <span style={{ color: palette.amber }}>Un controllo.</span>
          </Title>
          <Note style={{ marginTop: 42 }}>
            Il LED segnala
            <br />
            la richiesta di ispezione.
          </Note>
          <Evidence amber style={{ marginTop: 48 }}>
            LED REALE · REPLAY 0,5×
          </Evidence>
        </div>
      </Sequence>
      <Sequence
        name="Segnalazione inviata manualmente a Telegram"
        from={Math.round(5.5 * fps)}
        premountFor={fps}
      >
        <Sequence
          name="Ripresa originale del telefono"
          durationInFrames={Math.round(3.5 * fps)}
          premountFor={fps}
        >
          <Video
            name="Messaggio sul telefono"
            src={staticFile("social-v2/telegram.mp4")}
            trimBefore={2 * fps}
            premountFor={fps}
            muted
            objectFit="contain"
            style={{
              position: "absolute",
              left: 1080,
              top: 120,
              width: 740,
              height: 820,
            }}
          />
        </Sequence>
        <Sequence
          name="Ingrandimento autentico del messaggio"
          from={Math.round(3.5 * fps)}
          premountFor={fps}
        >
          <CanvasImage
            src={staticFile("social-v2/phone-detail.png")}
            premountFor={fps}
            style={{
              position: "absolute",
              left: 1180,
              top: 130,
              width: 610,
              height: 800,
              objectFit: "contain",
            }}
          />
          <Evidence
            style={{
              position: "absolute",
              left: 1180,
              bottom: 100,
              fontSize: 24,
            }}
          >
            DETTAGLIO REALE · FERMOIMMAGINE
          </Evidence>
        </Sequence>
        <div style={{ position: "absolute", left: 112, top: 255, width: 940 }}>
          <Title>
            I dati.
            <br />
            <span style={{ color: palette.mint }}>Al tecnico.</span>
          </Title>
          <Note style={{ marginTop: 44 }}>
            Una segnalazione
            <br />
            con i dati del pannello.
          </Note>
          <Evidence style={{ marginTop: 48 }}>
            INVIO MANUALE DALLA DASHBOARD
          </Evidence>
        </div>
      </Sequence>
    </FilmFrame>
  );
};
