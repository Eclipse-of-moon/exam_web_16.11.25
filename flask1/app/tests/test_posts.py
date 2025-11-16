def test_index_page(client):
    """Проверяет, что главная страница возвращает код 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_template(client, captured_templates):
    """Проверяет, что для главной страницы используется правильный шаблон."""
    with captured_templates as templates:
        client.get('/')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'

def test_about_page(client):
    """Проверяет, что страница 'Об авторе' возвращает код 200."""
    response = client.get("/about")
    assert response.status_code == 200


def test_about_template(client, captured_templates):
    """Проверяет, что для страницы 'Об авторе' используется правильный шаблон."""
    with captured_templates as templates:
        client.get('/about')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'about.html'
        assert context['title'] == 'Об авторе'

def test_posts_page(client):
    """Проверяет, что страница постов возвращает код 200."""
    response = client.get("/posts")
    assert response.status_code == 200


def test_posts_index_template(client, captured_templates, mocker, posts_list):
    """Проверяет, что для страницы постов используется правильный шаблон и контекст."""
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        _ = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert context['posts'] == posts_list


def test_post_page(client, mocker, captured_templates, test_post):
    """Проверяет, что страница отдельного поста возвращает код 200 и использует правильный шаблон."""
    mocker.patch("app.posts_list", return_value=[test_post])
    with captured_templates as templates:
        response = client.get(f"/posts/{test_post['id']}")
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'
        assert context['post'] == test_post
        assert context['title'] == test_post['title']


def test_post_content(client, mocker, test_post):
    """Проверяет, что на странице поста отображаются все данные поста."""
    mocker.patch("app.posts_list", return_value=[test_post])
    response = client.get(f"/posts/{test_post['id']}")
    html = response.data.decode('utf-8')

    assert test_post['title'] in html
    assert test_post['text'] in html
    assert test_post['author'] in html
    assert test_post['date'].strftime('%d.%m.%Y') in html
    assert f"images/{test_post['image_id']}" in html


def test_post_date_format(client, mocker, test_post):
    """Проверяет, что дата публикации отображается в правильном формате."""
    mocker.patch("app.posts_list", return_value=[test_post])
    response = client.get(f"/posts/{test_post['id']}")
    html = response.data.decode('utf-8')
    assert test_post['date'].strftime('%d.%m.%Y') in html


def test_nonexistent_post(client, mocker):
    """Проверяет, что при запросе несуществующего поста возвращается код 404."""
    mocker.patch("app.posts_list", return_value=[])
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert "Post not found" in response.data.decode('utf-8')

def test_base_template_footer(client):
    """Проверяет, что подвал (footer) присутствует на всех страницах."""
    response = client.get("/")
    html = response.data.decode('utf-8')
    assert "Филиппова Полина Владимировна, 231-352" in html

    response = client.get("/posts")
    html = response.data.decode('utf-8')
    assert "Филиппова Полина Владимировна, 231-352" in html

    response = client.get("/about")
    html = response.data.decode('utf-8')
    assert "Филиппова Полина Владимировна, 231-352" in html

    response = client.get("/posts/0")
    html = response.data.decode('utf-8')
    assert "Филиппова Полина Владимировна, 231-352" in html

def test_posts_list_empty(client, mocker):
    """Проверяет, что на странице постов отображается сообщение, если нет постов."""
    mocker.patch("app.posts_list", return_value=[])
    response = client.get("/posts")
    html = response.data.decode('utf-8')
    assert "Еще нет постов." in html


def test_post_comments_present(client, mocker, posts_list_with_comments):
    """Проверяет, что на странице поста отображаются комментарии, если они есть."""
    mocker.patch("app.posts_list", return_value=posts_list_with_comments)
    response = client.get("/posts/1")
    html = response.data.decode('utf-8')
    assert "First comment" in html
    assert "Second comment" in html

def test_post_no_comments_message(client, mocker, test_post):
    """Проверяет, что на странице поста отображается сообщение, если нет комментариев."""
    mocker.patch("app.posts_list", return_value=[test_post])
    response = client.get(f"/posts/{test_post['id']}")
    html = response.data.decode('utf-8')
    assert "Еще нет комментариев." in html

def test_about_content(client):
    """Проверяет, что на странице 'Об авторе' отображается какой-то контент (хотя бы абзац)."""
    response = client.get("/about")
    html = response.data.decode('utf-8')
    assert "<p>" in html