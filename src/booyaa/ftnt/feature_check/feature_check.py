import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from pathlib import Path

from deep_translator import GoogleTranslator
from datetime import datetime

def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


feature_url_pattern = re.compile(
    r"document/fortigate/\d+\.\d+\.\d+/new-features/(\w+)/(\d+-\d+-\d+)"
)

class NewFeatureParser:
    def __init__(self):
        self.target_version_list = []
        self.patch_url_df = None

        self.new_feature_df = pd.DataFrame()

        self.export_dir = Path('.')
        self.export_path = None

    def set_target(self, target_version_list):
        self.target_version_list = target_version_list

    def get_path_urls(self):
        tmp_result = []
        for target_version in self.target_version_list:
            url = f"https://docs.fortinet.com/document/fortigate/{target_version}/new-features"
            try:
                resp = requests.get(url, timeout=10)
                matches = feature_url_pattern.findall(resp.text)

                for doc_id, display_version in matches:
                    patch_version = display_version.replace('-', '.')
                    tmp_result.append({
                        "tareget_version": target_version,
                        "patch_version": patch_version,
                        "docid": doc_id,
                        "diplayversion": display_version,
                        "url": f"https://docs.fortinet.com/document/fortigate/{target_version}/new-features/{doc_id}/{display_version}"
                    })
            except Exception as e:
                print(f"Error fetching {url}: {e}")

        self.patch_url_df = pd.DataFrame(tmp_result).drop_duplicates(subset=["url"])
        # self.patch_url_df.to_csv("path_url.csv", index=False)

    def parse_feature_details_by_structure(self) -> pd.DataFrame:
        all_data = []

        for _, row in self.patch_url_df.iterrows():
            patch_version = row["patch_version"]
            url = row["url"]

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue

            content_div = soup.find("div", {"id": "mc-main-content"})
            if not content_div:
                continue

            h2_tags = content_div.find_all("h2")
            table_tags = content_div.find_all("table")

            for h2_tag, table in zip(h2_tags, table_tags):
                current_type = h2_tag.get_text(strip=True)

                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) != 2:
                        continue

                    category_tag = tds[0].find("p")
                    current_category = category_tag.get_text(strip=True) if category_tag else None

                    summary_td = tds[1]
                    li_tags = summary_td.find_all("li")
                    for li in li_tags:
                        a_tag = li.find("a", href=True)
                        if a_tag:
                            summary = a_tag.get_text(strip=True)
                            detail_link = a_tag["href"]
                            if detail_link.startswith("/"):
                                detail_link = "https://docs.fortinet.com" + detail_link

                            # 日本語訳追加
                            summary_ja = self.transrate(summary)
                            all_data.append({
                                "PatchVersion": patch_version,
                                "Type": current_type,
                                "Category": current_category,
                                "Summary": summary,
                                "SummaryJa": summary_ja,
                                "Detail Link": detail_link
                            })

        self.new_feature_df = pd.DataFrame(all_data)

    def transrate(self, text, source='en', target='ja'):
        translator = GoogleTranslator(source=source, target=target)
        try:
            translated_text = translator.translate(text)
        except Exception as e:
            print(e)
        return translated_text

    def export_csv(self, filename=None, export_dir=None):
        filename = filename or f'fos_new_{'_'.join(self.target_version_list)}_{timestamp()}.csv'
        export_dir = export_dir or self.export_dir

        export_dir.mkdir(exist_ok=True)

        self.export_path = Path(export_dir, filename)
        self.new_feature_df.to_csv(self.export_path, encoding='utf-8-sig')


if __name__ == '__main__':
    target_version_list = [
                '7.2.0',
                '7.4.0',
    ]

    fnf = NewFeatureParser()
    fnf.set_target(target_version_list)
    fnf.get_path_urls()
    fnf.parse_feature_details_by_structure()
    fnf.export_csv()

    print(fnf.new_feature_df)