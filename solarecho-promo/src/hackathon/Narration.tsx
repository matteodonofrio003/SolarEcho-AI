import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { BasicCaptions } from "./basic-captions";
export const Narration = () => (
  <AbsoluteFill>
    <Sequence
      name="Voce / problema"
      from={24}
      durationInFrames={498}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-problema.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Un",
            startMs: 94.88,
            endMs: 257.64,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " impatto",
            startMs: 269.29,
            endMs: 699.49,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " può",
            startMs: 711.09,
            endMs: 850.64,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " durare",
            startMs: 862.25,
            endMs: 1152.94,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " un",
            startMs: 1164.55,
            endMs: 1257.57,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " istante.",
            startMs: 1269.18,
            endMs: 1885.4,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Le",
            startMs: 2697.46,
            endMs: 2906.73,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sue",
            startMs: 2918.38,
            endMs: 3104.4,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " conseguenze",
            startMs: 3116.05,
            endMs: 3767.16,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " possono",
            startMs: 3778.77,
            endMs: 4150.85,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " durare",
            startMs: 4162.45,
            endMs: 4569.39,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " anni.",
            startMs: 4581.04,
            endMs: 4976.37,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Grandine,",
            startMs: 5790.25,
            endMs: 6313.47,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vento",
            startMs: 6522.75,
            endMs: 6848.3,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 6859.91,
            endMs: 6906.43,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " urti",
            startMs: 6918.08,
            endMs: 7231.99,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " mettono",
            startMs: 7243.64,
            endMs: 7627.32,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " alla",
            startMs: 7638.93,
            endMs: 7801.69,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " prova",
            startMs: 7813.33,
            endMs: 8022.61,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " i",
            startMs: 8034.26,
            endMs: 8092.38,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " pannelli.",
            startMs: 8104.03,
            endMs: 8720.24,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Un’alterazione",
            startMs: 9534.12,
            endMs: 10301.48,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " non",
            startMs: 10313.13,
            endMs: 10510.79,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sempre",
            startMs: 10522.44,
            endMs: 10906.12,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " si",
            startMs: 10917.73,
            endMs: 11045.63,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vede",
            startMs: 11057.27,
            endMs: 11278.2,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " subito.",
            startMs: 11289.81,
            endMs: 11836.29,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Capire",
            startMs: 12650.16,
            endMs: 13057.1,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " quando",
            startMs: 13068.75,
            endMs: 13347.8,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " controllare",
            startMs: 13359.4,
            endMs: 13987.26,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " protegge",
            startMs: 13998.91,
            endMs: 14487.23,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " produzione",
            startMs: 14498.88,
            endMs: 15103.48,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 15115.09,
            endMs: 15138.35,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " risorse.",
            startMs: 15149.96,
            endMs: 15777.82,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / soluzione"
      from={564}
      durationInFrames={561}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-soluzione.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Solar",
            startMs: 95.17,
            endMs: 550.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Echo",
            startMs: 561.65,
            endMs: 829.91,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " AI",
            startMs: 841.55,
            endMs: 1063.15,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " ascolta",
            startMs: 1074.83,
            endMs: 1494.7,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " la",
            startMs: 1506.34,
            endMs: 1587.97,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " firma",
            startMs: 1599.61,
            endMs: 1902.84,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vibrazionale",
            startMs: 1914.52,
            endMs: 2567.63,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " del",
            startMs: 2579.27,
            endMs: 2730.88,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " pannello.",
            startMs: 2742.57,
            endMs: 3360.66,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Il",
            startMs: 4175.16,
            endMs: 4373.43,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " piezo",
            startMs: 4385.12,
            endMs: 4723.31,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " rileva",
            startMs: 4734.96,
            endMs: 5049.83,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " l’impatto.",
            startMs: 5061.51,
            endMs: 5702.93,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Il",
            startMs: 6519.34,
            endMs: 6705.92,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sensore",
            startMs: 6717.6,
            endMs: 7160.8,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " di",
            startMs: 7172.44,
            endMs: 7277.4,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " movimento",
            startMs: 7289.04,
            endMs: 7743.88,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " misura",
            startMs: 7755.56,
            endMs: 8163.74,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " le",
            startMs: 8175.43,
            endMs: 8245.41,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vibrazioni",
            startMs: 8257.06,
            endMs: 8886.83,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sui",
            startMs: 8898.48,
            endMs: 9108.39,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " tre",
            startMs: 9120.07,
            endMs: 9365.0,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " assi.",
            startMs: 9376.64,
            endMs: 9808.15,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Arduino",
            startMs: 10624.51,
            endMs: 11067.71,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " UNO",
            startMs: 11079.35,
            endMs: 11312.59,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Q",
            startMs: 11324.28,
            endMs: 11487.53,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " raccoglie",
            startMs: 11499.22,
            endMs: 11989.03,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " i",
            startMs: 12000.71,
            endMs: 12059.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dati",
            startMs: 12070.69,
            endMs: 12455.55,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 12467.19,
            endMs: 12490.52,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " li",
            startMs: 12502.2,
            endMs: 12607.16,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " analizza",
            startMs: 12618.8,
            endMs: 13062.0,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sul",
            startMs: 13073.64,
            endMs: 13260.23,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dispositivo.",
            startMs: 13271.91,
            endMs: 14053.3,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " È",
            startMs: 14869.66,
            endMs: 15032.92,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Edge",
            startMs: 15044.6,
            endMs: 15242.87,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " AI:",
            startMs: 15254.56,
            endMs: 15674.42,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " intelligenza",
            startMs: 15930.95,
            endMs: 16689.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " artificiale",
            startMs: 16700.7,
            endMs: 17295.5,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " locale.",
            startMs: 17307.15,
            endMs: 17866.94,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / impatto"
      from={1164}
      durationInFrames={234}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-impatto.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "La",
            startMs: 98.08,
            endMs: 338.46,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " pallina",
            startMs: 350.5,
            endMs: 747.12,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " colpisce",
            startMs: 759.12,
            endMs: 1251.92,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " il",
            startMs: 1263.96,
            endMs: 1324.04,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " pannello.",
            startMs: 1336.04,
            endMs: 1985.08,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Il",
            startMs: 2824.5,
            endMs: 3016.79,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sistema",
            startMs: 3028.83,
            endMs: 3497.58,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " rileva",
            startMs: 3509.62,
            endMs: 3834.12,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " l’urto:",
            startMs: 3846.17,
            endMs: 4350.96,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " da",
            startMs: 4591.33,
            endMs: 4783.62,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " solo,",
            startMs: 4795.67,
            endMs: 5168.25,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " non",
            startMs: 5456.75,
            endMs: 5661.08,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dimostra",
            startMs: 5673.08,
            endMs: 6081.75,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " un",
            startMs: 6093.75,
            endMs: 6225.96,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " danno.",
            startMs: 6238.0,
            endMs: 6754.83,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / acquisizione"
      from={1425}
      durationInFrames={264}
      premountFor={30}
    >
      <Audio
        src={staticFile("hackathon/voice-acquisizione.wav")}
        volume={0.94}
      />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "I",
            startMs: 86.66,
            endMs: 245.95,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sensori",
            startMs: 256.56,
            endMs: 670.71,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " misurano",
            startMs: 681.35,
            endMs: 1137.99,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " la",
            startMs: 1148.59,
            endMs: 1244.16,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " risposta.",
            startMs: 1254.8,
            endMs: 1849.49,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " La",
            startMs: 2591.15,
            endMs: 2771.68,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dashboard",
            startMs: 2782.29,
            endMs: 3238.92,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " mostra",
            startMs: 3249.53,
            endMs: 3621.2,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " le",
            startMs: 3631.84,
            endMs: 3695.57,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vibrazioni",
            startMs: 3706.17,
            endMs: 4247.77,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sui",
            startMs: 4258.38,
            endMs: 4449.51,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " tre",
            startMs: 4460.15,
            endMs: 4683.17,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " assi:",
            startMs: 4693.78,
            endMs: 4980.48,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " una",
            startMs: 5171.66,
            endMs: 5352.19,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " traccia",
            startMs: 5362.79,
            endMs: 5670.74,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " registrata,",
            startMs: 5681.38,
            endMs: 6339.8,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " insieme",
            startMs: 6594.66,
            endMs: 7030.06,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " ai",
            startMs: 7040.66,
            endMs: 7136.23,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dati",
            startMs: 7146.87,
            endMs: 7380.49,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dell’evento.",
            startMs: 7391.09,
            endMs: 8038.87,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / analisi"
      from={1725}
      durationInFrames={324}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-analisi.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Il",
            startMs: 98.08,
            endMs: 278.37,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " modello",
            startMs: 290.38,
            endMs: 735.08,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " confronta",
            startMs: 747.12,
            endMs: 1251.92,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " il",
            startMs: 1263.96,
            endMs: 1300.0,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " segnale",
            startMs: 1312.0,
            endMs: 1816.79,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " con",
            startMs: 1828.83,
            endMs: 2033.17,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " il",
            startMs: 2045.21,
            endMs: 2129.33,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " riferimento.",
            startMs: 2141.33,
            endMs: 2994.71,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Lo",
            startMs: 3834.12,
            endMs: 4062.5,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " score",
            startMs: 4074.5,
            endMs: 4314.88,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " misura",
            startMs: 4326.92,
            endMs: 4723.54,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " lo",
            startMs: 4735.58,
            endMs: 4843.75,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " scostamento",
            startMs: 4855.75,
            endMs: 5444.71,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dalla",
            startMs: 5456.75,
            endMs: 5697.12,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " firma",
            startMs: 5709.12,
            endMs: 6033.62,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " normale:",
            startMs: 6045.67,
            endMs: 6562.5,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " non",
            startMs: 6802.88,
            endMs: 6983.17,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " è",
            startMs: 6995.21,
            endMs: 7043.29,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " una",
            startMs: 7055.29,
            endMs: 7259.62,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " percentuale",
            startMs: 7271.62,
            endMs: 7896.62,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " di",
            startMs: 7908.67,
            endMs: 8016.83,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " danno.",
            startMs: 8028.83,
            endMs: 8545.67,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / risultato"
      from={2082}
      durationInFrames={300}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-risultato.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Oltre",
            startMs: 92.04,
            endMs: 407.87,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " soglia,",
            startMs: 419.13,
            endMs: 847.76,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " l’ispezione",
            startMs: 1084.6,
            endMs: 1750.07,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " è",
            startMs: 1761.37,
            endMs: 1817.75,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " consigliata.",
            startMs: 1829.05,
            endMs: 2629.89,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Dashboard",
            startMs: 3428.9,
            endMs: 4060.54,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 4071.84,
            endMs: 4128.23,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " LED",
            startMs: 4139.49,
            endMs: 4308.68,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " mostrano",
            startMs: 4319.98,
            endMs: 4805.0,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " la",
            startMs: 4816.26,
            endMs: 4917.77,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " segnalazione.",
            startMs: 4929.07,
            endMs: 5752.47,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Il",
            startMs: 6553.27,
            endMs: 6745.03,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " test",
            startMs: 6756.29,
            endMs: 7060.81,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sintetico",
            startMs: 7072.11,
            endMs: 7647.37,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " non",
            startMs: 7658.63,
            endMs: 7805.27,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dimostra",
            startMs: 7816.57,
            endMs: 8267.72,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " danni",
            startMs: 8279.02,
            endMs: 8538.46,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " fisici.",
            startMs: 8549.72,
            endMs: 9203.93,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / economia"
      from={2424}
      durationInFrames={606}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-economia.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Per",
            startMs: 96.78,
            endMs: 286.52,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " chi",
            startMs: 298.4,
            endMs: 417.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " gestisce",
            startMs: 428.85,
            endMs: 974.38,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " un",
            startMs: 986.22,
            endMs: 1104.83,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " impianto,",
            startMs: 1116.71,
            endMs: 1792.69,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " la",
            startMs: 1994.31,
            endMs: 2184.05,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " domanda",
            startMs: 2195.93,
            endMs: 2646.61,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " è:",
            startMs: 2658.45,
            endMs: 2788.9,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dove",
            startMs: 3073.53,
            endMs: 3298.87,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " intervenire",
            startMs: 3310.71,
            endMs: 3903.68,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " prima?",
            startMs: 3915.53,
            endMs: 4342.48,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Ai",
            startMs: 5171.69,
            endMs: 5349.59,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " controlli",
            startMs: 5361.47,
            endMs: 5859.56,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " programmati,",
            startMs: 5871.44,
            endMs: 6583.02,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Solar",
            startMs: 6796.48,
            endMs: 7187.84,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Echo",
            startMs: 7199.68,
            endMs: 7460.58,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " AI",
            startMs: 7472.46,
            endMs: 7697.8,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " affianca",
            startMs: 7709.64,
            endMs: 8184.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " segnali",
            startMs: 8195.89,
            endMs: 8682.13,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " per",
            startMs: 8693.97,
            endMs: 8848.15,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " dare",
            startMs: 8860.03,
            endMs: 9085.37,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " priorità",
            startMs: 9097.21,
            endMs: 9536.01,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " alle",
            startMs: 9547.89,
            endMs: 9690.23,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " ispezioni.",
            startMs: 9702.07,
            endMs: 10437.37,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " L’obiettivo:",
            startMs: 11278.42,
            endMs: 11930.68,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " meno",
            startMs: 12167.9,
            endMs: 12428.81,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " controlli",
            startMs: 12440.65,
            endMs: 12926.89,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " inutili,",
            startMs: 12938.77,
            endMs: 13413.14,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " interventi",
            startMs: 13543.59,
            endMs: 14207.73,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " più",
            startMs: 14219.57,
            endMs: 14350.02,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " mirati",
            startMs: 14361.9,
            endMs: 14812.58,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 14824.42,
            endMs: 14883.71,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " costi",
            startMs: 14895.59,
            endMs: 15263.22,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " potenzialmente",
            startMs: 15275.07,
            endMs: 16057.78,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " ridotti.",
            startMs: 16069.66,
            endMs: 16650.79,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Benefici",
            startMs: 17492.83,
            endMs: 18062.08,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " da",
            startMs: 18073.92,
            endMs: 18204.37,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " validare",
            startMs: 18216.25,
            endMs: 18643.21,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " sul",
            startMs: 18655.05,
            endMs: 18844.79,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " campo.",
            startMs: 18856.67,
            endMs: 19366.64,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / innovazione"
      from={3075}
      durationInFrames={261}
      premountFor={30}
    >
      <Audio
        src={staticFile("hackathon/voice-innovazione.wav")}
        volume={0.94}
      />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Firma",
            startMs: 91.13,
            endMs: 413.44,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " vibrazionale",
            startMs: 424.57,
            endMs: 1102.57,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " e",
            startMs: 1113.7,
            endMs: 1158.17,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " AI",
            startMs: 1169.26,
            endMs: 1324.85,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " locale.",
            startMs: 1335.99,
            endMs: 1858.39,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Manutenzione",
            startMs: 2634.17,
            endMs: 3345.53,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " intelligente.",
            startMs: 3356.63,
            endMs: 4168.02,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Prossimo",
            startMs: 4946.04,
            endMs: 5368.41,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " passo:",
            startMs: 5379.51,
            endMs: 5768.52,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " validazione",
            startMs: 5968.61,
            endMs: 6613.27,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " su",
            startMs: 6624.37,
            endMs: 6757.77,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " alterazioni",
            startMs: 6768.86,
            endMs: 7324.6,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " fisiche.",
            startMs: 7335.73,
            endMs: 7902.6,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
    <Sequence
      name="Voce / finale"
      from={3378}
      durationInFrames={147}
      premountFor={30}
    >
      <Audio src={staticFile("hackathon/voice-finale.wav")} volume={0.94} />
      <BasicCaptions
        width={1900}
        combineTokensWithinMilliseconds={2200}
        style={{
          position: "absolute",
          left: 200,
          bottom: 65,
          transform: "scale(.8)",
          transformOrigin: "bottom left",
        }}
        captions={[
          {
            text: "Solar",
            startMs: 92.71,
            endMs: 501.71,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " Echo",
            startMs: 513.05,
            endMs: 808.43,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " AI.",
            startMs: 819.78,
            endMs: 1126.5,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
          {
            text: " Il",
            startMs: 1919.97,
            endMs: 2101.73,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " pannello",
            startMs: 2113.11,
            endMs: 2567.52,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " che",
            startMs: 2578.9,
            endMs: 2703.87,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " riconosce",
            startMs: 2715.21,
            endMs: 3192.35,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " i",
            startMs: 3203.73,
            endMs: 3283.25,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " propri",
            startMs: 3294.63,
            endMs: 3578.67,
            timestampMs: null,
            confidence: null,
          },
          {
            text: " danni.",
            startMs: 3590.01,
            endMs: 4078.53,
            timestampMs: null,
            confidence: null,
            pageBreakAfter: true,
          },
        ]}
      />
    </Sequence>
  </AbsoluteFill>
);
