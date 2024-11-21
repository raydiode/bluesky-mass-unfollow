import requests
import time

def authenticate(identifier, password):
    auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    response = requests.post(auth_url, json={"identifier": identifier, "password": password})
    return response.json()

def get_list_follows(session, did):
    url = "https://bsky.social/xrpc/app.bsky.graph.getFollows"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    follows = []
    cursor = None
    
    while True:
        params = {"actor": did, "limit": 100}
        if cursor:
            params["cursor"] = cursor
            
        response = requests.get(url, headers=headers, params=params).json()
        follows.extend(response['follows'])
        
        if not response.get('cursor'):
            break
        cursor = response['cursor']
        
    return follows

def unfollow_user(session, follow_uri):
    # Parse the URI to get collection and rkey
    # URI format: at://did:plc:xxx/app.bsky.graph.follow/yyy
    parts = follow_uri.split('/')
    collection = parts[-2]
    rkey = parts[-1]
    repo = parts[2]

    url = "https://bsky.social/xrpc/com.atproto.repo.deleteRecord"
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    data = {
        "repo": repo,
        "collection": collection,
        "rkey": rkey
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def mass_unfollow():
    identifier = input("Enter your Bluesky handle: ")
    password = input("Enter your password: ")
    
    session = authenticate(identifier, password)
    follows = get_list_follows(session, identifier)
    total = len(follows)
    print(f"Found {total} accounts to unfollow")
    
    for i, follow in enumerate(follows, 1):
        follow_uri = follow['viewer']['following']
        success = unfollow_user(session, follow_uri)
        print(f"[{i}/{total}] Unfollowed {follow['handle']}: {'✓' if success else '✗'}")
        time.sleep(0.5)

if __name__ == "__main__":
    mass_unfollow()
