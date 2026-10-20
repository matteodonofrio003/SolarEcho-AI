import { CanvasImage, staticFile, useVideoConfig } from "remotion";
import { Evidence, FilmFrame, Note, palette, Title } from "./visual";

export const Synthetic = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="06 / TEST SOFTWARE SEPARATO">
      <Title
        style={{ position: "absolute", left: 112, top: 145, fontSize: 128 }}
      >
        E se la firma <span style={{ color: palette.amber }}>cambia?</span>
      </Title>
      <Evidence amber style={{ position: "absolute", left: 112, top: 305 }}>
        TEST SINTETICO · FIRMA ALTERATA ARTIFICIALMENTE
      </Evidence>
      <CanvasImage
        src={staticFile("social-v2/crop-synthetic-plot.png")}
        premountFor={fps}
        style={{
          position: "absolute",
          left: 200,
          top: 390,
          width: 1520,
          height: 513,
          borderRadius: 8,
        }}
      />
      <Note
        style={{ position: "absolute", left: 112, bottom: 100, fontSize: 36 }}
      >
        Score originale 0,6035 → sintetico 82,1386.{" "}
        <span style={{ color: palette.amber }}>Non dimostra danni fisici.</span>
      </Note>
    </FilmFrame>
  );
};
