from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

def search_github_repositories(query, sort_by='stars', order='desc', page=1):
    base_url = 'https://api.github.com/search/repositories'
    params = {'q': query, 'sort': sort_by, 'order': order, 'page': page}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        repositories = data.get('items', [])
        total_count = data.get('total_count', 0)
        return repositories, total_count
    else:
        print(f"Error: Unable to fetch data from GitHub API. Status Code: {response.status_code}")
        return [], 0

def get_trending_repositories(language='python', since='weekly', quantity=5):
    base_url = f'https://api.github.com/search/repositories'
    params = {
        'q': f'language:{language}',
        'sort': 'stars',
        'order': 'desc',
        'per_page': quantity,
        'page': 1,
    }

    # If 'since' is provided, set the 'created' parameter accordingly
    if since:
        since_mapping = {
            'daily': 'daily',
            'weekly': 'weekly',
            'monthly': 'monthly'
        }
        params['created'] = since_mapping.get(since, 'daily')

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        repositories = data.get('items', [])
        return repositories
    else:
        print(f"Error: Unable to fetch trending data from GitHub API. Status Code: {response.status_code}")
        return []

def paginate_repositories(repositories, page_size=10):
    total_pages = (len(repositories) + page_size - 1) // page_size
    return total_pages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        sort_by = request.form.get('sort_by', 'stars')
        order = request.form['order']
        page = 1  # default page

        repositories, total_count = search_github_repositories(query, sort_by, order, page)

        if repositories:
            page_size = 10  # You can adjust the page size
            total_pages = paginate_repositories(repositories, page_size)
            return render_template('index.html', query=query, repositories=repositories, page=page, total_pages=total_pages)
        else:
            return render_template('index.html', query=query, message='No repositories found.')

    return render_template('index.html', query='', repositories=[], message='')

@app.route('/trending', methods=['GET'])
def trending():
    language = request.args.get('language', 'python')
    since = request.args.get('since', 'weekly')
    quantity = int(request.args.get('quantity', 5))

    trending_repositories = get_trending_repositories(language=language, since=since, quantity=quantity)

    return render_template('trending.html', trending_repositories=trending_repositories)

if __name__ == '__main__':
    app.run(debug=True)
