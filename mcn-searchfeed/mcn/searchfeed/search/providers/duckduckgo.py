import bs4
from . import provider


class DuckDuckGoHTML(provider.Provider):
    URL = "https://duckduckgo.com/html/"

    def run_search(self, term, product):
        response = self.session.post(
            self.URL,
            data=dict(
                q=term,
                b="",
                x="",
                ok="us-en",
            ),
            # headers=dict()
        )

        if response.status_code not in [200]:
            self.log.error(response.url)
            return None

        # self.log.debug(response)

        return self.parse(self.decode_content(response))

    def parse(self, text):
        results = []
        soup = bs4.BeautifulSoup(text, "lxml")
        results_div = soup.find(id="links")
        links = results_div.find_all("div", {"class": "result"})

        for l in links:
            title = l.find("a", {"class": "result__a"})
            url = l.find("a", {"class": "result__url"})
            description = l.find("a", {"class": "result__snippet"})
            if url and url.has_attr("href"):
                url = url.get("href")

            r = provider.Result(
                url.strip() if url else None,
                title.text.strip() if title else None,
                description.text.strip() if description else None,
            )
            results.append(r)
        return results
