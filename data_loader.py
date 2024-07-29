from pathlib import Path

from trame.assets.remote import download_file_from_google_drive

data_dir = Path(__file__).parent / 'data'

star_nanoparticle_path = data_dir / 'Recon_NanoParticle_doi_10.1021-nl103400a.tiff'  # noqa
star_nanoparticle_google_drive_id = '1S821zdERFfJ-TlnMeyE0aTdBdV642OL4'

nanotube_path = data_dir / 'reconstructed_tiltser_180_subsampled_10.6084-m9.figshare.c.2185342.v2.tiff'  # noqa
nanotube_google_drive_id = '1bJi4yYis8yCh2A7yIpAzYjGUrqSV1us2'


def fetch_dataset(name: str) -> Path:
    if name == 'star_nanoparticle':
        path = star_nanoparticle_path
        drive_id = star_nanoparticle_google_drive_id
    else:
        path = nanotube_path
        drive_id = nanotube_google_drive_id

    # Make sure the data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print('Downloading dataset from Google Drive...')
        download_file_from_google_drive(drive_id, path)
    return path
