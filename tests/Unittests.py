import os

import pytest
import requests
from click.testing import CliRunner

from ImageDownloader.ImageDownloader import download_image, read_file, main

WORKING_URL = 'https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg'
NOT_WORKING_URL = 'http://www.google.com/nocathere.jpg'
INVALID_URL = 'hello/nocathere.jpg'

URLS = [
    'https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg',
    'https://img.cutenesscdn.com/640/clsd/6/11/985e1d503ba94e07970bb4551c6e4f3e.jpg'
    'https://www.readersdigest.ca/wp-content/uploads/sites/14/2011/01/4-ways-cheer-up-depressed-cat.jpg',
    'https://www.rd.com/wp-content/uploads/2016/04/01-cat-wants-to-tell-you-laptop-760x506.jpg',
]


@pytest.fixture(scope='session')
def temp_path(tmpdir_factory):
    return tmpdir_factory.mktemp('images')


# region test download_image


def test_working_url(temp_path):
    url = WORKING_URL
    save_to = temp_path / 'working_url'
    save_to.mkdir()
    download_image(url, save_to)
    assert os.path.isfile(save_to / 'Cat03.jpg')


def test_not_working_url(temp_path):
    url = NOT_WORKING_URL
    save_to = temp_path / 'not_working_url'
    save_to.mkdir()
    with pytest.raises(requests.exceptions.RequestException):
        download_image(url, save_to)
    assert not os.path.isfile(save_to / 'nocathere.jpg')


def test_invalid_url(temp_path):
    url = INVALID_URL
    save_to = temp_path / 'not_invalid_url'
    save_to.mkdir()
    with pytest.raises(requests.exceptions.RequestException):
        download_image(url, save_to)
    assert not os.path.isfile(save_to / 'nocathere.jpg')


def test_invalid_save_to(temp_path):
    url = WORKING_URL
    save_to = temp_path / 'not_invalid_save_to'
    with pytest.raises(FileNotFoundError):
        download_image(url, save_to)
    assert not os.path.isfile(save_to / 'Cat03.jpg')


# endregion

# region test read_file


def test_valid_file(temp_path):
    path = temp_path / 'valid_file'
    path.mkdir()
    file = path / 'data.txt'
    file.write_text('\n'.join(URLS), encoding='utf-8')
    for l1, l2 in zip(read_file(file), URLS):
        assert l1 == l2


def test_empty_file(temp_path):
    path = temp_path / 'empty_file'
    path.mkdir()
    file = path / 'data.txt'
    with pytest.raises(StopIteration):
        next(read_file(file))


def test_wrong_format(temp_path):
    path = temp_path / 'wrong_format'
    path.mkdir()
    file = path / 'data.txt'
    content = 'asdfasfasdf.jpg asfasdfasdf\n\n      http://www.google.com/nocathere\n'
    expected = ['asdfasfasdf.jpg', 'http://www.google.com/nocathere']
    file.write_text(content, encoding='utf-8')
    for l1, l2 in zip(read_file(file), expected):
        assert l1 == l2


def test_file_not_found(temp_path, capsys):
    path = temp_path / 'file_not_found'
    file = path / 'data.txt'
    expected = f"Error: No such file or directory: {file}\n"
    with pytest.raises(StopIteration):
        next(read_file(file))
    captured = capsys.readouterr()
    assert expected == captured.out

# endregion


def test_main_with_args(temp_path):
    save_to = temp_path / 'main_with_args'
    save_to.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ['data.txt', '-v', '--save_to', save_to])
    assert result.exit_code == 0
    assert result.output == '''Success
Success
Success
404 Client Error: Not Found for url: http://www.google.com/nocathere
Invalid URL 'asdfasfasdf.jpg': No schema supplied. Perhaps you meant http://asdfasfasdf.jpg?
Success
Success
'''
    expected_images = 5
    actual_images = len([name for name in os.listdir(save_to) if os.path.isfile(save_to / name)])
    assert expected_images == actual_images


def test_main_without_args():
    cwd = os.getcwd()
    runner = CliRunner()
    result = runner.invoke(main, ['data.txt'])
    assert result.exit_code == 0
    expected_images = 5
    images = [name for name in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, name) and name.endswith('.jpg'))]
    assert expected_images == len(images)
    # clean up
    for i in images:
        os.remove(os.path.join(cwd, i))
