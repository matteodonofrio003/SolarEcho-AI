import {
  CanvasImage,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  clamp,
  Evidence,
  FilmFrame,
  Note,
  palette,
  StillPhoto,
  Title,
} from "./visual";

export const ExplodedHardware = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <FilmFrame chapter="03 / DENTRO IL PROTOTIPO">
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: interpolate(frame, [1.3 * fps, 2 * fps], [1, 0], clamp),
        }}
      >
        <StillPhoto
          file="electronics"
          style={{
            left: 112,
            top: 165,
            width: 800,
            height: 750,
            borderRadius: 8,
          }}
        />
        <div style={{ position: "absolute", left: 1020, top: 280, width: 780 }}>
          <Title style={{ fontSize: 128 }}>
            Il nostro
            <br />
            <span style={{ color: palette.mint }}>prototipo.</span>
          </Title>
          <Note style={{ marginTop: 40, fontSize: 48 }}>Hardware reale.</Note>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: interpolate(frame, [1.3 * fps, 2 * fps], [0, 1], clamp),
        }}
      >
        <CanvasImage
          src={staticFile("exploded/solarecho-illustrative-v1.png")}
          premountFor={fps}
          style={{
            position: "absolute",
            left: 210,
            top: 165,
            width: 1460,
            height: 821,
            objectFit: "contain",
            translate: `${interpolate(frame, [1.3 * fps, 2.4 * fps], [32, 0], { ...clamp, easing: Easing.out(Easing.cubic) })}px 0`,
            maskImage:
              "linear-gradient(to bottom, transparent, black 6%, black 91%, transparent), linear-gradient(to right, transparent, black 6%, black 94%, transparent)",
            maskComposite: "intersect",
          }}
        />
        <Title
          style={{ position: "absolute", left: 112, top: 130, fontSize: 104 }}
        >
          Dentro <span style={{ color: palette.mint }}>SolarEcho.</span>
        </Title>

        <svg
          width="1920"
          height="1080"
          style={{ position: "absolute", inset: 0 }}
        >
          <path
            d="M 250 390 L 320 390 L 470 490"
            fill="none"
            stroke={palette.mint}
            strokeWidth="2"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={interpolate(
              frame,
              [2.2 * fps, 3 * fps],
              [1, 0],
              clamp,
            )}
            opacity={interpolate(
              frame,
              [2.2 * fps, 2.4 * fps],
              [0, 0.85],
              clamp,
            )}
          />
          <circle
            cx="470"
            cy="490"
            r="5"
            fill={palette.mint}
            opacity={interpolate(frame, [2.8 * fps, 3 * fps], [0, 1], clamp)}
          />
          <path
            d="M 1110 245 L 1110 280 L 1030 350"
            fill="none"
            stroke={palette.mint}
            strokeWidth="2"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={interpolate(
              frame,
              [3.3 * fps, 4.1 * fps],
              [1, 0],
              clamp,
            )}
            opacity={interpolate(
              frame,
              [3.3 * fps, 3.5 * fps],
              [0, 0.85],
              clamp,
            )}
          />
          <circle
            cx="1030"
            cy="350"
            r="5"
            fill={palette.mint}
            opacity={interpolate(frame, [3.9 * fps, 4.1 * fps], [0, 1], clamp)}
          />
          <path
            d="M 1410 610 L 1580 650 L 1580 682"
            fill="none"
            stroke={palette.mint}
            strokeWidth="2"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={interpolate(
              frame,
              [4.4 * fps, 5.2 * fps],
              [1, 0],
              clamp,
            )}
            opacity={interpolate(
              frame,
              [4.4 * fps, 4.6 * fps],
              [0, 0.85],
              clamp,
            )}
          />
          <circle
            cx="1410"
            cy="610"
            r="5"
            fill={palette.mint}
            opacity={interpolate(frame, [4.4 * fps, 4.6 * fps], [0, 1], clamp)}
          />
        </svg>

        <div
          style={{
            position: "absolute",
            left: 112,
            top: 285,
            opacity: interpolate(frame, [2.2 * fps, 2.7 * fps], [0, 1], clamp),
          }}
        >
          <Evidence style={{ fontSize: 24 }}>01 / PANNELLO</Evidence>
          <Note style={{ fontSize: 42, color: palette.ink, marginTop: 12 }}>
            Energia solare.
          </Note>
        </div>
        <div
          style={{
            position: "absolute",
            left: 970,
            top: 145,
            opacity: interpolate(frame, [3.3 * fps, 3.8 * fps], [0, 1], clamp),
          }}
        >
          <Evidence style={{ fontSize: 24 }}>02 / SUPPORTO</Evidence>
          <Note style={{ fontSize: 42, color: palette.ink, marginTop: 12 }}>
            Struttura stampata.
          </Note>
        </div>
        <div
          style={{
            position: "absolute",
            left: 1500,
            top: 700,
            width: 325,
            opacity: interpolate(frame, [4.4 * fps, 4.9 * fps], [0, 1], clamp),
          }}
        >
          <Evidence style={{ fontSize: 24 }}>03 / UNO Q</Evidence>
          <Note style={{ fontSize: 42, color: palette.ink, marginTop: 12 }}>
            Acquisizione
            <br />e AI locale.
          </Note>
        </div>

        <div
          style={{
            position: "absolute",
            left: 112,
            right: 112,
            bottom: 150,
            display: "flex",
            justifyContent: "space-between",
            gap: 20,
            paddingTop: 18,
            borderTop: "1px solid #79f2cd45",
            fontFamily: "ShowcaseDisplay",
            fontSize: 32,
            opacity: interpolate(frame, [6.5 * fps, 7 * fps], [0, 1], clamp),
          }}
        >
          <span>
            <span style={{ color: palette.mint }}>Piezo</span> / impatto
          </span>
          <span>
            <span style={{ color: palette.mint }}>Modulino</span> / vibrazioni
            XYZ
          </span>
          <span>
            <span style={{ color: palette.mint }}>INA219</span> / potenza
          </span>
          <span>
            <span style={{ color: palette.mint }}>LED</span> / ispezione
          </span>
        </div>
        <Evidence
          amber
          style={{ position: "absolute", left: 112, bottom: 90, fontSize: 24 }}
        >
          ESPLOSO ILLUSTRATIVO DA FOTO · GEOMETRIE SEMPLIFICATE
        </Evidence>
      </div>
    </FilmFrame>
  );
};
