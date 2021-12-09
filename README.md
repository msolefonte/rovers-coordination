[![Maintainability](https://api.codeclimate.com/v1/badges/e717b12097cdcc46d248/maintainability)](https://codeclimate.com/github/msolefonte/rovers-coordination/maintainability)
[![License](https://img.shields.io/github/license/msolefonte/rovers-coordination)](https://github.com/msolefonte/rovers-coordination/blob/master/LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/msolefonte/rovers-coordination/blob/master/CONTRIBUTING.md)

# Rovers Coordination Project

Wireless coordination algorithms applied to Mars rovers.

## About the project

The objective of this project is to design, implement and
build a peer-to-peer networking protocol applied to Mars
rovers. In order to do so, a Software Defined Network is
utilized in order to simulate the wireless environment,
unreliable and with constant topology changes.

Apart from the core, a list of components have been added
in order to simulate a sufficiently realistic environment.
This includes but is not limited to radios, antennas,
engines, batteries and sensors, all of them with automated
failures associated in order to evaluate the algorithm
fault-tolerance capacities.

## Usage

**Start*
```bash
./scripts/start.sh
```

**Stop**
```bash
./scripts/stop.sh
```

## Contributing

Contributions are welcome. See
[CONTRIBUTING](https://github.com/msolefonte/rovers-coordination/blob/master/CONTRIBUTING.md) for more information.

## Versioning

[SemVer](http://semver.org/) is used for versioning. For the changelog, see [CHANGELOG.md](CHANGELOG.md).

## Authors

* **Marc Solé Fonte** - *Initial work* - [msolefonte](https://github.com/msolefonte)
* **Berkan Ozdamar** - *Initial work* - [ozdamarberkan](https://github.com/ozdamarberkan)
* **Swagat Dash** - *Initial work* - [swagatdash95](https://github.com/swagatdash95)
* **Manu Prasannakumar** - *Initial work* - [manupmanoos](https://github.com/manupmanoos)

## License

Distributed under the GPL-3.0 License. See
[LICENSE](https://github.com/msolefonte/rovers-coordination/blob/master/LICENSE) for more information.
