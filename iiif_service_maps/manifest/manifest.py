from iiif_prezi3 import Manifest, config, KeyValueString, load_bundled_extensions
import base64


class ManifestGenerator:
    def __init__(self, csv_row):
        self.csv_row = csv_row
        self.images = self.__get_base_64_images()

    def __get_base_64_images(self):
        all_images = []
        filenames = self.csv_row['New Filenames'].split('||')
        work_id = int(self.csv_row['Parent Identifier'].split('_')[-1]) + 1
        i = 0
        for filename in filenames:
            url = f"https://api-pre.library.tamu.edu/fcrepo/rest/batch-service-maps-tests_objects/{work_id}/pages/page_{i}/files/{filename}"
            url_encoded_file = base64.urlsafe_b64encode(bytes(url, 'utf-8')).decode('utf-8')
            all_images.append(f"https://api-pre.library.tamu.edu/iiif/2/{url_encoded_file}")
            i += 1
        return all_images
