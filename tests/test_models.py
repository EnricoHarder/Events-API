from models import User

def test_user_password_hashing():
    '''Test that password and checking works correctly'''
    # Arrange: Create a user
    user = User (username="moritz")
    user.set_password("mypassword123")
    # Act & assert
    assert user. check_password("mypassword123") == True
    assert user. check_password("wrongpassword") == False

    assert user.password_hash != "mypassword123" # Check that the password hash is not the plain password
    assert user.password_hash is not None # Check that the password hash is not None after setting