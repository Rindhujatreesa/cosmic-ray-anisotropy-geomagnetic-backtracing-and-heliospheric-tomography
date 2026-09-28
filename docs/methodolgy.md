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

