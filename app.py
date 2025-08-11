# app.py

import os
import streamlit as st
from newspaper import Article
from collections import Counter
import textstat, requests, re, openai, json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import streamlit.components.v1 as components
import markdown as md

import json

with open("technical_links.json") as f:
    keyword_map = json.load(f)

sorted_keywords = sorted(keyword_map.keys(), key=len, reverse=True)

from company_config import (
    openai_api_key, company_name, core_tech, value_props, positioning,
    google_api_key, google_cx
)

openai.api_key = openai_api_key

STOPWORDS = set("the and that with this from have which will would there their what when where while about these those been because could into upon some other than then they them were such only also very many more most over your ours ourselves hers herself his himself yourself yourselves does did had has was are not for but you its our can may might shall should must been who whom how why each few both same once".split())

# -------------------- FONT STYLING --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# -------------------- HELPERS --------------------
def call_openai(prompt):
    res = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a concise, insightful summarizer and formatter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return res.choices[0].message.content.strip()

# -------------------- HELPERS --------------------

def extract_section_from_template(section_header, filepath="blog_prompt_template.txt"):
    """
    Reads the template file and returns all lines after `section_header`
    up to the next line starting with '###' (or EOF).
    """
    tpl = load_prompt_template(filepath)
    lines = tpl.splitlines()
    collecting = False
    section_lines = []
    for line in lines:
        if collecting:
            if line.startswith("###") and line.strip() != section_header:
                break
            section_lines.append(line)
        elif line.strip() == section_header:
            collecting = True
    return "\n".join(section_lines).strip()

import re

def hyperlink_keywords(text: str, mapping: dict) -> str:
    """
    Wrap any occurrence of each keyword in text with a markdown link
    to the first URL in its list.
    """
    for kw in sorted_keywords:
        url = mapping[kw][0]  # or pick random.choice(mapping[kw])
        # \b for word boundaries, re.IGNORECASE for case-insensitive
        pattern = re.compile(rf"\b{re.escape(kw)}\b", flags=re.IGNORECASE)
        text = pattern.sub(lambda m: f"[{m.group(0)}]({url})", text)
    return text

def markdown_to_html(markdown_text):
    return md.markdown(markdown_text)

def google_search_urls(query, num=5):
    try:
        params = {"q": query, "cx": google_cx, "key": google_api_key, "num": num}
        res = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=8)
        res.raise_for_status()
        return [item["link"] for item in res.json().get("items", [])]
    except:
        return []

def scrape_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/110.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        article = Article(url)
        article.set_html(response.text)
        article.parse()

        if len(article.text.strip()) < 100:
            st.warning(f"Article parsed but too short: {url}")
            return None
        return article.text

    except Exception:
        return None

def scrape_html(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        return BeautifulSoup(r.text, "html.parser")
    except:
        return None

def extract_keywords(text):
    words = re.findall(r"\w+", text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 4]
    return Counter(filtered).most_common(10)

def keyword_share(counter):
    total = sum(counter.values())
    return [(kw, f"{(cnt/total)*100:.1f}%") for kw, cnt in counter.most_common(10)] if total else []

def compute_tfidf_keywords(texts):
    if not texts:
        return []
    vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
    X = vectorizer.fit_transform(texts)
    sums = X.sum(axis=0).A1
    return sorted(
        [(word, sums[idx]) for word, idx in vectorizer.vocabulary_.items()],
        key=lambda x: x[1], reverse=True
    )[:10]

def detect_snippet_format(soup):
    if soup is None:
        return "unknown"
    if soup.find_all('div', class_='related-question-pair'):
        return "faq"
    if soup.find('ol') or soup.find('ul'):
        return "list"
    if soup.find('table'):
        return "table"
    return "paragraph"

def verify_urls(urls):
    verified = []
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                verified.append(url)
        except:
            continue
    return verified

def load_prompt_template(filepath="blog_prompt_template.txt"):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except:
        return ""

def load_tagged_technical_pool(filepath="technical_links.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

def match_links_to_keywords(tagged_pool, keywords):
    matches = []
    for kw in keywords:
        for topic, links in tagged_pool.items():
            if topic.lower() in kw.lower():
                matches.extend(links)
    return list(set(matches))

def build_prompt(avg_read, kw_guidance, tfidf_keywords, user_additional_info, format_summary,
                 news_links, authority_links, solution_links):
    template = load_prompt_template()
    kw_lines = "\n".join([f"- {kw}: {share}" for kw, share in kw_guidance])
    tfidf_lines = "\n".join([f"- {kw} (priority keyword)" for kw, _ in tfidf_keywords])
    core_tech_lines = "\n".join([f"- {ct}" for ct in core_tech])
    value_props_lines = "\n".join([f"- {vp}" for vp in value_props])
    positioning_lines = "\n".join([f"- {pos}" for pos in positioning])

    return template.format(
        kw_lines=kw_lines,
        tfidf_lines=tfidf_lines,
        core_tech_lines=core_tech_lines,
        value_props_lines=value_props_lines,
        positioning_lines=positioning_lines,
        user_additional_info=user_additional_info,
        format_summary=format_summary,
        news_links=", ".join([f"[{url}]({url})" for url in news_links]),
        authority_links=", ".join([f"[{url}]({url})" for url in authority_links]),
        solution_links=", ".join([f"[{url}]({url})" for url in solution_links]),
        avg_read=avg_read
    )

def copy_to_clipboard_component(blog_html):
    components.html(f"""
        <button onclick="copyRichBlog()" style="padding:8px 16px; font-size:16px; border-radius:5px;">Copy Formatted Blog</button>
        <script>
        function copyRichBlog() {{
            const htmlContent = `{blog_html.replace("`", "\\`").replace("\\", "\\\\")}`;
            const type = "text/html";
            const blob = new Blob([htmlContent], {{ type }});
            const data = [new ClipboardItem({{ [type]: blob }})];

            navigator.clipboard.write(data).then(function() {{
                alert("Formatted blog copied to clipboard!");
            }}, function(err) {{
                alert("Copy failed: " + err);
            }});
        }}
        </script>
    """, height=60)

# -------------------- BLOG GENERATOR --------------------
def analyze_and_generate(comp_urls, tech_urls, user_additional_info, topic=None):
    read_scores, article_texts, kw_counter, formats = [], [], Counter(), []

    for url in comp_urls:
        txt = scrape_article_text(url)
        soup = scrape_html(url)
        if txt:
            article_texts.append(txt)
            read_scores.append(textstat.flesch_reading_ease(txt))
            kw_counter.update(dict(extract_keywords(txt)))
        if soup:
            formats.append(detect_snippet_format(soup))

    for url in tech_urls:
        txt = scrape_article_text(url)
        if txt:
            article_texts.append(txt)
            kw_counter.update(dict(extract_keywords(txt)))

    if not read_scores:
        st.warning("No readable competitor content scraped.")
        return

    avg_read = sum(read_scores) / len(read_scores)
    kw_guidance = keyword_share(kw_counter)
    tfidf_keywords = compute_tfidf_keywords(article_texts)
    format_summary = ", ".join(formats) if formats else "unknown"
    news_links = comp_urls[:5]

    tagged_pool = load_tagged_technical_pool()
    all_keywords = [kw for kw, _ in kw_guidance] + [kw for kw, _ in tfidf_keywords]
    authority_links = verify_urls(match_links_to_keywords(tagged_pool, all_keywords))[:10]
    # Fr0ntierX-links logic removed:
    solution_links = authority_links[:3]

    prompt = build_prompt(avg_read, kw_guidance, tfidf_keywords, user_additional_info,
                          format_summary, news_links, authority_links, solution_links)

    # … after you’ve built your prompt …
    raw_blog = call_openai(prompt)

    # ←── Add these three lines here ──→
    blog_markdown = hyperlink_keywords(raw_blog, keyword_map)
    st.subheader("Your Optimized Blog")
    st.write(blog_markdown, unsafe_allow_html=True)

    blog_html = markdown_to_html(blog_markdown)
    copy_to_clipboard_component(blog_html)

# -------------------- Short blog generator --------------------
def extract_compelling_quote(text):
    return call_openai(f"Extract the most striking sentence from:\n\n{text[:2000]}")

def summarize_text(text):
    return call_openai(f"Summarize this in 1–2 sentences:\n\n{text[:2000]}")

def map_to_fr0ntierx_value_prop(text):
    kws = {
        "zero trust": "Polaris isolates threats even from authenticated users.",
        "supply chain": "Polaris validates binaries and environments at runtime.",
        "confidential computing": "Fr0ntierX ensures data stays encrypted even in use."
    }
    for k,v in kws.items():
        if k in text.lower():
            return v
    return "Fr0ntierX secures critical workloads from advanced threats."

def format_social_post(quote, summary, insight, url):
    return (
        f"🧠 “{quote.strip()}”\n\n"
        f"🔍 Summary: {summary.strip()}\n\n"
        f"🧩 Fr0ntierX Insight: {insight}\n\n"
        f"🔗 Source: [{url}]({url})"
    )

# -------------------- STREAMLIT UI --------------------

mode = st.radio(
    "Choose mode:",
    ["Long Blog Generator", "Short Blog Generator"],
    key="mode_selector"
)

if mode == "Long Blog Generator":
    st.title(f"{company_name} BlogBuddy")
    sub_mode = st.radio(
        "Choose input mode:",
        ["Automatic (Google search + optional URLs)", "Manual (only manual URLs)"],
        key="long_input_mode"
    )
    # Topic box (only for Automatic)
    topic = (
        st.text_input("Input the topic you'd like to write about:", key="long_topic")
        if "Auto" in sub_mode
        else None
    )

    # Competitor URLs
    manual_urls_box = st.text_area(
        "Add competitor URLs (one per line):",
        height=100,
        key="long_urls"
    )
    # Technical URLs
    tech_box = st.text_area(
        "Optional: technical article URLs (one per line):",
        height=80,
        key="long_tech_urls"
    )
    # Extra instructions
    extra_info = st.text_area(
        "Optional: Add any additional information you'd like represented in the blog.",
        height=80,
        key="long_extra_info"
    )

    # Generate button for long blogs
    if st.button("Generate Blog", key="generate_long"):
        manual_urls = [u.strip() for u in manual_urls_box.splitlines() if u.strip()]
        tech_urls   = [u.strip() for u in tech_box.splitlines()   if u.strip()]
        comp_urls   = (google_search_urls(topic) + manual_urls) if ("Auto" in sub_mode and topic) else manual_urls

        if not comp_urls:
            st.warning("No competitor URLs to analyze.")
        else:
            analyze_and_generate(comp_urls, tech_urls, extra_info.strip(), topic)


elif mode == "Short Blog Generator":
    st.title(f"{company_name} Short Blog Generator")

    # ────── session‐state initialization ──────
    if "scrape_failed" not in st.session_state:
        st.session_state.scrape_failed = False
    if "article_text" not in st.session_state:
        st.session_state.article_text = ""

    # Step 1: URL input & scrape
    url = st.text_input("Paste the article URL here:", key="short_url")
    if st.button("Try Scraping Article", key="try_scrape"):
        txt = scrape_article_text(url)
        if txt:
            st.session_state.scrape_failed = False
            st.session_state.article_text = txt
        else:
            st.session_state.scrape_failed = True
            st.session_state.article_text = ""

    # Step 2: Manual fallback
    if st.session_state.scrape_failed:
        st.warning("⚠️ Website couldn’t be scraped. Please paste the text below:")
        st.markdown(f"[🔗 Open in browser]({url})", unsafe_allow_html=True)
        manual = st.text_area("Paste article text here:", height=300, key="short_manual_text")
        if manual:
            st.session_state.article_text = manual

    # ────── Step 3: Summarize & Link button ──────
    if st.session_state.article_text:
        if st.button("Summarize & Link", key="summarize_short"):
            article_text = st.session_state.article_text

            # 1) Pull in the SOCIAL_MODE_INSTRUCTIONS from your template
            social_instructions = extract_section_from_template("###SOCIAL_MODE_INSTRUCTIONS")

            # 2) Build a single prompt using that instruction block
            prompt = f"""
You are a formatting assistant. Follow the exact instructions below to generate a polished, insight-driven short-form blog post.

{social_instructions}

Article text:
{article_text}

Source URL:
{url}

Only return the final formatted result.
"""

            # 3) Ask OpenAI for the fully formatted markdown
            blog_markdown = call_openai(prompt)

            # 4) Display it
            st.markdown(blog_markdown, unsafe_allow_html=True)

            # 5) Convert markdown → HTML so the rich copy button works
            blog_html = markdown_to_html(blog_markdown)

            # 6) Show the same “Copy Formatted Blog” button you have in Long mode
            copy_to_clipboard_component(blog_html)