from iiif_prezi3 import Manifest, config, KeyValueString, load_bundled_extensions
import base64
import json
import httpx


class ManifestGenerator:
    def __init__(self, csv_row):
        self.csv_row = csv_row
        self.config = config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"
        self.rights = "http://rightsstatements.org/vocab/NKC/1.0/"
        self.manifest_url = self.__get_manifest_path()
        self.images = self.__get_base_64_images()
        self.metadata = self.__build_metadata()
        self.manifest = self.__build()

    def __get_manifest_path(self):
        return f"https://markpbaggett.github.io/static_iiif/manifests/service_maps_demo/{self.csv_row['Parent Identifier']}.json"

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

    def __build_metadata(self):
        metadata = []
        not_for_metadata = ('Title', 'Scanned', 'New Filenames')
        for k, v in self.csv_row.items():
            if k not in not_for_metadata and v != "":
                metadata.append(
                    KeyValueString(
                        label=k,
                        value={"en": [v]}
                    )
                )
        return metadata

    def __build(self):
        manifest = Manifest(
            id=self.manifest_url,
            label=self.csv_row['Title'] if self.csv_row['Title'] != "" else "Untitled",
            metadata=self.metadata,
            rights=self.rights,
        )
        i = 1
        for image in self.images:
            thumbnail = self.__get_thumbnail(image)
            manifest.make_canvas_from_iiif(
                url=image,
                thumbnail=thumbnail,
                label=f"Canvas {i}",
                id=f"{self.manifest_url.replace('.json', '')}/canvas/{i}",
                anno_id=f"{self.manifest_url.replace('.json', '')}/canvas/{i}/annotation/{i}",
                anno_page_id=f"{self.manifest_url.replace('.json', '')}/canvas/{i}/annotation/{i}/page/{i}",
            )
            i += 1
        x = manifest.json(indent=2)
        manifest_as_json = json.loads(x)
        return manifest_as_json

    @staticmethod
    def __get_thumbnail(url):
        image_response = httpx.get(f"{url}/info.json", timeout=60).json()
        size = image_response['sizes'][4]
        return {
          "id": f"{url}/full/{size['width']},/0/default.jpg",
          "width": size['width'],
          "height": size['height'],
          "type": "Image",
          "format": "image/jpeg",
          "service": [
            {
              "@id": url,
              "@type": "http://iiif.io/api/image/2/context.json",
              "profile": "http://iiif.io/api/image/2/level2.json"
            }
          ]
        }

    def write(self, path):
        with open(f'{path}/{self.csv_row["Parent Identifier"]}.json', 'w') as outfile:
            outfile.write(
                json.dumps(
                    self.manifest, indent=2)
            )