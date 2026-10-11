#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>
#include <stdio.h>
#include <atomic>
#include "ina219_monitor.h"

// LED rosso esterno: D7 -> resistenza 1 kohm -> anodo LED; catodo -> GND.
// LED3_R integrato replica l'allerta (attivo LOW), senza componenti aggiuntivi.
constexpr int kInspectionLedPin = D7;
std::atomic<int> inspectionLedRequested{0};
bool inspectionLedOn = false;

int requestInspectionLed(int enabled) {
  if (enabled != 0 && enabled != 1) return -1;
  // Callback del thread RPC: solo memoria atomica, nessuna API Arduino/Serial/RPC.
  inspectionLedRequested.store(enabled);
  return 1;  // Conferma della richiesta, non ancora dell'uscita fisica.
}

void applyInspectionLed() {
  const bool enabled = inspectionLedRequested.load() != 0;
  if (enabled == inspectionLedOn) return;
  digitalWrite(kInspectionLedPin, enabled ? HIGH : LOW);
  digitalWrite(LED3_R, enabled ? LOW : HIGH);
  inspectionLedOn = enabled;
  Serial.println(enabled ? "INSPECTION: LED rosso ON; consultare il motivo in dashboard."
                         : "INSPECTION: LED rosso OFF; allerta confermata/reset.");
}

// Piezo analogico: A0 deve ricevere un segnale condizionato e protetto 0..3,3 V.
// La sola resistenza da 1 Mohm in parallelo al piezo NON protegge l'ADC.
ModulinoMovement movement;

// Cablaggio confermato: INA219 sui pin SDA/SCL (Wire), shunt marcato R100.
// Wire1 resta il bus Qwiic del Modulino. 0x40 richiede A0/A1 del chip a GND;
// modificare l'indirizzo se i ponticelli del modulo sono configurati diversamente.
constexpr uint8_t kIna219Address = 0x40;
constexpr float kIna219ShuntOhms = 0.1f;
Ina219Monitor powerMonitor(Wire, kIna219Address, kIna219ShuntOhms);
Ina219Monitor::Reading latestPower;
Ina219Monitor::Result powerResult = Ina219Monitor::Result::NONE;
bool havePower = false;

void printPowerError(Ina219Monitor::Result result) {
  switch (result) {
    case Ina219Monitor::Result::I2C_ERROR:
      Serial.print("POWER SENSOR ERROR: INA219 I2C su SDA/SCL (Wire), indirizzo 0x");
      Serial.print(kIna219Address, HEX);
      Serial.println("; controllare cablaggio e indirizzo.");
      break;
    case Ina219Monitor::Result::CONFIG_ERROR:
      Serial.println("POWER SENSOR ERROR: configurazione INA219 non valida o registro non confermato.");
      break;
    case Ina219Monitor::Result::TIMEOUT:
      Serial.println("POWER SENSOR ERROR: timeout conversione INA219.");
      break;
    case Ina219Monitor::Result::OUT_OF_RANGE:
      Serial.println("POWER SENSOR ERROR: misura INA219 fuori range o saturata; corrente/potenza non valide.");
      break;
    default:
      break;
  }
}

void pollAndPrintPower() {
  Ina219Monitor::Reading reading;
  const Ina219Monitor::Result result = powerMonitor.poll(reading);
  if (result == Ina219Monitor::Result::SAMPLE) {
    latestPower = reading;
    havePower = true;
    powerResult = result;
    char line[240];
    snprintf(line, sizeof(line),
             "POWER t_ms=%lu V_IN=%.3f V V_OUT=%.3f V SHUNT=%.3f mV I=%.2f mA P_IN=%.5f W P_OUT=%.5f W",
             (unsigned long)reading.timestamp_ms, reading.source_v, reading.bus_v,
             reading.shunt_mv, reading.current_ma, reading.input_power_w, reading.output_power_w);
    Serial.println(line);
  } else {
    if (result != Ina219Monitor::Result::NONE) {
      powerResult = result;
      havePower = false;
    }
    printPowerError(result);
  }
}

constexpr uint32_t kPreTriggerUs = 200000UL;
constexpr uint32_t kPostTriggerUs = 2000000UL;
constexpr size_t kPreSamples = 32;  // Circa 300 ms a 104 Hz; selezioniamo gli ultimi 200 ms.
constexpr size_t kMaxSamples = 384;  // 2,2 s a 104 Hz, con margine.
constexpr uint32_t kAckTimeoutMs = 15000;
constexpr int kPiezoPin = A0;
constexpr uint32_t kPiezoPeriodUs = 1000;  // Obiettivo di polling, non frequenza garantita.
constexpr uint16_t kPiezoThresholdOn = 512;  // Soglie diagnostiche da calibrare sul montaggio.
constexpr uint16_t kPiezoThresholdOff = 256;
constexpr uint32_t kPiezoLockoutMs = 800;
constexpr uint32_t kSerialPeriodMs = 200;  // Anteprima a 5 Hz.
constexpr uint32_t kTelemetryPeriodMs = 1000;  // Web: solo IDLE, massimo 1 Hz.

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

// true solo per un nuovo evento accettato dal lockout.
bool pollPiezo() {
  const uint32_t nowUs = micros();
  const uint32_t gapUs = nowUs - lastPiezoReadUs;
  if (havePiezoSample && gapUs < kPiezoPeriodUs) return false;
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
    return false;
  }
  if (piezoAdc < kPiezoThresholdOn) return false;
  piezoActive = true;
  ++piezoThresholdCrossings;
  const uint32_t nowMs = millis();
  if (!hasPiezoEvent || nowMs - lastPiezoEventMs >= kPiezoLockoutMs) {
    ++piezoEvents;
    lastPiezoEventMs = nowMs;
    hasPiezoEvent = true;
    return true;
  } else {
    ++piezoSuppressedCrossings;
  }
  return false;
}

struct Sample {
  uint32_t timestamp_us;  // micros() assoluto; convertito in tempo firmato al trasferimento.
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
Sample preSamples[kPreSamples];
size_t preHead = 0;
size_t preCount = 0;
size_t sampleCount = 0;
size_t capturedPreCount = 0;
size_t sendIndex = 0;
uint32_t triggerUs = 0;
uint16_t triggerAdc = 0;
uint32_t triggerEventCount = 0;
uint32_t additionalEvents = 0;
uint32_t waitAckSinceMs = 0;
uint32_t resumedAtMs = 0;
int captureId = 0;
bool autoEnabled = false;  // Python arma dopo aver registrato i callback.
bool readyAnnounced = false;
bool sensorReady = false;
bool overflow = false;
bool haveAcceleration = false;
float latestX = 0;
float latestY = 0;
float latestZ = 0;
uint32_t lastAccelerationMs = 0;
uint32_t lastSerialMs = 0;
uint32_t lastTelemetryMs = 0;
bool ackFailed = false;

enum class State { IDLE, CAPTURING, SENDING, WAIT_ACK };
State state = State::IDLE;

int armCapture() {
  if (!sensorReady) return -1;
  if (state != State::IDLE) return 0;
  autoEnabled = true;
  return 1;
}

bool readyForImpact() {
  if (!autoEnabled || !sensorReady || state != State::IDLE || !haveAcceleration) return false;
  if (millis() - lastAccelerationMs >= 500 || preCount < 2 || piezoActive) return false;
  if (hasPiezoEvent && millis() - lastPiezoEventMs < kPiezoLockoutMs) return false;
  const size_t oldest = (preHead + kPreSamples - preCount) % kPreSamples;
  return micros() - preSamples[oldest].timestamp_us >= kPreTriggerUs;
}

void publishTelemetry() {
  // Un solo messaggio compatto: niente RPC durante CAPTURING/SENDING/WAIT_ACK.
  // Le letture sono un'anteprima, non la forma d'onda acquisita a ~104 Hz.
  if (state != State::IDLE || (!autoEnabled && !ackFailed)
      || millis() - lastTelemetryMs < kTelemetryPeriodMs) return;
  lastTelemetryMs = millis();
  const bool imuOk = sensorReady && haveAcceleration && millis() - lastAccelerationMs < 500;
  char payload[640];
  const int length = snprintf(payload, sizeof(payload),
      "{\"t_ms\":%lu,\"ready\":%u,\"imu_ok\":%u,\"ack_error\":%u,"
      "\"ax\":%.5f,\"ay\":%.5f,\"az\":%.5f,\"adc\":%u,\"peak\":%u,"
      "\"active\":%u,\"raw\":%lu,\"events\":%lu,\"suppressed\":%lu,"
      "\"power_ok\":%u,\"power_error\":%u,\"power_t_ms\":%lu,"
      "\"v_in\":%.4f,\"v_out\":%.4f,\"shunt_mv\":%.3f,\"current_ma\":%.3f,\"power_w\":%.6f,"
      "\"led_on\":%u,\"led_requested\":%u}",
      (unsigned long)millis(), (unsigned)readyForImpact(), (unsigned)imuOk, (unsigned)ackFailed,
      latestX, latestY, latestZ, (unsigned)piezoAdc, (unsigned)piezoSerialPeak,
      (unsigned)piezoActive, (unsigned long)piezoThresholdCrossings,
      (unsigned long)piezoEvents, (unsigned long)piezoSuppressedCrossings,
      (unsigned)havePower, (unsigned)powerResult, (unsigned long)latestPower.timestamp_ms,
      latestPower.source_v, latestPower.bus_v, latestPower.shunt_mv,
      latestPower.current_ma, latestPower.input_power_w,
      (unsigned)inspectionLedOn, (unsigned)inspectionLedRequested.load());
  if (length > 0 && (size_t)length < sizeof(payload)) Bridge.notify("solarecho_live", payload);
}

void beginImpactCapture() {
  powerMonitor.cancel();  // Non riusare una lettura elettrica precedente all'impatto.
  ++captureId;
  sampleCount = 0;
  sendIndex = 0;
  overflow = false;
  triggerUs = piezoTimestampUs;
  triggerAdc = piezoAdc;
  triggerEventCount = piezoEvents;
  additionalEvents = 0;
  const size_t oldest = (preHead + kPreSamples - preCount) % kPreSamples;
  for (size_t i = 0; i < preCount; ++i) {
    const Sample& s = preSamples[(oldest + i) % kPreSamples];
    const uint32_t ageUs = triggerUs - s.timestamp_us;
    if (ageUs > 0 && ageUs <= kPreTriggerUs) samples[sampleCount++] = s;
  }
  capturedPreCount = sampleCount;
  readyAnnounced = false;
  state = State::CAPTURING;
}

void resumeMonitoring() {
  preHead = 0;
  preCount = 0;
  haveAcceleration = false;
  havePiezoSample = false;
  piezoSamplePeak = 0;
  piezoSerialPeak = 0;
  piezoMaxGapUs = 0;
  readyAnnounced = false;
  resumedAtMs = millis();
  state = State::IDLE;
}

// Non riutilizziamo il buffer finche Python non conferma il salvataggio.
int acknowledgeCapture(int receivedId) {
  if (state != State::WAIT_ACK || receivedId != captureId) return 0;
  resumeMonitoring();
  return 1;
}

void setup() {
  pinMode(kInspectionLedPin, OUTPUT);
  digitalWrite(kInspectionLedPin, LOW);
  pinMode(LED3_R, OUTPUT);
  pinMode(LED3_G, OUTPUT);
  pinMode(LED3_B, OUTPUT);
  digitalWrite(LED3_R, HIGH);
  digitalWrite(LED3_G, HIGH);
  digitalWrite(LED3_B, HIGH);
  // Richiede protezione hardware; ingresso riferito a GND, senza bias a meta' scala.
  pinMode(kPiezoPin, INPUT);
  analogReadResolution(14);  // 0..16383, riferimento predefinito 3,3 V.

  Modulino.begin(Wire1);  // Qwiic dell'UNO Q: bus I2C4 a 3,3 V.
  sensorReady = movement.begin();

  Bridge.begin();
  Serial.begin(115200);  // Console/Serial Monitor di Arduino App Lab su UNO Q.
  Serial.println("SolarEcho: X/Y/Z in g; PIEZO_ADC su A0 a 14 bit; lockout=800 ms.");
  Serial.println("A0 richiede protezione hardware 0..3,3 V. Soglie ADC ON=512 OFF=256 da calibrare.");
  Wire.begin();  // INA219 su SDA/D20 e SCL/D21; livelli logici a 3,3 V.
  Serial.println("INA219: Wire/SDA/SCL, address=0x40, R_SHUNT=0.100 ohm (R100), stampa circa 1 Hz.");
  Serial.println("POWER: V_IN su VIN+, V_OUT su VIN-; I positiva da VIN+ a VIN-. Posizione nel circuito da annotare.");
  powerResult = powerMonitor.begin();
  printPowerError(powerResult);
  if (!sensorReady) Serial.println("SENSOR ERROR: Modulino Movement non inizializzato.");
  resumedAtMs = millis();
  Bridge.provide_safe("solarecho_arm", armCapture);
  Bridge.provide_safe("solarecho_ack", acknowledgeCapture);
  Bridge.provide("solarecho_inspection_led", requestInspectionLed);
}

void loop() {
  // Il trasferimento RPC interrompe il monitoraggio: non simuliamo campioni mancanti.
  if (state == State::IDLE || state == State::CAPTURING) {
    const bool wasReady = readyForImpact();
    if (pollPiezo() && wasReady) beginImpactCapture();
  }

  // Letture continue fuori dal trasferimento; i campioni della cattura restano in RAM.
  if (sensorReady && (state == State::IDLE || state == State::CAPTURING)) {
    // L'IMU segnala dati nuovi: non assumiamo che il loop equivalga a 104 Hz.
    if (movement.available() && movement.update()) {
      latestX = movement.getX();
      latestY = movement.getY();
      latestZ = movement.getZ();
      haveAcceleration = true;
      lastAccelerationMs = millis();
      const uint32_t stampUs = micros();
      const Sample current = {
        stampUs, latestX, latestY, latestZ,
        (uint8_t)piezoActive, piezoThresholdCrossings, piezoEvents,
        piezoAdc, piezoSamplePeak, piezoTimestampUs, piezoMaxGapUs
      };
      piezoSamplePeak = 0;
      piezoMaxGapUs = 0;
      if (state == State::IDLE) {
        preSamples[preHead] = current;
        preHead = (preHead + 1) % kPreSamples;
        if (preCount < kPreSamples) ++preCount;
      } else if (state == State::CAPTURING) {
        if (stampUs - triggerUs < kPostTriggerUs) {
          if (sampleCount < kMaxSamples) {
            samples[sampleCount++] = current;
          } else {
            overflow = true;
            state = State::SENDING;
          }
        }
      }
    }
  }

  if (state == State::CAPTURING) {
    if (micros() - triggerUs >= kPostTriggerUs) {
      state = State::SENDING;
    }
  }

  if (state == State::SENDING) {
    if (sendIndex == 0) {
      additionalEvents = piezoEvents - triggerEventCount;
      Serial.println("BUSY: cattura terminata; trasferimento e salvataggio CSV.");
      Bridge.notify("solarecho_begin", captureId, (int)sampleCount,
                    (int)capturedPreCount, kPreTriggerUs, kPostTriggerUs,
                    triggerAdc, triggerEventCount);
    }

    if (sendIndex < sampleCount) {
      const Sample& s = samples[sendIndex];
      Bridge.notify("solarecho_sample", captureId, (int)sendIndex,
                    (int32_t)(s.timestamp_us - triggerUs), s.ax_g, s.ay_g, s.az_g,
                    s.piezo_state, s.piezo_threshold_crossings, s.piezo_event_count,
                    s.piezo_adc, s.piezo_peak_adc,
                    (int32_t)(s.piezo_timestamp_us - triggerUs), s.piezo_max_gap_us);
      ++sendIndex;
      delay(5);  // Trasmissione separata dalla cattura; limita il burst RPC.
    } else {
      state = State::WAIT_ACK;
      waitAckSinceMs = millis();
      Bridge.notify("solarecho_end", captureId, (int)sampleCount, overflow, additionalEvents);
    }
  }

  if (state == State::WAIT_ACK && millis() - waitAckSinceMs >= kAckTimeoutMs) {
    ackFailed = true;
    autoEnabled = false;
    resumeMonitoring();
    Serial.println("SENSOR ERROR: nessuna conferma CSV da Python; riavviare la App.");
  }

  if (state == State::IDLE) {
    // Le richieste durante una cattura restano in memoria fino alla ripresa.
    applyInspectionLed();
    const bool ready = readyForImpact();
    if (ready && !readyAnnounced) {
      Serial.println("READY: far cadere una pallina; cattura automatica -200 ms / +2 s.");
      Bridge.notify("solarecho_ready", captureId);
    }
    readyAnnounced = ready;
    // Le transazioni INA219 e le stampe avvengono soltanto fuori dalla cattura.
    pollAndPrintPower();
    publishTelemetry();
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
    } else if (millis() - resumedAtMs >= 500) {
      snprintf(line, sizeof(line), "SENSOR ERROR: IMU senza dati | ADC=%u PEAK=%u EVENTS=%lu",
               (unsigned)piezoAdc, (unsigned)piezoSerialPeak, (unsigned long)piezoEvents);
    } else {
      snprintf(line, sizeof(line), "WAIT: ripresa letture IMU | ADC=%u PEAK=%u EVENTS=%lu",
               (unsigned)piezoAdc, (unsigned)piezoSerialPeak, (unsigned long)piezoEvents);
    }
    Serial.println(line);
    piezoSerialPeak = 0;
  }
}
