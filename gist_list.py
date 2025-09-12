from argparse import ArgumentParser
from json import loads
from os import environ
from pprint import pprint
from urllib.request import Request, urlopen


class GistList:
    """List all or a selection of Gist details."""

    def __init__(self):
        self.url = 'https://api.github.com/gists'
        if not environ.get('GIST_TOK', None):
            raise KeyError('Missing required Environment Variable "GIST_TOK"')
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'Authorization': f'Bearer {environ['GIST_TOK']}'
        }

    def get_gists(self):
        req = Request(self.url, headers=self.headers)
        with urlopen(req) as response:
            return loads(response.read().decode('utf-8'))

    def get_gist_list(self):
        for gist in self.get_gists():
            _, file_details = gist['files'].popitem()
            print(file_details['filename'])
            print(file_details['language'])
            print(file_details['type'])
        return self.get_gists()


if __name__ == "__main__":
    message = 'Usage: python3 gist_list.py -a | -t <search text> | -e <search extension>'
    parser = ArgumentParser(description=message)
    parser.add_argument(
        '-t', '--txt', help='Text to search for'
    )
    parser.add_argument(
        '-e', '--ext', help='File extension to search for'
    )
    parser.add_argument(
        '-a', '--all', action='store_true', help='Github Username'
    )

    args = parser.parse_args()
    try:
        client = GistList()
        if args.txt:
            pass
        elif args.ext:
            pass
        elif args.all:
            pprint(client.get_gist_list())
        else:
            parser.print_help()
            raise RuntimeError('No command line options provided.')
    except Exception as err:
        print(err)
        exit(1)
