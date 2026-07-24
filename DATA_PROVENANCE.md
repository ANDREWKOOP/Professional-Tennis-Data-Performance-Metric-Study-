# Data Provenance

## Source

This project downloads Grand Slam point-level and match-level tennis data from the Jeff Sackmann archive mirror:

- Mirror: https://huggingface.co/datasets/Aneeshers/tennis-sackmann-archive
- Original upstream repository: https://github.com/JeffSackmann/tennis_slam_pointbypoint

The pipeline uses files from `slam_pointbypoint/` with names like:

- `YYYY-usopen-points.csv`
- `YYYY-usopen-matches.csv`
- `YYYY-wimbledon-points.csv`
- `YYYY-wimbledon-matches.csv`

By default, the script downloads singles Grand Slam data from 2017 through 2024.

## License

Jeff Sackmann's tennis datasets are licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.

Use this project for non-commercial academic and portfolio purposes. Attribute Jeff Sackmann / Tennis Abstract when sharing reports, charts, or derived outputs.

## Derived Data

The script writes derived files to `data/processed/`.

RAAVBSS is derived from body serves where:

- `ServeWidth` is `B`, `BC`, or `BW`
- serve speed is available and greater than zero
- point server and point winner are available

Return accuracy is proxied by the presence of a recorded `ReturnDepth` value of `D` or `ND`.

Return point win percentage is computed separately as `PointWinner != PointServer`.

