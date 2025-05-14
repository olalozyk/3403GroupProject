def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200 or response.status_code == 302

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200 or response.status_code == 302

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_reset_request_page(client):
    response = client.get('/reset_request')
    assert response.status_code == 200

def test_reset_password_token_page(client):
    response = client.get('/reset_password/test-token')
    assert response.status_code == 200

def test_dashboard_page_redirect(client):
    # Should redirect if not logged in
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302  # Redirect status code

def test_change_password_page(client):
    # Should redirect if not logged in 
    response = client.get('/change_password', follow_redirects=False)
    assert response.status_code == 302  # Redirect status code

def test_appointment_page(client):
    # Should redirect if not logged in
    response = client.get('/appointments', follow_redirects=False)
    assert response.status_code == 302  # Redirect status code

def test_calendar_page(client):
    # Should redirect if not logged in
    response = client.get('/calendar', follow_redirects=False)
    assert response.status_code == 302  # Redirect status code
