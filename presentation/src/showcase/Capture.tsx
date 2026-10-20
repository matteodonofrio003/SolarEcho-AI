import { Video } from "@remotion/media";
import { CanvasImage, Sequence, staticFile, useVideoConfig } from "remotion";
import { Evidence, FilmFrame, palette, Title } from "./visual";

export const Capture = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="04 / ACQUISIZIONE REALE">
      <Title
        style={{ position: "absolute", left: 112, top: 155, fontSize: 126 }}
      >
        La risposta diventa <span style={{ color: palette.mint }}>dato.</span>
      </Title>
      <div
        style={{
          position: "absolute",
          left: 112,
          top: 345,
          width: 1696,
          height: 530,
          overflow: "hidden",
          borderRadius: 8,
          background: "#f5f9f8",
        }}
      >
        <Sequence
          name="Forma d'onda nella registrazione originale"
          durationInFrames={3 * fps}
          premountFor={fps}
        >
          <Video
            name="Dashboard registrata"
            src={staticFile("footage/dashboard.mp4")}
            trimBefore={Math.round(19.3 * fps)}
            premountFor={fps}
            muted
            style={{
              position: "absolute",
              width: 2039.663,
              height: 1030.99,
              left: -178.526,
              top: -379.368,
            }}
          />
        </Sequence>
        <Sequence
          name="Ferma il dettaglio per leggerlo"
          from={3 * fps}
          premountFor={fps}
        >
          <CanvasImage
            src={staticFile("social-v2/crop-waveform.png")}
            premountFor={fps}
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        </Sequence>
      </div>
      <Evidence style={{ position: "absolute", left: 112, bottom: 100 }}>
        XYZ IN g · DASHBOARD REGISTRATA, POI FERMOIMMAGINE
      </Evidence>
    </FilmFrame>
  );
};
