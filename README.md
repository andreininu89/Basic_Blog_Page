# Basic Blog Page

A small Django blog application with post publishing, draft management, authentication, and comment moderation.

## Features

- Public post list showing published posts in reverse chronological order
- Individual post pages with comments
- Login-protected post creation, editing, deletion, and publishing
- Draft post view for unpublished posts
- Login-protected comment creation and moderation
- Django admin support
- SQLite database for local development
- Bootstrap-based UI with custom styling

## Tech Stack

- Python
- Django 6
- SQLite
- Bootstrap 5
- Medium Editor styling in forms/templates

## Project Structure

```text
Basic_Blog_Page/
├── blog_clone_project/
│   ├── blog/
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── static/
│   │   └── templates/
│   ├── blog_clone_project/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── manage.py
│   └── requirements.txt
├── .venv/
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Basic_Blog_Page
```

### 2. Create and activate a virtual environment

If you do not already have one:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r blog_clone_project/requirements.txt
```

### 4. Apply migrations

```bash
python blog_clone_project/manage.py migrate
```

### 5. Create a superuser

```bash
python blog_clone_project/manage.py createsuperuser
```

### 6. Start the development server

```bash
python blog_clone_project/manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Main Routes

- `/` - published blog posts
- `/about/` - about page
- `/post/new/` - create a post
- `/drafts/` - view drafts
- `/accounts/login/` - login page
- `/admin/` - Django admin

## Authentication and Permissions

- Unauthenticated users can browse published posts and the about page.
- Authenticated users can create posts, save drafts, publish posts, add comments, and moderate comments.
- Only the post author can update or delete a post.

## Running Tests

The repository includes a test suite in `blog/tests.py`.

Run:

```bash
python blog_clone_project/manage.py test blog.tests
```

Current note: `python blog_clone_project/manage.py test` reports `0` discovered tests because the existing test module/class naming does not follow Django's default discovery pattern, but the targeted test command runs successfully.

## Development Notes

- The project currently uses SQLite through `db.sqlite3`.
- Static files are served from Django's default development setup.
- `DEBUG` is enabled in settings, so this configuration is for local development only.

## Possible Improvements

- Add registration and profile support
- Improve test discovery by renaming test classes/modules to Django defaults
- Add pagination for blog posts
- Restrict comment moderation permissions more tightly
- Add deployment configuration for production
