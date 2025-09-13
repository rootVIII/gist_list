from argparse import ArgumentParser
from json import loads
from os import environ
from pprint import pprint
from typing import Any
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

    def get_gists(self) -> list[dict[str, Any]]:
        """Make API call to Github API to retrieve Gists."""
        req = Request(self.url, headers=self.headers)
        with urlopen(req) as response:
            return loads(response.read().decode('utf-8'))

    def parse_gist(self, gist: dict[str, Any]) -> dict[str, Any]:
        """Extract the required keys/values from a given gist dictionary."""
        _, file_details = gist['files'].popitem()
        return {
            'filename': file_details['filename'],
            'language': str(file_details['language']),
            'description': gist['description'],
            'type': file_details['type'],
            'public': gist['public'],
            'url': gist['html_url']
        }

    def get_gist_list(self) -> list[dict]:
        return [self.parse_gist(gist) for gist in self.get_gists()]

    def search_gists_txt(self, text: str) -> list[dict]:
        matches = []
        for gist in self.get_gists():
            gist = self.parse_gist(gist)
            if text.lower() in gist['description'].lower() \
                    or text.lower() in gist['filename'].lower() \
                    or text.lower() in gist['language'].lower():
                matches.append(gist)
        return matches

    def search_gists_ext(self, text: str) -> list[dict]:
        matches = []
        for gist in self.get_gists():
            gist = self.parse_gist(gist)
            if gist['description'].lower().endswith(text.lower()):
                matches.append(gist)
        return matches


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
        if args.all:
            pprint(client.get_gist_list())
        elif args.txt:
            pprint(client.search_gists_txt(args.txt))
        elif args.ext:
            pprint(client.search_gists_ext(args.ext))
        else:
            parser.print_help()
            raise RuntimeError('No command line options provided.')
    except Exception as err:
        print(err)
        exit(1)
