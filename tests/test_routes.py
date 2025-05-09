def login_test_user(client):
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard_route(client, login_test_user):
    login_test_user(client)
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200