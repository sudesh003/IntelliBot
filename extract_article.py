import newspaper

def extract_article(url):
    try:
        obj = newspaper.Article(url)
        obj.download()
        obj.parse()

        if obj.is_valid_body():
            return obj.text
        else:
            return "Article not detected."
    except Exception as e:
        output += f"Error processing {url}: {str(e)}\n"
        return f"Error processing {url}: {str(e)}"

# # Example usage:
# url_to_extract = 'https://refactoring.guru/design-patterns/factory-method'
# article_content = extract_article(url_to_extract)

