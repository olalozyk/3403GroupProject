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

# Page 15 - Password Reset Page
def test_reset_password_page(client):
    response = client.get('/reset_password')
    assert response.status_code == 200
    assert b'Reset Password' in response.data
    
def test_reset_password_request_invalid_email(client):
    # First get the page to get the CSRF token
    response = client.get('/reset_password')
    csrf_token = response.data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    
    response = client.post('/reset_password', data={
        'email': 'nonexistentuser@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'There is no account with that email' in response.data

def test_reset_password_request_valid_email(client, test_user):
    # First get the page to get the CSRF token
    response = client.get('/reset_password')
    csrf_token = response.data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    
    response = client.post('/reset_password', data={
        'email': 'test@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'An email has been sent with instructions' in response.data

def test_reset_token_invalid(client):
    response = client.get('/reset_password/invalidtoken', follow_redirects=True)
    assert b'That is an invalid or expired token' in response.data
    assert b'Reset Password' in response.data


# Page 17 - Changing password
def test_change_password(client, test_user, login_test_user):
    login_test_user(client)
    response = client.get('/change_password')
    assert response.status_code == 200
    assert b'Change Password' in response.data
    
    response = client.post('/change_password', data={
        'current_password': 'wrongpassword',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert b'Current password is incorrect' in response.data
    
    response = client.post('/change_password', data={
        'current_password': 'testpassword',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert b'Your password has been updated' in response.data
    
    #test login with new password
    client.get('/logout', follow_redirects=True)
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'newpassword123'
    }, follow_redirects=True)
    assert b'Login successful' in response.data
