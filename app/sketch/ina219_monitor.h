#pragma once

#include <Arduino.h>
#include <Wire.h>

// Driver minimo basato sul datasheet TI INA219, sezioni 8.5 e 8.6.
// Corrente da Vshunt/R: non dipende dalla calibrazione fissa di una libreria.
class Ina219Monitor {
 public:
  enum class Result { NONE, SAMPLE, I2C_ERROR, CONFIG_ERROR, TIMEOUT, OUT_OF_RANGE };
  struct Reading {
    uint32_t timestamp_ms = 0;
    float bus_v = 0;       // VIN- rispetto a GND.
    float source_v = 0;    // VIN+ rispetto a GND: Vbus + Vshunt.
    float shunt_mv = 0;
    float current_ma = 0;  // Positivo da VIN+ verso VIN-.
    float input_power_w = 0;
    float output_power_w = 0;
  };

  Ina219Monitor(arduino::HardwareI2C& bus, uint8_t address, float shuntOhms)
      : bus_(bus), address_(address), shuntOhms_(shuntOhms) {}

  Result begin() {
    pending_ = false;
    initialized_ = false;
    lastAttemptMs_ = millis();
    if (!(shuntOhms_ > 0)) return Result::CONFIG_ERROR;
    // I registri corrente/potenza interni non sono usati. Azzeriamo la
    // calibrazione per evitare overflow di eventuali configurazioni precedenti.
    if (!writeRegister(0x05, 0) || !writeRegister(0x00, kConfigBase)) {
      return Result::I2C_ERROR;
    }
    uint16_t config = 0;
    if (!readRegister(0x00, config)) return Result::I2C_ERROR;
    if (config != kConfigBase) return Result::CONFIG_ERROR;
    initialized_ = true;
    lastStartMs_ = millis();
    return Result::NONE;
  }

  // Il chiamante deve usare poll solo fuori dalla cattura IMU.
  // Nessun delay: la conversione viene avviata e controllata in loop successivi.
  Result poll(Reading& reading) {
    const uint32_t now = millis();
    if (!initialized_) {
      return now - lastAttemptMs_ >= 5000 ? begin() : Result::NONE;
    }
    if (!pending_) {
      if (now - lastStartMs_ < 1000) return Result::NONE;
      lastStartMs_ = now;
      if (!writeRegister(0x00, kConfigBase | 0x03)) return fail(Result::I2C_ERROR);
      pending_ = true;
      lastCheckMs_ = now;
      return Result::NONE;
    }
    // 16 medie per canale: circa 17 ms complessivi, piu' margine.
    if (now - lastStartMs_ < 20 || now - lastCheckMs_ < 5) return Result::NONE;
    lastCheckMs_ = now;
    uint16_t busRaw = 0;
    if (!readRegister(0x02, busRaw)) return fail(Result::I2C_ERROR);
    if (!(busRaw & 0x02)) {  // CNVR: tutti i canali hanno completato la conversione.
      return now - lastStartMs_ >= 100 ? fail(Result::TIMEOUT) : Result::NONE;
    }
    uint16_t shuntRaw = 0;
    if (!readRegister(0x01, shuntRaw)) return fail(Result::I2C_ERROR);
    pending_ = false;
    const int32_t signedShunt = shuntRaw & 0x8000
        ? static_cast<int32_t>(shuntRaw) - 65536 : shuntRaw;
    const float busV = (busRaw >> 3) * 0.004f;
    const float shuntV = signedShunt * 0.00001f;
    const float sourceV = busV + shuntV;
    // Il FSR ADC di 32 V NON estende il limite elettrico del chip, pari a 26 V.
    // Conservativo vicino al fondo scala shunt: non stampiamo misure saturate.
    if ((busRaw & 0x01) || busV > 26.0f || sourceV > 26.0f || sourceV < -0.3f
        || signedShunt >= 31900 || signedShunt <= -31900) {
      return Result::OUT_OF_RANGE;
    }
    const float currentA = shuntV / shuntOhms_;
    reading.timestamp_ms = now;
    reading.bus_v = busV;
    reading.source_v = sourceV;
    reading.shunt_mv = shuntV * 1000.0f;
    reading.current_ma = currentA * 1000.0f;
    reading.input_power_w = sourceV * currentA;
    reading.output_power_w = busV * currentA;
    return Result::SAMPLE;
  }

  // Scarta una conversione iniziata prima di un impatto. Nessuna transazione I2C.
  void cancel() { pending_ = false; }

 private:
  // BRNG=32 V FSR, PGA=+/-320 mV, BADC/SADC=16 medie, MODE=power down.
  static constexpr uint16_t kConfigBase = (1U << 13) | (3U << 11)
      | (12U << 7) | (12U << 3);
  arduino::HardwareI2C& bus_;
  uint8_t address_;
  float shuntOhms_;
  bool initialized_ = false;
  bool pending_ = false;
  uint32_t lastAttemptMs_ = 0;
  uint32_t lastStartMs_ = 0;
  uint32_t lastCheckMs_ = 0;

  Result fail(Result result) {
    initialized_ = false;
    pending_ = false;
    lastAttemptMs_ = millis();
    return result;
  }

  bool writeRegister(uint8_t reg, uint16_t value) {
    bus_.beginTransmission(address_);
    bus_.write(reg);
    bus_.write(static_cast<uint8_t>(value >> 8));
    bus_.write(static_cast<uint8_t>(value & 0xFF));
    return bus_.endTransmission() == 0;
  }

  bool readRegister(uint8_t reg, uint16_t& value) {
    bus_.beginTransmission(address_);
    bus_.write(reg);
    if (bus_.endTransmission(false) != 0) return false;
    if (bus_.requestFrom(address_, static_cast<size_t>(2), true) != 2
        || bus_.available() < 2) return false;
    const int high = bus_.read();
    const int low = bus_.read();
    if (high < 0 || low < 0) return false;
    value = (static_cast<uint16_t>(high) << 8) | static_cast<uint16_t>(low);
    return true;
  }
};
