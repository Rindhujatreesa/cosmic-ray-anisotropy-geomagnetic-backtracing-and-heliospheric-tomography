# Methodology

## Pipeline

CR-TOMO v0.1 implements:

```text
Data retrieval
      |
      v
Parsing
      |
      v
Quality control
      |
      v
Valid observations
      |
      v
Fractional variation
      |
      v
Harmonic analysis
      |
      v
Scientific visualization
```

---

## Quality Control

The current implementation identifies:

* missing values,
* negative count rates,
* robust statistical outliers.

Outliers are identified using a robust z-score based on the median absolute deviation:

$$
z_{\mathrm{robust}}=
0.6745
\frac{x-\mathrm{median}(x)}
{\mathrm{MAD}}.
$$

Observations exceeding the configured threshold are flagged.

The default threshold is:

```text
|z| > 5
```

The quality-control algorithm is intended as an initial screening method rather than a replacement for station-specific quality-control procedures.

---

## Fractional Variation

The reference intensity is calculated using the configured statistic.

The default is the median:

$$
N_0 =\text{median}(N).
$$

The fractional variation is:

$$
\delta N =100
\frac{N-N_0}{N_0}.
$$

---

## Harmonic Analysis

For a periodic signal:

$$
x(t)=
a_1\cos(\omega t)
+
b_1\sin(\omega t).
$$

The coefficients are estimated using:

$$
a_1 =
\frac{2}{N}
\sum_i
x_i\cos(\omega t_i),
$$

$$
b_1 =
\frac{2}{N}
\sum_i
x_i\sin(\omega t_i).
$$

The amplitude and phase are:

$$
A_1 =
\sqrt{a_1^2+b_1^2},
$$

$$
\phi_1 =
\text{atan2}(b_1,a_1).
$$

The current default period is 24 hours.

---

## Limitations

The current implementation does not yet include:

* neutron-monitor yield functions,
* full directional detector response,
* atmospheric cascade simulation,
* a full external magnetospheric field model,
* solar-wind coupling,
* heliospheric particle transport,
* uncertainty propagation through the complete pipeline.

These are planned extensions.

---

## Validation Strategy

Each major physical component will eventually be validated independently.

Examples include:

1. comparison with published station parameters,
2. numerical conservation tests,
3. comparison of calculated geomagnetic cutoffs with reference values,
4. trajectory convergence tests,
5. comparison between magnetic-field models,
6. sensitivity to particle rigidity,
7. uncertainty propagation.

The project should not treat numerical output as physically meaningful until the underlying numerical behavior has been tested.


## Multi-Station Analysis (v0.2)

### 1. Station-specific fractional variation

Each station is normalized independently using its own median or mean count rate:

$$

\delta I_i(t)=100\frac{N_i(t)-N_{i,0}}{N_{i,0}}.
$$

This removes the absolute count-rate scale, but does not make the stations' detector responses identical.

### 2. Timestamp alignment

The analysis retains timestamps shared by every selected station. It does not interpolate missing observations.

This avoids introducing artificial measurements but may reduce the analysis interval if one station has substantial gaps.

### 3. Least-squares harmonic fit

The fitted model is:

$$
x(t)=c_0+c_1\tau+
a_1\cos(\omega\tau)+
b_1\sin(\omega\tau),
$$

where $\tau$ is elapsed time relative to the first observation, expressed in hours.

The amplitude is:

$$
A_1=\sqrt{a_1^2+b_1^2}.
$$

The phase is reported relative to the beginning of the selected interval. It is not automatically a solar-time anisotropy direction.

### 4. Differential residuals

The network median is calculated independently at each timestamp:

$$
m(t)=\operatorname{median}_i[\delta I_i(t)].
$$

The differential residual for station $i$ is:



$$
r_i(t)=\delta I_i(t)-m(t)
$$
These residuals show how each station differs from the network median. They are not a physical anisotropy measurement and may suppress genuine signals shared by multiple stations.

### 5. Limitations

The initial implementation does not account for:

- station-specific neutron-monitor yield functions;
- directional detector response;
- atmospheric corrections validated for each station;
- time-dependent geomagnetic transmission;
- station-dependent calibration and systematic uncertainties;
- solar-time transformation and anisotropy coordinate conventions.

These effects must be addressed before interpreting inter-station differences as a physical cosmic-ray anisotropy.