"""
Scraper de reviews do IMDB via API GraphQL.

Uso:
    python scraper_imdb.py <url_do_filme> [arquivo_saida.csv]

Exemplos:
    python scraper_imdb.py https://www.imdb.com/title/tt27847051/reviews/
    python scraper_imdb.py https://www.imdb.com/pt/title/tt27847051/reviews/ reviews_tt27847051.csv
    python scraper_imdb.py tt27847051
"""

import sys
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

GRAPHQL_URL = "https://api.graphql.imdb.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}

QUERY = """
query Reviews($titleId: ID!, $after: ID, $first: Int!) {
  title(id: $titleId) {
    titleText { text }
    reviews(after: $after, first: $first, sort: {by: SUBMISSION_DATE, order: DESC}) {
      edges {
        node {
          author { nickName }
          summary { originalText }
          text { originalText { plaidHtml } }
          authorRating
          submissionDate
        }
      }
      pageInfo { hasNextPage endCursor }
      total
    }
  }
}
"""


def extract_title_id(input_str: str) -> str:
    """Extrai o title ID (ttXXXXXXX) de uma URL ou string direta."""
    match = re.search(r"(tt\d+)", input_str)
    if match:
        return match.group(1)
    raise ValueError(f"Não foi possível extrair o title ID de: {input_str}")


def scrape_reviews(title_id: str, batch_size: int = 50) -> pd.DataFrame:
    """Coleta todas as reviews de um filme via API GraphQL do IMDB."""
    all_reviews = []
    cursor = None
    page = 0
    title_name = None

    while True:
        page += 1
        variables = {"titleId": title_id, "first": batch_size}
        if cursor:
            variables["after"] = cursor

        resp = requests.post(
            GRAPHQL_URL, json={"query": QUERY, "variables": variables}, headers=HEADERS
        )

        if resp.status_code != 200:
            print(f"Erro HTTP {resp.status_code}: {resp.text[:300]}")
            break

        data = resp.json()
        if "errors" in data:
            print(f"Erro GraphQL: {data['errors'][0]['message']}")
            break

        title_data = data["data"]["title"]
        if title_name is None:
            title_name = (title_data.get("titleText") or {}).get("text", title_id)
            print(f"Filme: {title_name}")

        reviews_data = title_data["reviews"]
        edges = reviews_data["edges"]
        total = reviews_data["total"]

        for edge in edges:
            n = edge["node"]
            rating = n.get("authorRating")
            title = (n.get("summary") or {}).get("originalText", "")
            raw_html = ((n.get("text") or {}).get("originalText") or {}).get(
                "plaidHtml", ""
            )
            text = (
                BeautifulSoup(raw_html, "lxml").get_text(strip=True) if raw_html else ""
            )

            all_reviews.append(
                {
                    "rating": rating,
                    "title": title,
                    "text": text,
                    "date": n.get("submissionDate"),
                    "author": (n.get("author") or {}).get("nickName", ""),
                }
            )

        print(f"  Página {page}: {len(edges)} reviews (total: {len(all_reviews)}/{total})")

        if not reviews_data["pageInfo"]["hasNextPage"]:
            break
        cursor = reviews_data["pageInfo"]["endCursor"]
        time.sleep(0.5)

    df = pd.DataFrame(all_reviews)
    print(f"\nTotal coletado: {len(df)} reviews")
    if "rating" in df.columns:
        print(f"Com rating: {df['rating'].notna().sum()}")
        print(f"Sem rating: {df['rating'].isna().sum()}")
    return df


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_str = sys.argv[1]
    title_id = extract_title_id(input_str)
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"reviews_{title_id}.csv"

    print(f"Title ID: {title_id}")
    print(f"Arquivo de saída: {output_file}\n")

    df = scrape_reviews(title_id)

    if not df.empty:
        df.to_csv(output_file, index=False)
        print(f"\nSalvo em: {output_file}")
        print(f"\nDistribuição das notas:")
        print(df["rating"].value_counts().sort_index())
    else:
        print("Nenhuma review encontrada.")


if __name__ == "__main__":
    main()
