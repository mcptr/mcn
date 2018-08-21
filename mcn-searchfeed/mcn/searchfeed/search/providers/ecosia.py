import bs4
from . import provider


class EcosiaHTML(provider.Provider):
    URL = "https://www.ecosia.org/search"

    def run_search(self, term, product):
        response = self.session.get(
            self.URL,
            params=dict(
                q=term,
            ),
            # headers=dict()
        )

        if response.status_code not in [200]:
            self.log.error(response)
            return None

        # self.log.debug(response)

        return self.parse(self.decode_content(response))

    def parse(self, text):
        results = []
        soup = bs4.BeautifulSoup(text, "lxml")
        items = soup.find_all("div", {"class": "result"})

        for item in items:
            url = item.find("a", {"class": "result-url"})
            if url and url.has_attr("href"):
                url = url.get("href")
            else:
                url = None

            title = item.find("a", {"class": "result-title"})
            title = title.text.strip() if title else None

            description = item.find("p", {"class": "result-snippet"})
            description = description.text.strip() if description else None

            if url:
                r = provider.Result(url, title, description)
                results.append(r)
        return results
