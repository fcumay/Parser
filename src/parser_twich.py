# import requests
#
# client_id = "7farkw03xdeuwbwduvvy8ee3wpcsar"
# client_secret = "8k2r1a8zq3dkkt9gychm12vt2mqyna"
# url = "https://id.twitch.tv/oauth2/token"
# params = {
#     "client_id": client_id,
#     "client_secret": client_secret,
#     "grant_type": "client_credentials"
# }
#
# response = requests.post(url, params=params)
# data = response.json()
# print(response)
# if response.status_code == 200:
#     access_token = data.get("access_token")
#     print(f"access_token {access_token}")
# else:
#     print("Error get token")
#
# headers = {
#     "Client-ID": client_id,
#     "Authorization": f"Bearer {access_token}",
#     "Accept": "application/vnd.twitchtv.v5+json"
# }
#
# def get_games():
#     url = "https://api.twitch.tv/helix/games/top"
#
#     response = requests.get(url, headers=headers)
#     print(response)
#     if response.status_code == 200:
#         games = response.json()
#         print("games")
#         print(games)
#     else:
#         print("Error get games")
#
# def get_streams_streamers():
#     url = "https://api.twitch.tv/helix/streams"
#
#     response = requests.get(url, headers=headers)
#     print(response)
#     if response.status_code == 200:
#         streams = response.json()
#         print("streams")
#         print(streams)
#     else:
#         print("Error get streams")
#
#
# get_games()
# get_streams_streamers()
import httpx

client_id = "7farkw03xdeuwbwduvvy8ee3wpcsar"
client_secret = "8k2r1a8zq3dkkt9gychm12vt2mqyna"
url = "https://id.twitch.tv/oauth2/token"
params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        data = response.json()
        print(response)
        if response.status_code == 200:
            access_token = data.get("access_token")
            print(f"access_token {access_token}")
            return access_token
        else:
            print("Error get token")

async def get_games(access_token):
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.twitchtv.v5+json"
    }
    url = "https://api.twitch.tv/helix/games/top"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(response)
        if response.status_code == 200:
            games = response.json()
            print("games")
            print(games)
        else:
            print("Error get games")

async def get_streams_streamers(access_token):
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.twitchtv.v5+json"
    }
    url = "https://api.twitch.tv/helix/streams"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(response)
        if response.status_code == 200:
            streams = response.json()
            print("streams")
            print(streams)
        else:
            print("Error get streams")

async def main():
    access_token = await get_access_token()
    if access_token:
        await get_games(access_token)
        await get_streams_streamers(access_token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
