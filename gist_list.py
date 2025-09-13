from argparse import ArgumentParser
from json import loads
from os import environ
from pprint import pprint
from typing import Any, Generator
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

    def get_gists(self, url: str) -> list[dict[str, Any]]:
        """Make API call to Github API to retrieve Gists."""
        req = Request(url, headers=self.headers)
        with urlopen(req) as response:
            return loads(response.read().decode('utf-8'))

    def paginate_gists(self) -> Generator[list[dict]]:
        """Make API call to Github API to retrieve Gists."""
        index = 1
        resp = self.get_gists(f'{self.url}?page={index}&per_page=100')
        index += 1
        yield resp
        while resp:
            resp = self.get_gists(f'{self.url}?page={index}&per_page=100')
            index += 1
            yield resp

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

    def process_gists(self) -> Generator[dict[str, Any]]:
        for page in self.paginate_gists():
            for gist in page:
                yield self.parse_gist(gist)

    def get_gist_list(self):
        _ = [pprint(gist) for gist in self.process_gists()]

    def search_gists_txt(self, text: str):
        for gist in self.process_gists():
            gist = self.parse_gist(gist)
            val = text.lower()
            if val in gist['description'].lower() or val in gist['filename'].lower() \
                    or val in gist['language'].lower() or val in gist['type']:
                pprint(gist)

    def search_gists_ext(self, text: str):
        for gist in self.process_gists():
            gist = self.parse_gist(gist)
            if gist['description'].lower().endswith(text.lower()):
                pprint(gist)


if __name__ == "__main__":
    message = 'Usage: python3 gist_list.py -a | -t <search text> | -e <search extension>'
    message += '(select 1 option: -a|-t|-e)'
    parser = ArgumentParser(description=message)
    parser.add_argument(
        '-t', '--txt', help='Text to search for'
    )
    parser.add_argument(
        '-e', '--ext', help='File extension to search for'
    )
    parser.add_argument(
        '-a', '--all', action='store_true', help='Retrieve all gists'
    )

    args = parser.parse_args()
    try:
        client = GistList()
        if args.all:
            client.get_gist_list()
        elif args.txt:
            client.search_gists_txt(args.txt)
        elif args.ext:
            client.search_gists_ext(args.ext)
        else:
            parser.print_help()
            raise RuntimeError('No command line options provided.')
    except Exception as err:
        print(err)
        exit(1)
