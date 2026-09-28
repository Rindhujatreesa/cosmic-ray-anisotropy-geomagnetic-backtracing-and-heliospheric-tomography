# Scientific Background

## 1. Cosmic Rays

Cosmic rays are energetic charged particles propagating through interplanetary and interstellar space.

Near Earth, the observed cosmic-ray population is affected by magnetic fields in the heliosphere and Earth's magnetosphere.

The intensity observed at Earth therefore depends on both the incident particle population and the transport through the magnetic environment.

---

## 2. Neutron Monitors

A neutron monitor detects secondary particles produced when primary cosmic rays interact with Earth's atmosphere.

A simplified chain is:

```text
Primary cosmic ray
       |
       v
Atmospheric interaction
       |
       v
Particle cascade
       |
       v
Secondary neutrons
       |
       v
Neutron monitor
```

The neutron-monitor count rate therefore acts as a proxy for variations in the cosmic-ray flux reaching the Earth's atmosphere.

---

## 3. Geomagnetic Rigidity

A charged particle moving through a magnetic field experiences the Lorentz force.

The rigidity is defined as

$$
R=\frac{pc}{|q|}.
$$

High-rigidity particles are less strongly deflected by magnetic fields.

Low-rigidity particles are more strongly affected.

Consequently, neutron monitors at different geomagnetic locations have different directional and rigidity responses.

---

## 4. Atmospheric Pressure

Atmospheric pressure changes the amount of material through which secondary particles propagate before reaching a detector.

Neutron-monitor count rates therefore exhibit a barometric response.

A simplified exponential correction can be written as

$$
N_{\mathrm{corr}}=N_{\mathrm{obs}}\exp[\beta(P-P_0)].
$$

The coefficient and sign convention must be taken from the relevant station documentation.

CR-TOMO treats pressure correction as a documented processing step rather than assuming that all NMDB products require the same correction.

---

## 5. Cosmic-Ray Variability

The fractional variation of the measured count rate is

$$
\delta I(t)=\frac{N(t)-N_0}{N_0}.
$$

This representation removes the absolute detector count scale and makes relative temporal changes easier to compare.

---

## 6. Harmonic Analysis

Periodic directional signatures can be investigated using Fourier analysis.

For a harmonic with angular frequency $\omega$,

$$
x(t)=a_1\cos(\omega t)+b_1\sin(\omega t).
$$

The amplitude is

$$
A_1=\sqrt{a_1^2+b_1^2}.
$$

The phase is

$$
\phi_1=\text{atan2}(b_1,a_1).
$$

The first harmonic provides a compact description of the amplitude and phase of a periodic variation.

---

## 7. Geomagnetic Backtracing

A charged particle propagating through a magnetic field follows the relativistic Lorentz equation:

$$
\frac{d\mathbf p}{dt}=q\left(\mathbf E+\mathbf v\times\mathbf B\right).
$$

For an initial implementation in a predominantly magnetic region:

$$
\frac{d\mathbf p}{dt}=q\mathbf v\times\mathbf B.
$$

The particle position evolves according to

$$
\frac{d\mathbf r}{dt}=\mathbf v.
$$

Numerical integration of these equations allows the trajectory to be traced backward from the detector toward the outer magnetosphere.

---

## 8. Asymptotic Directions

A particle detected at a neutron monitor does not necessarily arrive from the same geographic direction as its original interplanetary trajectory.

The geomagnetic field changes its path.

The direction obtained when the trajectory reaches a sufficiently distant outer boundary is called the asymptotic direction.

This provides a bridge between:

```text
Detector coordinates
        |
        v
Geomagnetic trajectory
        |
        v
Asymptotic direction
        |
        v
Heliospheric interpretation
```

---

## 9. Heliospheric Mapping

The first heliospheric model used by CR-TOMO is the Parker spiral.

In a simplified heliospheric model,

$$
B_\phi=-\frac{\Omega r\sin\theta}{V_{\mathrm{sw}}}B_r.
$$

where:

* $\Omega$ is the solar rotation rate,
* $r$ is heliocentric distance,
* $\theta$ is heliographic colatitude,
* $V_{\mathrm{sw}}$ is solar-wind speed.

This model is deliberately simplified.

It provides a first framework for relating near-Earth asymptotic directions to heliospheric magnetic-field geometry.

---

## 10. Tomography

The long-term objective is to reconstruct a directional cosmic-ray intensity distribution.

Conceptually:

$$
d_i=\int K_i(\Omega)F(\Omega)d\Omega+\epsilon_i
$$

where:

* $d_i$ is an observation,
* $K_i$ represents the directional response of detector $i$,
* $F(\Omega)$ is the directional cosmic-ray intensity,
* $\epsilon_i$ represents measurement and modeling uncertainty.

Multiple neutron monitors provide different directional responses.

Combining those measurements can therefore constrain the directional structure of the cosmic-ray population.

---

## 11. Scope

The initial implementation does not attempt to reproduce the complete physical complexity of the heliosphere or neutron-monitor detector response.

Instead, the project progressively replaces simplified models with more sophisticated models as validation becomes available.

This keeps each stage independently testable.

