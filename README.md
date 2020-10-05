![Arceus's logo](./banner.png)

[![Discord](https://img.shields.io/discord/761790519646617632?label=discord&style=for-the-badge)](https://discord.gg/gxwedaE)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/arceus?style=for-the-badge)](https://pypi.org/project/arceus/)
![License](https://img.shields.io/github/license/aquild/arceus?style=for-the-badge)

# Arceus

The best (probably) free Minecraft name sniper.

## IMPORTANT - LICENSE TERMS

The Arceus project is licensed under GNU GPLv3 or later. This means you CANNOT redistribute modifications to the project except under GNU GLPv3. In other words, any modifications you make must also be open source.

## Features

- Transfer and blocking sniper
- Benchmark to test settings
- Low latency by opening the TCP connections before sending requests
- High requests/second by bypassing HTTP overhead

## Discussion and Support

Join the [Discord Server](https://discord.gg/gxwedaE) for support, feature suggestions, usage help, and general discussion.

## Installation

You can read the installation instructions [here](./INSTALLATION.md).

## Usage

First, you'll need to create a `config.json`:

**IMPORTANT**: If you don't know JSON syntax, please read [this tutorial](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON) and make sure your JSON is valid _before_ asking for help.

```jsonc
{
  "accounts": [
    {
      "email": <ACCOUNT_EMAIL>,
      "password": <ACCOUNT_PASSWD>
    }
    ...
  ],
  "offset": <REQUEST_OFFSET>,
  "attempts": <REQUEST_ATTEMPTS>
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
