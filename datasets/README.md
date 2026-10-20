# Dataset

## Acquisizioni originali da usare

Ogni evento resta una coppia CSV + JSON. La deduplicazione non ha cambiato
i contenuti o le assegnazioni dei seguenti gruppi:

| Cartella in `raw/` | Ruolo | Eventi |
| --- | --- | ---: |
| `demo_normal_training/` | Training normale del lotto demo | 18 |
| `demo_normal_calibration/` | Calibrazione separata del lotto demo | 5 |
| `demo_normal_test/` | Test normale separato del lotto demo | 5 |
| `normal/` | Raccolta normale precedente | 42 |
| `normal_test/` | Test normale precedente | 8 |
| `modified_test/` | Test con massa, condizione annotata dal team | 8 |
| `restored_test/` | Test dopo ripristino | 6 |

Non unire automaticamente i lotti precedenti al training corrente: montaggio,
sessione e protocollo devono restare tracciabili. L'appartenenza a una cartella
non certifica l'efficacia del modello o l'esistenza di danni.

## Organizzazione

- `raw/`: acquisizioni canoniche, divise per condizione e gruppo.
- `edge_impulse/`: export e report dei lotti già prodotti. Gli export storici
  possono avere finestre diverse: leggere il rispettivo `export_report.json`.
- `rejected/`: archivi delle acquisizioni escluse, conservate per audit.
- `manifests/archive/`: report originali della divisione del lotto demo.

Le vecchie cartelle generiche `raw/demo/` e `raw/raw/` contenevano copie delle
acquisizioni già assegnate ai gruppi. Sono state deduplicate verificando sia il
CSV sia il JSON. I tre eventi esclusi 29–31 sono conservati senza alterazioni
in [demo_excluded_20261017.zip](rejected/demo_excluded_20261017.zip).

I percorsi di origine nei report storici descrivono l'organizzazione dell'epoca.
Il [manifest del riordino](../docs/archive/REPOSITORY_CLEANUP_20261017.json)
permette di risalire alla copia attuale o al membro dello ZIP tramite SHA-256.

Per produrre nuovi CSV usare la [guida di export](../docs/EDGE_IMPULSE_EXPORT.md):
il valore predefinito corrente è **100 Hz, 200 campioni XYZ, [-150, +1850) ms**.
