"""
Given a plaintext file containing URLs (one per line) this script downloads the images the URLs are pointing
to the local harddrive.
"""
import os

import click
import requests


def download_image(url, save_to):
    """
    Attempts to download the image from the URL. On success the image is saved in save_to.
    If there is a problem the associated exception is raised.
    """
    name = url.split('/')[-1]
    response = requests.get(url)
    response.raise_for_status()
    if response.ok:
        with open(os.path.join(save_to, name), 'wb') as fout:
            fout.write(response.content)


def read_file(file):
    """
    Attempts to open the provided file and yields each line. If the file does not exist a
    FileNotFoundException is raised.
    """
    try:
        with open(file) as fin:
            for line in fin:
                line = line.strip('\n')
                if not line:
                    continue
                yield line.split()[0]  # ignore everything after a whitespace
    except FileNotFoundError:
        print(f'Error: No such file or directory: {file}')


@click.command()
@click.argument('file')
@click.option('--save_to', default=os.getcwd(), help='Where to save the images. Default is the current directory.')
@click.option('-v', '--verbose', is_flag=True, help='Output the result for each URL')
def main(**kwargs):
    """
    Given a plaintext file containing URLs (one per line) this script downloads the images the URLs are pointing
    to the local harddrive.
    """
    file = kwargs.get('file')
    save_to = kwargs.get('save_to')
    verbose = kwargs.get('verbose')
    for line in read_file(file):
        msg = 'Success'
        try:
            download_image(line, save_to)
        except requests.exceptions.RequestException as err:
            msg = err
        except FileNotFoundError as err:
            msg = err
        if verbose:
            print(msg)


if __name__ == '__main__':
    main()
