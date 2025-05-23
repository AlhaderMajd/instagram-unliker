import os
import pyotp

from instagrapi import Client
from pathlib import Path

like_removal_amount = 10000000000
quiet_mode = False
username = ""
password = ""
mfa_secret = ""

output = ""

def init_client() -> Client:
    settings_file = "session.json"
    client = Client()
    client.delay_range = [1, 3]

    if not os.path.isfile(settings_file):
        println("Settings file not found, creating one on the fly...")
        println("Logging in via username and password...")
        if mfa_secret is not None and mfa_secret != "":
            totp = pyotp.TOTP(mfa_secret).now()
            println(f"Configured TOTP MFA with code '{totp}'")
            client.login(username, password, verification_code=totp)
        else:
            client.login(username, password)
        client.dump_settings(Path("session.json"))
    else:
        println("Session found, reusing login...")
        client.load_settings(Path("session.json"))
        client.login(username, password)

    return client

def unlike(client: Client):
    removed = 0

    while removed < like_removal_amount:
        liked = client.liked_medias()
        count_reached = False

        println("Beginning deletion of liked posts...")

        for post in liked:
            try:
                client.media_unlike(post.id)
                removed += 1
                println(f"{removed}: Deleted {post.id} by {post.user.username}")
            except Exception as e:
                println("\nRate limit most likely reached. Try again soon.")
                println(f"Deleted {removed} liked posts.")
                println("Exception: ")
                println(e)
                print(output)
                return

            if removed >= like_removal_amount:
                count_reached = True
                break

        if not count_reached:
            println("Grabbing more posts...")
            liked = client.liked_medias()

            result_count = len(liked)
            println(f"Grabbed {result_count} more posts.")
            if result_count == 0:
                print("No more posts to unlike.")
                print(f"Deleted {removed} liked posts.")
                break

    print(f"Finished deleting {removed} liked posts.")

def println(line):
    if quiet_mode:
        global output
        output += f"\n{line}"
    else:
        print(line)

def main():
    client = init_client()
    unlike(client)

if __name__ == '__main__':
    main()