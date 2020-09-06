# Arceus

The best (probably) free Minecraft name sniper.

## IMPORTANT - LICENSE TERMS

The arceus project is licensed under GNU GPLv3 or later. This means you CANNOT redistribute modifications to the project except under GNU GLPv3. In other words, any modifications you make must also be open source.

## Features

- Transfer and blocking sniper
- Benchmark to test settings
- Low latency by opening the TCP connections before sending requests
- High requests/second by bypassing HTTP overhead

## Installation

You can install using pip:

```sh
pip install arceus
```

## Discussion and Support

Join the [Discord Server](https://discord.gg/nhZDSEM) for support, feature suggestions, bug reports, usage help, and general discussion.

## Usage

First, you'll need to create a `config.json`:

```jsonc
{
  "account": {
    "email": <ACCOUNT_EMAIL>,
    "password": <ACCOUNT_PASSWD>
  },
  "offset": <REQUEST_OFFSET>
}
```

CLI Options:

| Name         | Short |         Description |
| :----------- | :---: | ------------------: |
| `--target`   | `-t`  |       Name to snipe |
| `--config`   | `-c`  |  Config file to use |
| `--attempts` | `-a`  |    Request attempts |
| `--later`    | `-l`  | Days later to snipe |

Transfer Snipe:

```sh
arceus transfer
```

Block Snipe:

```sh
arceus block
```

## Benchmarking

CLI Options:

| Name         | Short |                  Description |
| :----------- | :---: | ---------------------------: |
| `--host`     | `-h`  |         Benchmark API to use |
| `--offset`   | `-o`  |        Request timing offset |
| `--attempts` | `-a`  |             Request attempts |
| `--delay`    | `-d`  | Seconds before the benchmark |

_Benchmarking doesn't read `config.json`, if you want to specify an offset, use the `--offset` option_

```sh
arceus benchmark
```

## Contributing

Feel free to fork the project and make a pull request on GitHub.
