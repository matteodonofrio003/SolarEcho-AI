import { Video } from "@remotion/media";
import { staticFile, useVideoConfig } from "remotion";
import { Evidence, FilmFrame, Note, palette, Title } from "./visual";

export const Hook = () => {
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="01 / UN IMPATTO, UN SEGNALE">
      <Video
        name="Lancio reale della pallina"
        src={staticFile("footage/demo.mp4")}
        trimBefore={Math.round(6.3 * fps)}
        premountFor={fps}
        muted
        objectFit="contain"
        style={{
          position: "absolute",
          left: 1050,
          top: 0,
          width: 780,
          height: 1080,
        }}
      />
      <div style={{ position: "absolute", left: 112, top: 255, width: 900 }}>
        <Title>
          Un impatto.
          <br />
          <span style={{ color: palette.mint }}>Un segnale.</span>
        </Title>
        <Note style={{ marginTop: 44 }}>
          Il pannello ha qualcosa
          <br />
          da raccontare.
        </Note>
        <Evidence style={{ marginTop: 64 }}>
          PROVA FISICA SUL PROTOTIPO
        </Evidence>
      </div>
    </FilmFrame>
  );
};
