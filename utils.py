from instagrapi import Client
import time

def send_mass_dm(target_account, message, time_delay, is_followers):
    """
    This function sends a DM to either followers or following of the target account
    """
    client = Client()
    
    # Ensure you're logged in with the session stored in Flask app
    client.login("your_instagram_username", "your_instagram_password")
    
    try:
        # Get the user object for the target account
        target_user = client.user_info_by_username(target_account)
        target_list = client.user_followers(target_user.pk) if is_followers else client.user_following(target_user.pk)
        
        for user in target_list:
            try:
                # Send DM
                client.direct_send(message, [user.pk])
                print(f"Sent DM to {user.username}")

                # Control the delay between messages
                time.sleep(time_delay)
            except Exception as e:
                print(f"Failed to send DM to {user.username}: {e}")

    except Exception as e:
        print(f"Error retrieving user data for {target_account}: {e}")
