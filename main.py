from argparse import ArgumentParser

from converter.converter import Converter
from mp4_worker.writer import Writer


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("filename", help="Filename to convert")
    args = parser.parse_args()

    document = Converter.convert(args.filename, True)
    print(document.date)

    writer = Writer(document.shots[0])
    writer.run()
