import click
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def get_html_of(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f'HTTP status code of {resp.status_code} returned for {url}')
            return None
        return resp.content.decode()
    except Exception as e:
        print(f'Error fetching {url}: {e}')
        return None

def count_occurences_in(word_list, min_length):
    word_count = {}
    for word in word_list:
        if len(word) < min_length:
            continue
        if word not in word_count:
            word_count[word] = 1
        else:
            current_count = word_count.get(word)
            word_count[word] = current_count + 1
    return word_count

def get_all_words_from(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return re.findall(r'\w+', raw_text)

def get_urls_from(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for link in soup.find_all('a', href=True):
        url = urljoin(base_url, link['href'])
        urls.add(url)
    return urls

def is_same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc

def crawl_pages(start_url, depth):
    visited = set()
    to_visit = [(start_url, 0)]
    all_words = []
    base_domain = urlparse(start_url).netloc
    
    while to_visit:
        current_url, current_depth = to_visit.pop(0)
        
        if current_url in visited or current_depth > depth:
            continue
            
        print(f'Crawling: {current_url} (depth: {current_depth})')
        visited.add(current_url)
        
        html = get_html_of(current_url)
        if not html:
            continue
            
        # Extract words
        words = get_all_words_from(html)
        all_words.extend(words)
        
        # Extract URLs for next depth level
        if current_depth < depth:
            urls = get_urls_from(html, current_url)
            for url in urls:
                if url not in visited and is_same_domain(url, start_url):
                    to_visit.append((url, current_depth + 1))
    
    return all_words

def get_top_words_from(all_words, min_length):
    occurences = count_occurences_in(all_words, min_length)
    return sorted(occurences.items(), key=lambda item: item[1], reverse=True)

def generate_password_mutations(word):
    mutations = [
        word.lower(),
        word.upper(),
        word.capitalize(),
        word.title(),
    ]
    
    # Add variations with years
    for year in ['2019', '2020', '2021', '2022', '2023', '2024', '2025']:
        mutations.append(f"{word}{year}")
        mutations.append(f"{word.capitalize()}{year}")
    
    # Add variations with numbers
    for num in ['1', '12', '123', '1234', '01', '001']:
        mutations.append(f"{word}{num}")
        mutations.append(f"{word.capitalize()}{num}")
    
    # Add variations with symbols
    for symbol in ['!', '!!', '!1', '1!', '2!', '3!', '@', '#', '$']:
        mutations.append(f"{word}{symbol}")
        mutations.append(f"{word.capitalize()}{symbol}")
    
    # Combined: capitalized word + year + symbol
    for year in ['2019', '2020', '2021', '2022', '2023', '2024', '2025']:
        for symbol in ['!', '@', '#']:
            mutations.append(f"{word.capitalize()}{year}{symbol}")
    
    return list(set(mutations))  # Remove duplicates

@click.command()
@click.option('--url', '-u', prompt='Web URL', help='URL of webpage to extract from.')
@click.option('--length', '-l', type=int, default=0, help='Minimum word length (default: 0, no limit).')
@click.option('--output', '-o', type=click.Path(), default=None, help='Output file path (default: print to console).')
@click.option('--depth', '-d', type=int, default=0, help='Crawl depth (default: 0, single page only).')
@click.option('--mutations/--no-mutations', '-m', default=False, help='Generate password mutations (default: no).')
def main(url, length, output, depth, mutations):
    print(f"\nStarting crawl from {url} (depth: {depth}, min length: {length})\n")
    
    # Crawl pages
    the_words = crawl_pages(url, depth)
    
    if not the_words:
        print("No words found!")
        return
    
    top_words = get_top_words_from(the_words, length)
    
    if not top_words:
        print(f"No words found with minimum length {length}")
        return
    
    # Prepare output
    lines = []
    lines.append(f"Top words from {url} (minimum length: {length}):\n")
    lines.append("=" * 60 + "\n\n")
    
    for word, count in top_words[:50]:  # Show top 50
        lines.append(f"{word}: {count}\n")
    
    # Add password mutations if requested
    if mutations:
        lines.append("\n" + "=" * 60 + "\n")
        lines.append("PASSWORD MUTATIONS (Top 20 words):\n")
        lines.append("=" * 60 + "\n\n")
        
        for word, count in top_words[:20]:
            lines.append(f"\nMutations for '{word}':\n")
            word_mutations = generate_password_mutations(word)
            for mutation in word_mutations[:30]:  # Limit mutations per word
                lines.append(f"  {mutation}\n")
    
    # Output to file or console
    if output:
        with open(output, 'w', encoding='utf-8') as wr:
            wr.writelines(lines)
        print(f"\nResults written to {output}")
    else:
        for line in lines:
            print(line, end='')

if __name__ == '__main__':
    main()