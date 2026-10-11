# TEST SINTETICO

5 CSV derivati da 5 impatti normali reali di test.

Profilo: stress.

Trasformazioni fisse, applicate solo dopo il trigger:

- stress_sustained: somma di oscillazioni persistenti di ampiezza 0,35 g su X/Y/Z, rispettivamente a 8/17/29 Hz; rampa iniziale di 50 ms.

Queste trasformazioni non sono modelli fisici validati del pannello.
Originali, timestamp, unita e pretrigger sono conservati.

Caricare SOLO i CSV in test/ nella destinazione Testing di Edge Impulse, con etichetta anomaly.
Non caricarli nel Training. Mantenere fissi modello e soglia durante il confronto.
Confrontare gli score di ogni variante con il suo originale; riportare anche i mancati rilevamenti.
Le varianti sono correlate e non sono nuove prove sperimentali.
Nessun risultato AI viene generato da questo script.
