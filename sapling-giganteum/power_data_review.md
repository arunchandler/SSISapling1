# review of sapling flight data (quick)

Measurement using the current ranger showed average power consumption on the ground was 385 mW (leading to 2194.5 J per 90 minute period), and average energy use for beaconing per orbit (90 minute interval) was 864.50 J. This gives an estimate of (864/2194 + 1) * 0.385 = 0.536 W of power consumption on average, which is consistent with values seen in telemetry which cluster around 400 mW.

Based on the ratio of beacons with charging flag high to total beacons, the satellite is charging ~0.615 of each orbit.

Using 385 mW as a low estimate, and 550mW as a high estimate, and assuming that all power generated is used (note: bad assumption since the charger won't charge beyond the max of the batteries).

Lower Bound:
0.385 * 1/0.61 = 0.631 W

Conservative Upper Bound:
0.550 * 1/0.61 = 0.901 W
