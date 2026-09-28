# CR-TOMO

## Cosmic-Ray Anisotropy, Geomagnetic Backtracing and Heliospheric Tomography

CR-TOMO is an open-source research project for investigating directional variations in near-Earth cosmic-ray observations.

The project combines:

* neutron-monitor observations,
* cosmic-ray temporal variability,
* harmonic anisotropy analysis,
* geomagnetic rigidity modeling,
* particle backtracing,
* asymptotic arrival directions,
* heliospheric magnetic-field modeling, and
* directional reconstruction.

The long-term objective is to develop a reproducible computational framework for connecting ground-based cosmic-ray observations with particle arrival directions in the heliosphere.

---

## Scientific Motivation

Cosmic rays reaching Earth are affected by magnetic fields in both the heliosphere and the near-Earth environment.

A neutron monitor does not directly measure the primary cosmic-ray particle. Primary cosmic rays interact with the atmosphere and generate secondary particle cascades, including neutrons that are subsequently detected by the monitor.

The measured count rate therefore contains information about the cosmic-ray population after propagation through:

1. the heliosphere,
2. the magnetosphere,
3. the atmosphere, and
4. the detector response.

CR-TOMO investigates how this observational information can be combined with numerical particle tracing to infer directional information about cosmic-ray populations.

---

## Research Questions

The project addresses the following questions:

1. How can neutron-monitor measurements be processed reproducibly for cosmic-ray variability studies?
2. What low-amplitude temporal variations are present in neutron-monitor observations?
3. What first-harmonic signatures can be extracted from the measurements?
4. How does geomagnetic rigidity affect the accessible cosmic-ray population?
5. How do particle trajectories through the geomagnetic field determine asymptotic arrival directions?
6. How can asymptotic directions be mapped into heliospheric coordinates?
7. Can measurements from multiple neutron-monitor stations constrain a directional cosmic-ray anisotropy?

---

## Current Version

### v0.1 — Observational Cosmic-Ray Variability

The first version focuses on the observational foundation:

```text
NMDB
  |
  v
Data ingestion
  |
  v
Quality control
  |
  v
Count-rate processing
  |
  v
Fractional variation
  |
  v
First-harmonic analysis
  |
  v
Scientific figures
```

Current capabilities:

* NMDB data retrieval
* Oulu neutron-monitor configuration
* timestamp handling
* quality-control flags
* robust outlier detection
* fractional count-rate variation
* first-harmonic analysis
* automated scientific figures
* automated unit tests

---

## Planned Development

### v0.2 — Multi-station analysis

The next stage will extend the analysis to multiple neutron-monitor stations.

Planned capabilities:

* simultaneous station analysis,
* geomagnetic-cutoff comparison,
* common-mode variation removal,
* station-to-station phase comparison,
* directional response analysis.

### v0.3 — Geomagnetic particle tracing

Planned capabilities:

* rigidity-dependent particle momentum,
* relativistic velocity calculation,
* IGRF magnetic field,
* Lorentz-force integration,
* allowed/forbidden trajectories,
* cutoff-rigidity estimation.

### v0.4 — Asymptotic directions

The trajectory model will be extended to determine particle directions at the outer magnetospheric boundary.

### v0.5 — Heliospheric mapping

The asymptotic directions will be mapped using heliospheric magnetic-field models, initially using the Parker spiral.

### v0.6 — Cosmic-ray tomography

Multiple detector responses will be combined to reconstruct a directional cosmic-ray intensity distribution.

---

## Scientific Workflow

The complete planned architecture is:

```text
                    NEAR-EARTH OBSERVATIONS
                             |
              +--------------+--------------+
              |                             |
       Neutron Monitors              Spacecraft Data
              |                             |
              +--------------+--------------+
                             |
                       Data Validation
                             |
                             v
                   Cosmic-Ray Variability
                             |
                             v
                     Anisotropy Analysis
                             |
                             v
                    Geomagnetic Modeling
                             |
                             v
                     Particle Backtrace
                             |
                             v
                    Asymptotic Direction
                             |
                             v
                   Heliospheric Mapping
                             |
                             v
                         TOMOGRAPHY
```

---

## Mathematical Framework

### Fractional cosmic-ray variation

For measured count rate \(N(t)\):

$$
\delta I(t)=\frac{N(t)-N_0}{N_0}.
$$

The percentage variation is:

$$
\delta{I_{\\%}(t)}=100\times\frac{N(t)-N_0}{N_0}.
$$

### First harmonic

The first harmonic is represented as

$$
I(t)=I_0+A_1\cos(\omega t-\phi_1).
$$

The Fourier coefficients are

$$
a_1 =\frac{2}{N}\sum_ix_i\cos(\omega t_i),
$$

$$
b_1 =\frac{2}{N}\sum_ix_i\sin(\omega t_i).
$$

The amplitude is

$$
A_1 =\sqrt{a_1^2+b_1^2},
$$

and the phase is

$$
\phi_1 =\text{atan}2(b_1,a_1).
$$

### Rigidity

Particle rigidity is

$$
R=\frac{pc}{|q|}.
$$

For a particle with charge number \(Z\),

$$
p c \approx |Z|R
$$

when \(p\) is expressed in GeV/c and \(R\) in GV.

### Particle propagation

The planned relativistic trajectory model is based on

$$
\frac{d\mathbf r}{dt}=\mathbf v
$$

and

$$
\frac{d\mathbf p}{dt}=q\mathbf v\times\mathbf B.
$$

The initial geomagnetic implementation will use IGRF.

---

## Data

The primary observational data source is the Neutron Monitor Database (NMDB).

The first analysis focuses on the Oulu neutron monitor.

Oulu is operated by the Sodankylä Geophysical Observatory of the University of Oulu.

Station parameters used by this project include:

| Parameter                          |       Value |
| ---------------------------------- | ----------: |
| Latitude                           |  65.0544° N |
| Longitude                          |  25.4681° E |
| Altitude                           |        15 m |
| Effective vertical cutoff rigidity |     ~0.8 GV |
| Reference pressure                 |   1000 mbar |
| Barometric coefficient             | 0.74 %/mbar |

The exact processing state of downloaded NMDB data must always be documented because NMDB provides original and revised data products with different processing histories.

---

## Reproducibility

All analysis should be executable from a clean environment.

Install:

```bash
git clone <repository-url>
cd cr-tomo

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run the Oulu analysis:

```bash
python scripts/run_oulu_analysis.py \
    --start 2025-01-01 \
    --end 2025-01-07
```

Results are written to:

```text
data/processed/
results/figures/
```

---

## Project Philosophy

CR-TOMO distinguishes between:

* observations,
* physical models,
* numerical approximations,
* assumptions,
* validation results, and
* scientific interpretation.

Simplified models are explicitly identified as such.

The project does not claim to reproduce the full SOCRATES research pipeline. Instead, it develops an independent computational framework inspired by the scientific problem of connecting cosmic-ray observations with magnetospheric and heliospheric particle trajectories.

---

## Scientific Reproducibility

The project aims to provide:

* version-controlled code,
* documented data provenance,
* reproducible configuration,
* automated tests,
* numerical validation,
* publication-quality figures, and
* explicit model assumptions.

---

## Acknowledgement

Neutron-monitor measurements are obtained through the Neutron Monitor Database (NMDB) and originate from the individual neutron-monitor data providers.

Users of NMDB data should follow the applicable data-use conditions and acknowledge NMDB and the individual monitor providers according to the station-specific requirements.

---

## License

This project is intended for scientific and educational use.

See `LICENSE` for details.
