import bs4
from . import provider


class BingHTML(provider.Provider):
    URL = "https://www.bing.com/search"

    def run_search(self, term, product):
        response = self.session.get(
            self.URL,
            params=dict(
                q=term,
            ),
        )

        if response.status_code not in [200]:
            self.log.error(response)
            self.log.error(response.text)
            return None

        # self.log.debug(response)

        return self.parse(self.decode_content(response))

    def parse(self, text):
        results = []
        soup = bs4.BeautifulSoup(text, "lxml")
        results_elem = soup.find(id="b_results")
        items = results_elem.find_all("li", {"class": "b_algo"})

        for item in items:
            header = item.find("div", {"class": "b_algoheader"})
            if not header:
                continue
            url = header.find("a")

            if url and url.has_attr("href"):
                url = url.get("href")
            else:
                url = None

            h2 = header.find("h2")
            title = h2.find_all("a")[-1]

            title = title.text.strip() if title else None

            description = item.find("div", {"class": "b_caption"})
            if description:
                description = description.find("p")
                description = description.text.strip() if description else None
            else:
                description = None

            r = provider.Result(url, title, description)
            results.append(r)

        return results
