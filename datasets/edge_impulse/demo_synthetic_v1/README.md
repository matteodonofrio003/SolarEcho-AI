# TEST SINTETICO

15 CSV derivati da 5 impatti normali reali di test.

Trasformazioni fisse, applicate solo dopo il trigger:

- attenuated: componente dinamica moltiplicata per 0,5.
- amplified: componente dinamica moltiplicata per 2.
- added_oscillation: somma su accZ di una sinusoide a 12 Hz, ampiezza iniziale 0,08 g, decadimento esponenziale di 0,45 s.

Queste trasformazioni non sono modelli fisici validati del pannello.
Originali, timestamp, unita e pretrigger sono conservati.

Caricare SOLO i CSV in test/ nella destinazione Testing di Edge Impulse, con etichetta anomaly.
Non caricarli nel Training. Mantenere fissi modello e soglia durante il confronto.
Confrontare gli score di ogni variante con il suo originale; riportare anche i mancati rilevamenti.
Le varianti sono correlate e non sono nuove prove sperimentali.
Nessun risultato AI viene generato da questo script.
