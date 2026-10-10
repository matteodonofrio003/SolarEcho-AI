#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>
#include <stdio.h>

// Piezo analogico: A0 deve ricevere un segnale condizionato e protetto 0..3,3 V.
// La sola resistenza da 1 Mohm in parallelo al piezo NON protegge l'ADC.
ModulinoMovement movement;

constexpr uint32_t kCaptureDurationUs = 6000000UL;
constexpr size_t kMaxSamples = 768;  // 6 s a 104 Hz nominali, con margine.
constexpr int kPiezoPin = A0;
constexpr uint32_t kPiezoPeriodUs = 1000;  // Obiettivo di polling, non frequenza garantita.
constexpr uint16_t kPiezoThresholdOn = 512;  // Soglie diagnostiche da calibrare sul montaggio.
constexpr uint16_t kPiezoThresholdOff = 256;
constexpr uint32_t kPiezoLockoutMs = 800;
constexpr uint32_t kSerialPeriodMs = 200;  // Anteprima a 5 Hz.

uint32_t piezoThresholdCrossings = 0;
uint32_t piezoEvents = 0;
uint32_t piezoSuppressedCrossings = 0;
uint32_t lastPiezoEventMs = 0;
bool hasPiezoEvent = false;
bool piezoActive = false;
bool havePiezoSample = false;
uint16_t piezoAdc = 0;
uint16_t piezoSerialPeak = 0;
uint16_t piezoSamplePeak = 0;
uint32_t lastPiezoReadUs = 0;
uint32_t piezoTimestampUs = 0;
uint32_t piezoMaxGapUs = 0;

void pollPiezo() {
  const uint32_t nowUs = micros();
  const uint32_t gapUs = nowUs - lastPiezoReadUs;
  if (havePiezoSample && gapUs < kPiezoPeriodUs) return;
  if (havePiezoSample && gapUs > piezoMaxGapUs) piezoMaxGapUs = gapUs;
  lastPiezoReadUs = nowUs;
  piezoAdc = analogRead(kPiezoPin);
  piezoTimestampUs = nowUs;
  havePiezoSample = true;
  if (piezoAdc > piezoSerialPeak) piezoSerialPeak = piezoAdc;
  if (piezoAdc > piezoSamplePeak) piezoSamplePeak = piezoAdc;

  // Isteresi: un nuovo fronte richiede prima il ritorno sotto la soglia OFF.
  if (piezoActive) {
    if (piezoAdc <= kPiezoThresholdOff) piezoActive = false;
    return;
  }
  if (piezoAdc < kPiezoThresholdOn) return;
  piezoActive = true;
  ++piezoThresholdCrossings;
  const uint32_t nowMs = millis();
  if (!hasPiezoEvent || nowMs - lastPiezoEventMs >= kPiezoLockoutMs) {
    ++piezoEvents;
    lastPiezoEventMs = nowMs;
    hasPiezoEvent = true;
  } else {
    ++piezoSuppressedCrossings;
  }
}

struct Sample {
  uint32_t timestamp_us;  // Relativo all'inizio della cattura.
  float ax_g;
  float ay_g;
  float az_g;
  uint8_t piezo_state;
  uint32_t piezo_threshold_crossings;
  uint32_t piezo_event_count;
  uint16_t piezo_adc;
  uint16_t piezo_peak_adc;
  uint32_t piezo_timestamp_us;
  uint32_t piezo_max_gap_us;
};

Sample samples[kMaxSamples];
size_t sampleCount = 0;
size_t sendIndex = 0;
uint32_t captureStartUs = 0;
int captureId = 0;
bool sensorReady = false;
bool overflow = false;
bool haveAcceleration = false;
float latestX = 0;
float latestY = 0;
float latestZ = 0;
uint32_t lastAccelerationMs = 0;
uint32_t lastSerialMs = 0;

enum class State { IDLE, CAPTURING, SENDING };
State state = State::IDLE;

// provide_safe esegue questa funzione nel loop, evitando accessi concorrenti allo stato.
// 1 = avviata; 0 = occupato; -1 = sensore non inizializzato.
int startCapture(int requestedId) {
  if (!sensorReady) return -1;
  if (state != State::IDLE) return 0;

  captureId = requestedId;
  sampleCount = 0;
  sendIndex = 0;
  overflow = false;
  captureStartUs = micros();
  havePiezoSample = false;  // Nuovo timestamp ADC appartenente alla finestra.
  piezoSamplePeak = 0;
  piezoMaxGapUs = 0;
  state = State::CAPTURING;
  return 1;
}

void setup() {
  // Richiede protezione hardware; ingresso riferito a GND, senza bias a meta' scala.
  pinMode(kPiezoPin, INPUT);
  analogReadResolution(14);  // 0..16383, riferimento predefinito 3,3 V.

  Modulino.begin(Wire1);  // Qwiic dell'UNO Q: bus I2C4 a 3,3 V.
  sensorReady = movement.begin();

  Bridge.begin();
  Serial.begin(115200);  // Console/Serial Monitor di Arduino App Lab su UNO Q.
  Serial.println("SolarEcho: X/Y/Z in g; PIEZO_ADC su A0 a 14 bit; lockout=800 ms.");
  Serial.println("A0 richiede protezione hardware 0..3,3 V. Soglie ADC ON=512 OFF=256 da calibrare.");
  if (!sensorReady) Serial.println("SENSOR ERROR: Modulino Movement non inizializzato.");
  Bridge.provide_safe("solarecho_start_capture", startCapture);
}

void loop() {
  // Il trasferimento RPC interrompe il monitoraggio: non simuliamo campioni mancanti.
  if (state != State::SENDING) pollPiezo();

  // Letture continue fuori dal trasferimento; i campioni della cattura restano in RAM.
  if (sensorReady && state != State::SENDING) {
    // L'IMU segnala dati nuovi: non assumiamo che il loop equivalga a 104 Hz.
    if (movement.available() && movement.update()) {
      latestX = movement.getX();
      latestY = movement.getY();
      latestZ = movement.getZ();
      haveAcceleration = true;
      lastAccelerationMs = millis();
      if (state == State::CAPTURING) {
        const uint32_t elapsedUs = micros() - captureStartUs;
        if (elapsedUs < kCaptureDurationUs) {
          if (sampleCount < kMaxSamples) {
            samples[sampleCount++] = {
              elapsedUs, latestX, latestY, latestZ,
              (uint8_t)piezoActive, piezoThresholdCrossings, piezoEvents,
              piezoAdc, piezoSamplePeak, piezoTimestampUs - captureStartUs, piezoMaxGapUs
            };
            piezoSamplePeak = 0;
            piezoMaxGapUs = 0;
          } else {
            overflow = true;
            state = State::SENDING;
          }
        }
      }
    }
  }

  if (state == State::CAPTURING) {
    if (micros() - captureStartUs >= kCaptureDurationUs) {
      state = State::SENDING;
    }
  }

  if (state == State::SENDING) {
    if (sendIndex == 0) {
      Serial.println("Cattura terminata; trasferimento CSV. La stampa LIVE riprende dopo il trasferimento.");
      Bridge.notify("solarecho_begin", captureId, (int)sampleCount);
    }

    if (sendIndex < sampleCount) {
      const Sample& s = samples[sendIndex];
      Bridge.notify("solarecho_sample", captureId, (int)sendIndex,
                    s.timestamp_us, s.ax_g, s.ay_g, s.az_g,
                    s.piezo_state, s.piezo_threshold_crossings, s.piezo_event_count,
                    s.piezo_adc, s.piezo_peak_adc, s.piezo_timestamp_us, s.piezo_max_gap_us);
      ++sendIndex;
      delay(5);  // Trasmissione separata dalla cattura; limita il burst RPC.
    } else {
      Bridge.notify("solarecho_end", captureId, (int)sampleCount, overflow);
      state = State::IDLE;
    }
  }

  // Una sola riga seriale a 5 Hz. Nessuna stampa durante cattura e trasferimento.
  if (state == State::IDLE && millis() - lastSerialMs >= kSerialPeriodMs) {
    lastSerialMs = millis();
    char line[240];
    if (haveAcceleration && millis() - lastAccelerationMs < 500) {
      snprintf(line, sizeof(line),
               "LIVE AX=%.4f AY=%.4f AZ=%.4f g | ADC=%u PEAK=%u ACTIVE=%u RAW=%lu EVENTS=%lu SUPPRESSED=%lu",
               latestX, latestY, latestZ, (unsigned)piezoAdc, (unsigned)piezoSerialPeak,
               (unsigned)piezoActive, (unsigned long)piezoThresholdCrossings,
               (unsigned long)piezoEvents, (unsigned long)piezoSuppressedCrossings);
    } else {
      snprintf(line, sizeof(line), "SENSOR ERROR: IMU senza dati | ADC=%u PEAK=%u EVENTS=%lu",
               (unsigned)piezoAdc, (unsigned)piezoSerialPeak, (unsigned long)piezoEvents);
    }
    Serial.println(line);
    piezoSerialPeak = 0;
  }
}
