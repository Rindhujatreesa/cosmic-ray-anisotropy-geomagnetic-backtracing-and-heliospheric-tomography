# Data Sources

## Neutron Monitor Database

CR-TOMO uses the Neutron Monitor Database (NMDB) as its primary neutron-monitor data source.

NMDB provides measurements from neutron-monitor stations around the world, including historical and high-resolution observations.

Official source:

[https://www.nmdb.eu/](https://www.nmdb.eu/)

---

## Oulu Neutron Monitor

The initial project uses the Oulu neutron monitor.

Oulu is operated by the Sodankylä Geophysical Observatory of the University of Oulu.

Station code:

```text
OULU
```

Station coordinates:

```text
Latitude:   65.0544° N
Longitude:  25.4681° E
Altitude:   15 m
```

Effective vertical cutoff rigidity:

```text
~0.8 GV
```

Reference pressure:

```text
1000 mbar
```

Barometric coefficient:

```text
0.74 %/mbar
```

---

## Data Provenance

NMDB provides multiple representations of neutron-monitor measurements.

In particular, the database distinguishes between original and revised data.

CR-TOMO records the selected data product in analysis metadata whenever possible.

The project should never silently mix:

* original measurements,
* revised measurements,
* pressure-corrected measurements, and
* independently processed measurements.

---

## Data Storage

Raw downloaded data should be stored locally under:

```text
data/raw/
```

Processed datasets should be stored under:

```text
data/processed/
```

Large observational datasets should not be committed directly to Git unless their redistribution conditions permit it.

Instead, the repository should contain:

* retrieval instructions,
* configuration,
* metadata,
* processing code, and
* checksums where appropriate.

---

## Citation and Acknowledgement

Any publication or public analysis using NMDB data must follow the data-use conditions specified by NMDB and the individual station providers.

The Oulu station is associated with the Sodankylä Geophysical Observatory and the University of Oulu.

Researchers should consult the station-specific data-use information before publication.

