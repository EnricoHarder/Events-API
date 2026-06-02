from models import User

def test_user_password_hashing_behaves_correctly():
    '''Test that password hashing and checking works correctly'''
    # Arrange: Create a user
    user = User(username="moritz")
    user.set_password("mypassword123")
    
    # Act & assert
    assert user.check_password("mypassword123") == True
    assert user.check_password("wrongpassword") == False

    # Check that the password hash is not the plain password
    assert user.password_hash != "mypassword123" 
    
    # Check that the password hash is not None after setting
    assert user.password_hash is not None