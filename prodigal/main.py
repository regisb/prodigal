#! /usr/bin/env python
import argparse
from tools import generate, translate_templates, serve

def main():
    parser = argparse.ArgumentParser(description="Prodigal: Yet another static website generator!")

    subparsers = parser.add_subparsers(dest="command", help="")

    parser_generate = subparsers.add_parser("generate",
            help="Generate a static website")
    parser_generate.add_argument("src_path", metavar="SOURCE",
            help="Path of source files")
    parser_generate.add_argument("dst_path", metavar="DEST",
            help="Path of destination files")
    parser_generate.add_argument("-l", "--locale",
            help="Locale of the generated content")

    parser_translate = subparsers.add_parser("translate",
            help="Produce the translation files for the static website")
    parser_translate.add_argument("locale", metavar="LOCALE",
            help="Locale code for generated translation files. E.g: fr, en_US.")
    parser_translate.add_argument("src_path", metavar="SOURCE",
            help="Path of source files")

    parser_serve = subparsers.add_parser("serve",
            help="Run a web server to dynamically serve your source folder.")
    parser_serve.add_argument("-l", "--locale", metavar="LOCALE",
            help="Locale code for generated translation files. E.g: fr, en_US.")
    parser_serve.add_argument("-a", "--address", metavar="IPADDR:PORT", default="127.0.0.1:8000",
            help="IP address and port where the content should be served.")
    parser_serve.add_argument("src_path", metavar="SOURCE",
            help="Path of source files")
    args = parser.parse_args()

    if args.command == "generate":
        generate(args.src_path, args.dst_path, args.locale)
    elif args.command == "translate":
        translate_templates(args.locale, args.src_path)
    elif args.command == "serve":
        serve(args.src_path, args.locale, args.address)

if __name__ == "__main__":
    main()
