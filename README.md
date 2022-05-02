# 🐍📚 SnakePedia

SnakePedia is a collection of Vyper code that are useful for daily jobs
as a [Vyper](https://github.com/vyperlang/vyper) software engineer.

For example: ERC721Metadata.

In the future, there will be sample code like Ducth Auction, simple AMM,
timelock controller, etc.

## Dependencies

* [Python3](https://www.python.org/downloads/release/python-3910/) version 3.7 or greater, python3-dev
* [Vyper](https://github.com/vyperlang/vyper)
* [Brownie](https://github.com/eth-brownie/brownie)

## Installation

Just clone this project. Then create a virtual environment. Finally,
install the dependencies using pip.

```bash
git clone https://github.com/artpedia-io/SnakePedia
cd SnakePedia
python3.9 -m venv env
source env/bin/activate
pip install -r requirement.txt
```

You can take a look at the smart contract code at the `contracts` folder. Just take what you need. The test code is in the `tests` folder.

To compile the code:

```bash
brownie compile
```

To test the code:

```bash
brownie test
```

## Contributing

Help is always appreciated! Feel free to open an issue if you find a problem, or a pull request if you've solved an issue.

## License

This project is licensed under the [MIT license](LICENSE).
