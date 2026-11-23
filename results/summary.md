# Red vs. blue agent comparison

- Variants: availability, confidentiality, integrity; scenarios [1, 2, 3, 4, 5]; 50 seeds each; 30 steps per game
- Games played: 5500 (0 errored)
- `blue_mean` = average total blue reward per game (closer to 0 is better for blue)
- `impact_rate` = share of games where red landed at least one successful Impact
- `final_step_mean` = blue reward on the last step (how bad things are when the game ends)

## availability

### vs. B_line (best defender: **ReactRestore**)

| blue         |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:-------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore |     250 |      -28.06 |      13.96 |        -25.05 |             -1.64 |          0    |           0    |              2.25 |
| ReactRemove  |     250 |      -79.46 |      30.09 |        -72.7  |             -6.78 |          0.25 |           1.03 |              2.51 |
| Monitor      |     250 |     -105.33 |      39.5  |        -92.05 |            -10.35 |          0.56 |           2.88 |              2.25 |

### vs. Meander (best defender: **ReactRestore**)

| blue         |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:-------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore |     250 |      -25.58 |       9.85 |        -23.65 |             -1.64 |          0    |           0    |              5.88 |
| ReactRemove  |     250 |      -49.68 |      10.99 |        -50.3  |             -4    |          0    |           0    |              6.1  |
| Monitor      |     250 |      -54.01 |       9.75 |        -55.2  |             -4.31 |          0.01 |           0.02 |              5.92 |

Mean blue total by scenario:

|                             |      1 |     2 |     3 |      4 |     5 |
|:----------------------------|-------:|------:|------:|-------:|------:|
| ('B_line', 'Monitor')       | -133.9 | -88.8 | -77   | -155   | -72   |
| ('B_line', 'ReactRemove')   | -100.3 | -79.8 | -61.6 |  -95.5 | -60   |
| ('B_line', 'ReactRestore')  |  -27.6 | -32.5 | -25.7 |  -32.3 | -22.2 |
| ('Meander', 'Monitor')      |  -57.6 | -57.8 | -51.8 |  -63.1 | -39.7 |
| ('Meander', 'ReactRemove')  |  -51.4 | -53.7 | -46.9 |  -59.5 | -36.9 |
| ('Meander', 'ReactRestore') |  -24.8 | -26   | -27.7 |  -32.6 | -16.8 |

## confidentiality

### vs. B_line (best defender: **ReactRestore**)

| blue         |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:-------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore |     250 |      -27.21 |      13.18 |        -24.6  |             -1.46 |          0    |           0    |              2.28 |
| ReactBlock   |     250 |      -89.59 |      72.59 |        -71    |             -9.12 |          0.18 |           0.48 |              2.5  |
| ReactRemove  |     250 |      -90.97 |      77.82 |        -71    |             -9.43 |          0.18 |           0.52 |              2.5  |
| Monitor      |     250 |     -133.68 |     107.75 |        -92.85 |            -19.81 |          0.46 |           1.49 |              2.28 |

### vs. Meander (best defender: **ReactRestore**)

| blue         |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:-------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore |     250 |      -26.31 |       9.76 |        -25.15 |             -1.67 |          0    |           0    |              5.96 |
| ReactBlock   |     250 |      -48.87 |      11.46 |        -50.85 |             -3.96 |          0    |           0    |              6.26 |
| ReactRemove  |     250 |      -48.87 |      11.46 |        -50.85 |             -3.96 |          0    |           0    |              6.26 |
| Monitor      |     250 |      -53.85 |      11.92 |        -55.4  |             -4.44 |          0.02 |           0.03 |              6.03 |

Mean blue total by scenario:

|                             |      1 |     2 |     3 |      4 |     5 |
|:----------------------------|-------:|------:|------:|-------:|------:|
| ('B_line', 'Monitor')       | -173.8 | -88.1 | -84.3 | -251.6 | -70.6 |
| ('B_line', 'ReactBlock')    | -126.9 | -78.2 | -61.9 | -122.2 | -58.6 |
| ('B_line', 'ReactRemove')   | -135.2 | -78.2 | -61.9 | -120.9 | -58.6 |
| ('B_line', 'ReactRestore')  |  -26.3 | -29.6 | -25.2 |  -34.2 | -20.8 |
| ('Meander', 'Monitor')      |  -56.3 | -58.9 | -51.4 |  -64.6 | -38.1 |
| ('Meander', 'ReactBlock')   |  -49.2 | -53.4 | -47.2 |  -59.5 | -35   |
| ('Meander', 'ReactRemove')  |  -49.2 | -53.4 | -47.2 |  -59.5 | -35   |
| ('Meander', 'ReactRestore') |  -26.8 | -26   | -28.4 |  -32.1 | -18.3 |

## integrity

### vs. B_line (best defender: **ReactRestore**)

| blue                      |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:--------------------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore              |     250 |      -29.21 |      13.09 |           -27 |             -1.7  |          0    |           0    |              2.24 |
| ReactRemoveRestoreContent |     250 |      -78    |      29.29 |           -71 |             -6.23 |          0.16 |           0.39 |              2.48 |
| ReactRemove               |     250 |      -87.22 |      55.27 |           -71 |             -8.69 |          0.16 |           0.74 |              2.48 |
| Monitor                   |     250 |     -133.43 |      84.72 |           -98 |            -16.52 |          0.47 |           2.3  |              2.24 |

### vs. Meander (best defender: **ReactRestore**)

| blue                      |   games |   blue_mean |   blue_std |   blue_median |   final_step_mean |   impact_rate |   impacts_mean |   first_loss_mean |
|:--------------------------|--------:|------------:|-----------:|--------------:|------------------:|--------------:|---------------:|------------------:|
| ReactRestore              |     250 |      -25.5  |       9.23 |        -24.25 |             -1.54 |          0    |           0    |              5.93 |
| ReactRemove               |     250 |      -49.9  |      11.18 |        -51.15 |             -3.92 |          0    |           0    |              6.24 |
| ReactRemoveRestoreContent |     250 |      -49.9  |      11.18 |        -51.15 |             -3.92 |          0    |           0    |              6.24 |
| Monitor                   |     250 |      -54.54 |      10.16 |        -55.75 |             -4.68 |          0.02 |           0.02 |              6    |

Mean blue total by scenario:

|                                          |      1 |      2 |     3 |      4 |     5 |
|:-----------------------------------------|-------:|-------:|------:|-------:|------:|
| ('B_line', 'Monitor')                    | -181.8 | -100.6 | -80.5 | -232.7 | -71.6 |
| ('B_line', 'ReactRemove')                | -106.3 |  -82.4 | -60.2 | -126.2 | -60.9 |
| ('B_line', 'ReactRemoveRestoreContent')  |  -91   |  -82.4 | -59.4 |  -97.7 | -59.5 |
| ('B_line', 'ReactRestore')               |  -28.3 |  -32.8 | -28   |  -35.1 | -21.8 |
| ('Meander', 'Monitor')                   |  -57.6 |  -58.7 | -51.5 |  -65.2 | -39.8 |
| ('Meander', 'ReactRemove')               |  -51   |  -54   | -50.5 |  -58.6 | -35.4 |
| ('Meander', 'ReactRemoveRestoreContent') |  -51   |  -54   | -50.5 |  -58.6 | -35.4 |
| ('Meander', 'ReactRestore')              |  -22.3 |  -29.1 | -27.5 |  -31.3 | -17.3 |
