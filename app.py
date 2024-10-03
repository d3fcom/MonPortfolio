import os
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, g
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
from datetime import datetime, timedelta
import logging
import sqlite3
import base64
import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
socketio = SocketIO(app)

logging.basicConfig(level=logging.DEBUG)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('messages.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

blog_posts = [
    {
        'id': 1,
        'title': 'Introduction to Cybersecurity',
        'content': 'Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information; extorting money from users; or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative.',
        'date': 'October 1, 2024',
        'tags': ['cybersecurity', 'technology', 'security']
    },
    {
        'id': 2,
        'title': 'Web Development Best Practices',
        'content': 'When it comes to web development, following best practices is crucial for creating maintainable and efficient code. Some key practices include: 1) Writing clean, readable code with proper indentation and comments. 2) Using version control systems like Git. 3) Implementing responsive design for various screen sizes. 4) Optimizing performance through minification and caching. 5) Ensuring website security through HTTPS and input validation. 6) Following accessibility guidelines for inclusive web experiences.',
        'date': 'October 5, 2024',
        'tags': ['web development', 'best practices', 'coding']
    },
    {
        'id': 3,
        'title': 'The Importance of Data Encryption',
        'content': 'Data encryption is a critical aspect of modern digital security. It involves converting data into a code to prevent unauthorized access. Whether it\'s protecting sensitive business information, personal data, or communications, encryption plays a vital role in maintaining privacy and security in our increasingly connected world. This post explores various encryption methods, their applications, and why they are essential in both personal and professional contexts.',
        'date': 'October 10, 2024',
        'tags': ['encryption', 'data security', 'privacy']
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    search_query = request.args.get('search', '')
    tag_filter = request.args.get('tag', '')

    filtered_posts = blog_posts
    if search_query:
        filtered_posts = [post for post in filtered_posts if search_query.lower() in post['title'].lower() or search_query.lower() in post['content'].lower()]
    if tag_filter:
        filtered_posts = [post for post in filtered_posts if tag_filter in post['tags']]

    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(filtered_posts) + per_page - 1) // per_page

    all_tags = set()
    for post in blog_posts:
        all_tags.update(post['tags'])

    recent_posts = sorted(blog_posts, key=lambda x: x['date'], reverse=True)[:5]

    return render_template('blog.html', 
                           posts=filtered_posts[start:end], 
                           page=page, 
                           total_pages=total_pages, 
                           search_query=search_query,
                           tag_filter=tag_filter,
                           all_tags=sorted(list(all_tags)),
                           recent_posts=recent_posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = next((post for post in blog_posts if post['id'] == post_id), None)
    if post is None:
        abort(404)
    return render_template('blog_post.html', post=post)

@app.route('/new_blog_post', methods=['GET', 'POST'])
def new_blog_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
        new_post = {
            'id': len(blog_posts) + 1,
            'title': title,
            'content': content,
            'date': datetime.now().strftime('%B %d, %Y'),
            'tags': tags
        }
        blog_posts.append(new_post)
        return redirect(url_for('blog_post', post_id=new_post['id']))
    return render_template('new_blog_post.html')

@app.route('/github_stats')
def github_stats():
    username = 'd3fcom'
    url = f'https://api.github.com/users/{username}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({
            'public_repos': data['public_repos'],
            'followers': data['followers'],
            'following': data['following']
        })
    except requests.RequestException as e:
        app.logger.error(f"Error fetching GitHub stats: {str(e)}")
        return jsonify({'error': 'Unable to fetch GitHub stats'}), 500

@app.route('/github_projects')
def github_projects():
    username = 'd3fcom'
    url = f'https://api.github.com/users/{username}/repos'
    try:
        response = requests.get(url)
        response.raise_for_status()
        projects = response.json()
        return jsonify(projects)
    except requests.RequestException as e:
        app.logger.error(f"Error fetching GitHub projects: {str(e)}")
        return jsonify({'error': 'Unable to fetch GitHub projects'}), 500

@app.route('/project/<string:project_name>')
def project_details(project_name):
    username = 'd3fcom'
    url = f'https://api.github.com/repos/{username}/{project_name}'
    readme_url = f'https://api.github.com/repos/{username}/{project_name}/readme'
    try:
        response = requests.get(url)
        response.raise_for_status()
        project = response.json()

        readme_response = requests.get(readme_url)
        if readme_response.status_code == 200:
            readme_content = base64.b64decode(readme_response.json()['content']).decode('utf-8')
            readme_html = markdown.markdown(readme_content)
        else:
            readme_html = "<p>No README found for this project.</p>"

        return render_template('project_details.html', project=project, readme_html=readme_html)
    except requests.RequestException as e:
        app.logger.error(f"Error fetching project details: {str(e)}")
        abort(404)

@app.route('/github_activity')
def github_activity():
    username = 'd3fcom'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    url = f'https://api.github.com/users/{username}/events/public'
    params = {
        'per_page': 100,
        'page': 1,
        'since': start_date.isoformat()
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        events = response.json()
        activity_data = {}
        for event in events:
            date = event['created_at'][:10]
            if date in activity_data:
                activity_data[date] += 1
            else:
                activity_data[date] = 1
        return jsonify(activity_data)
    except requests.RequestException as e:
        app.logger.error(f"Error fetching GitHub activity: {str(e)}")
        return jsonify({'error': 'Unable to fetch GitHub activity'}), 500

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=data['room'])

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)