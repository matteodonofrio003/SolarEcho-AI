import {
  CanvasImage,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  Evidence,
  FilmFrame,
  palette,
  StillPhoto,
  Title,
  clamp,
} from "./visual";

// Native viewports keep the original atlas alpha; each component moves separately.
const parts = [
  {
    name: "Pannello FV",
    crop: [0.015, 0.04, 0.323, 0.296],
    grid: [270, 350, 235],
  },
  {
    name: "Supporto 3D",
    crop: [0.345, 0.04, 0.333, 0.305],
    grid: [650, 350, 235],
  },
  {
    name: "Arduino UNO Q",
    crop: [0.685, 0.07, 0.31, 0.265],
    grid: [1030, 350, 235],
  },
  {
    name: "Piezo analogico",
    crop: [0.035, 0.38, 0.29, 0.26],
    grid: [270, 590, 210],
  },
  {
    name: "Modulino Movement",
    crop: [0.37, 0.395, 0.29, 0.25],
    grid: [650, 590, 210],
  },
  {
    name: "INA219",
    crop: [0.705, 0.38, 0.28, 0.26],
    grid: [1030, 590, 210],
  },
  {
    name: "Solar charger",
    crop: [0.035, 0.68, 0.32, 0.255],
    grid: [270, 820, 210],
  },
  {
    name: "Batteria LiPo",
    crop: [0.36, 0.675, 0.348, 0.27],
    grid: [650, 820, 210],
  },
  {
    name: "LED + resistenza",
    crop: [0.73, 0.69, 0.25, 0.245],
    grid: [1030, 820, 210],
  },
] as const;

const chapters = [
  {
    start: 1.8,
    end: 5.5,
    tag: "01 / IL SISTEMA",
    title: "Ogni parte.\nUn compito.",
    body: "Nove elementi, un unico prototipo per osservare il pannello.",
    detail: "Esplorazione dei componenti",
  },
  {
    start: 5.5,
    end: 9.5,
    tag: "02 / STRUTTURA",
    title: "Il pannello.\nIl suo supporto.",
    body: "La struttura stampata sostiene il pannello e ospita l’elettronica.",
    detail: "Configurazione meccanica ripetibile",
  },
  {
    start: 9.5,
    end: 14.5,
    tag: "03 / ACQUISIZIONE",
    title: "Un impatto.\nLa sua firma.",
    body: "Il piezo attiva la cattura. Modulino Movement registra l’accelerazione XYZ.",
    detail: "Piezo → trigger  •  Modulino → XYZ",
  },
  {
    start: 14.5,
    end: 19.5,
    tag: "04 / ELABORAZIONE",
    title: "L’AI resta\nqui.",
    body: "Arduino UNO Q acquisisce sul microcontrollore e analizza localmente su Linux.",
    detail: "Inferenza senza cloud",
  },
  {
    start: 19.5,
    end: 25.5,
    tag: "05 / ENERGIA",
    title: "Misurare.\nAccumulare.",
    body: "INA219 misura corrente e potenza. Charger e LiPo compongono il sottosistema solare.",
    detail: "Nella demo la UNO Q usa USB-C",
  },
  {
    start: 25.5,
    end: 28.5,
    tag: "06 / SEGNALAZIONE",
    title: "Una luce.\nUn’ispezione.",
    body: "Il LED rosso segnala una richiesta di controllo del pannello.",
    detail: "Un’allerta non dimostra un danno",
  },
  {
    start: 28.5,
    end: 31,
    tag: "07 / INSIEME",
    title: "Dal pannello\nai dati.",
    body: "Sensori, analisi locale e segnalazione nello stesso prototipo.",
    detail: "SolarEcho AI  •  Arduino UNO Q",
  },
];

// Position, size, opacity; faded parts provide context during a detail shot.
const focus = (phase: number, index: number): number[] => {
  const g = parts[index].grid;
  if (phase === 0 || phase === 6) return [...g, 1];
  const faded = [g[0], g[1], g[2] * 0.65, 0.13];
  if (phase === 1)
    return index === 0
      ? [400, 540, 480, 1]
      : index === 1
        ? [950, 530, 460, 1]
        : faded;
  if (phase === 2)
    return index === 3
      ? [380, 505, 390, 1]
      : index === 4
        ? [950, 505, 470, 1]
        : faded;
  if (phase === 3) return index === 2 ? [650, 560, 690, 1] : faded;
  if (phase === 4) {
    if (index === 5) return [280, 510, 300, 1];
    if (index === 6) return [650, 510, 310, 1];
    if (index === 7) return [1030, 510, 320, 1];
    if (index === 0) return [280, 790, 210, 0.8];
    return faded;
  }
  return index === 8 ? [650, 525, 570, 1] : faded;
};

const Sprite = ({ crop }: { crop: readonly number[] }) => {
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: "50%",
        width: "100%",
        aspectRatio: `${crop[2]} / ${crop[3]}`,
        translate: "0 -50%",
        overflow: "hidden",
      }}
    >
      <CanvasImage
        src={staticFile("exploded/components-atlas-v4.png")}
        premountFor={fps}
        style={{
          position: "absolute",
          maxWidth: "none",
          width: `${100 / crop[2]}%`,
          height: `${100 / crop[3]}%`,
          left: `${(-100 * crop[0]) / crop[2]}%`,
          top: `${(-100 * crop[1]) / crop[3]}%`,
        }}
      />
    </div>
  );
};

export const DynamicHardware = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const seconds = frame / fps;
  const times = [
    0, 1.8, 3.4, 5.5, 6.3, 9.5, 10.3, 14.5, 15.3, 19.5, 20.3, 25.5, 26.3, 28.5,
    29.3, 31,
  ];
  const phases = [-1, -1, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6];
  return (
    <FilmFrame chapter="03 / DENTRO IL PROTOTIPO">
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: interpolate(frame, [1.5 * fps, 2.1 * fps], [1, 0], clamp),
        }}
      >
        <StillPhoto
          file="electronics"
          style={{
            left: 112,
            top: 150,
            width: 800,
            height: 780,
            borderRadius: 8,
          }}
        />
        <Title
          style={{ position: "absolute", left: 1030, top: 310, fontSize: 116 }}
        >
          Il nostro
          <br />
          <span style={{ color: palette.mint }}>prototipo.</span>
        </Title>
      </div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: interpolate(frame, [1.6 * fps, 2.2 * fps], [0, 1], clamp),
        }}
      >
        <Title
          style={{ position: "absolute", left: 112, top: 132, fontSize: 87 }}
        >
          Dentro <span style={{ color: palette.mint }}>SolarEcho.</span>
        </Title>
        <div
          style={{
            position: "absolute",
            left: 1280,
            top: 270,
            bottom: 150,
            width: 1,
            background: "linear-gradient(transparent, #79f2cd65, transparent)",
          }}
        />
        {parts.map((part, index) => {
          const keyframes = phases.map((phase) =>
            phase === -1
              ? [
                  650 + ((index % 3) - 1) * 22,
                  560 + Math.floor(index / 3) * 12,
                  190,
                  0,
                ]
              : focus(phase, index),
          );
          const values = (axis: number) => keyframes.map((p) => p[axis]);
          const currentPhase = Math.max(
            0,
            chapters.findIndex((c) => seconds >= c.start && seconds < c.end),
          );
          const selected = focus(currentPhase, index)[3] > 0.5;
          const angle = interpolate(
            seconds,
            [1.8, 3.4, 14.5, 19.5, 28.5, 30.3],
            [(index - 4) * 8, ((index % 3) - 1) * 3, -3, 3, -2, 0],
            clamp,
          );
          return (
            <div
              key={part.name}
              style={{
                position: "absolute",
                left: interpolate(seconds, times, values(0), {
                  ...clamp,
                  easing: Easing.inOut(Easing.cubic),
                }),
                top: interpolate(seconds, times, values(1), {
                  ...clamp,
                  easing: Easing.inOut(Easing.cubic),
                }),
                width: interpolate(seconds, times, values(2), {
                  ...clamp,
                  easing: Easing.inOut(Easing.cubic),
                }),
                height: interpolate(seconds, times, values(2), {
                  ...clamp,
                  easing: Easing.inOut(Easing.cubic),
                }),
                opacity: interpolate(seconds, times, values(3), clamp),
                translate: "-50% -50%",
                rotate: `${angle}deg`,
                filter:
                  index === 8 && seconds >= 26 && seconds < 28.5
                    ? `drop-shadow(0 0 ${22 + 10 * Math.sin(seconds * Math.PI * 4)}px #ff3434aa)`
                    : "drop-shadow(0 18px 18px #0006)",
                zIndex: selected ? 3 : 1,
              }}
            >
              <Sprite crop={part.crop} />
              <div
                style={{
                  position: "absolute",
                  left: -50,
                  right: -50,
                  bottom: -30,
                  textAlign: "center",
                  fontFamily: "ShowcaseDisplay",
                  fontSize: 25,
                  color: index >= 5 ? palette.amber : palette.mint,
                  rotate: `${-angle}deg`,
                  opacity: selected ? 1 : 0,
                }}
              >
                {part.name}
              </div>
            </div>
          );
        })}
        {chapters.map((chapter, index) => (
          <div
            key={chapter.tag}
            style={{
              position: "absolute",
              left: 1340,
              top: 285,
              width: 460,
              opacity: interpolate(
                seconds,
                [
                  chapter.start,
                  chapter.start + 0.35,
                  chapter.end - 0.2,
                  chapter.end,
                ],
                [0, 1, 1, 0],
                clamp,
              ),
              translate: `${interpolate(seconds, [chapter.start, chapter.start + 0.5], [35, 0], clamp)}px 0`,
            }}
          >
            <Evidence style={{ fontSize: 24 }}>{chapter.tag}</Evidence>
            <div
              style={{
                whiteSpace: "pre-line",
                fontFamily: "ShowcaseDisplay",
                fontSize: 64,
                lineHeight: 1.05,
                marginTop: 28,
                letterSpacing: -1.5,
              }}
            >
              {chapter.title}
            </div>
            <div
              style={{
                fontSize: 32,
                lineHeight: 1.35,
                color: palette.muted,
                marginTop: 28,
              }}
            >
              {chapter.body}
            </div>
            <div
              style={{
                fontSize: 24,
                lineHeight: 1.4,
                color: index === 4 ? palette.amber : palette.mint,
                marginTop: 32,
                paddingTop: 20,
                borderTop: "1px solid #79f2cd45",
              }}
            >
              {chapter.detail}
            </div>
          </div>
        ))}
        <svg
          width="1920"
          height="1080"
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            zIndex: 4,
          }}
        >
          <path
            d="M 400 770 C 500 710 520 830 600 770 S 700 710 760 770 S 850 830 940 770"
            fill="none"
            stroke={palette.mint}
            strokeWidth="3"
            pathLength="1"
            strokeDasharray="1"
            strokeDashoffset={interpolate(seconds, [10.3, 12], [1, 0], clamp)}
            opacity={interpolate(
              seconds,
              [9.5, 10.3, 14, 14.5],
              [0, 0.8, 0.8, 0],
              clamp,
            )}
          />
          <g
            opacity={interpolate(
              seconds,
              [19.5, 20.3, 25, 25.5],
              [0, 0.8, 0.8, 0],
              clamp,
            )}
          >
            <path
              d="M 280 680 L 280 700 M 450 510 L 490 510 M 820 510 L 865 510"
              fill="none"
              stroke={palette.amber}
              strokeWidth="3"
              strokeDasharray="9 10"
              strokeDashoffset={-frame * 1.5}
            />
            <text
              x="500"
              y="910"
              fill={palette.amber}
              fontSize="24"
              fontFamily="ShowcaseDisplay"
            >
              MISURA → CARICA → ACCUMULO
            </text>
          </g>
        </svg>
        <Evidence
          amber
          style={{ position: "absolute", left: 112, bottom: 70, fontSize: 22 }}
        >
          ESPLOSO ILLUSTRATIVO · GEOMETRIE SEMPLIFICATE · COLLEGAMENTI
          FUNZIONALI
        </Evidence>
        <div
          style={{
            position: "absolute",
            left: 112,
            right: 112,
            bottom: 40,
            height: 2,
            background: "#79f2cd25",
          }}
        >
          <div
            style={{
              width: `${interpolate(frame, [0, 30.3 * fps], [0, 100], clamp)}%`,
              height: "100%",
              background: palette.mint,
            }}
          />
        </div>
      </div>
    </FilmFrame>
  );
};
