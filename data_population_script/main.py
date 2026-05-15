import asyncio
import httpx
import random
from faker import Faker

fake = Faker()
BASE_URL = "http://localhost:8000/api"

TRACK_IDS = [
    "4863c7fc-b3c3-4bbf-93be-baec4574296d",
    "0455e5fe-58a0-005e-2207-d13b5f94c711",
    "9c93d1b7-d4bd-488c-a40c-a51db8eb0538",
    "d08f3a7f-1d80-4893-90ff-75d72a5ccf98",
    "788e805a-0e7d-327d-3e5a-69bd8cff5e53",
    "4924767c-8dc5-6c2c-c593-5bd2a21b47e6",
    "e445d0d7-afa4-86eb-6a7d-bf42f07f0d7a",
    "7a58cdf0-f724-4170-956a-71d8935da829",
    "11bb4771-aeff-4588-95b3-c03b541ae874",
    "d29829d2-c1b6-d1a4-ee8c-098f11346fb6",
    "03696f81-7ed6-ad4c-0619-b7087b9d996a",
    "6ebc2c15-2e43-4163-901d-e25ab823db96",
    "d167ca57-a908-a78e-7e57-8bd077b2573c",
    "10839e9e-b4ba-4f9f-8ce9-513f66bc9851",
    "a6fd475a-7814-e9d1-a944-e3a4d6596532",
    "b7abdbdc-29a2-4456-b96f-300a7dd52d67",
    "1696171b-4b1c-0c61-4252-d0c05f5d6170",
    "8270842c-99e5-4f47-96b7-0eefc77fd7df",
    "c2131658-1326-5399-e3ca-c53b7c9138c4",
    "0cfa943e-9b6f-49a7-9fb2-5baa953d6b65"
]

EMOJIS = ["😎", "🔥", "☕", "😴", "💻", "🌌", "🎧", "⚡", "🫠", "🌧️", "✨", "🎵", "🛹", "🍀", "🍷", "🍕", "👾", "🌙"]

async def create_user_and_login(client, user_info):
    await client.post("/register/", json=user_info)

    try:
        res = await client.post("/login/", json=user_info)
        return res.json().get("access") or res.json().get("token")
    except Exception as e:
        print(f"Auth failed for {user_info['username']}: {e}")
        return None

async def populate():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        user_tokens = {}
        print("Registering and authenticating 15 dynamic users...")

        while len(user_tokens) < 15:
            username = fake.simple_profile()['username']
            user_info = {"username": username, "password": "password123"}

            token = await create_user_and_login(client, user_info)
            if token:
                user_tokens[username] = token

        print(f"Successfully online with {len(user_tokens)} active user profiles.")

        created_vibe_ids = []
        usernames_list = list(user_tokens.keys())
        total_posts_created = 0
        target_posts = 30

        print(f"\nDistributing {target_posts} posts randomly across accounts...")

        while total_posts_created < target_posts:
            username = random.choice(usernames_list)
            token = user_tokens[username]
            headers = {"Authorization": f"Bearer {token}"}

            has_song = random.choice([True, False])
            track_id = random.choice(TRACK_IDS) if has_song else None
            start = random.randint(0, 90) if has_song else None
            end = start + random.randint(10, 30) if has_song else None

            has_text = random.choice([True, False])
            if has_text:
                content = random.choice([fake.sentence(), fake.paragraph(nb_sentences=2)])
            else:
                content = ""

            if not has_song and not has_text:
                if random.choice([True, False]):
                    content = fake.sentence()
                else:
                    has_song = True
                    track_id = random.choice(TRACK_IDS)
                    start = random.randint(0, 90)
                    end = start + random.randint(10, 30)

            payload = {
                "content": content,
                "percentage": random.randint(0, 100),
                "emoji": random.choice(EMOJIS),
                "track_id": track_id,
                "snippet_start": start,
                "snippet_end": end
            }

            try:
                res = await client.post("/vibes/", json=payload, headers=headers)
                if res.status_code in [200, 201]:
                    vibe_id = res.json().get("id")
                    if vibe_id:
                        created_vibe_ids.append((vibe_id, username))
                        total_posts_created += 1
                        print(f"[{total_posts_created}/{target_posts}] @{username} posted — Text: {bool(content)}, Song: {has_song}")
            except Exception as e:
                print(f"Post generation hiccup: {e}")

        print("\nSpreading random timeline engagement likes...")
        for vibe_id, author_username in created_vibe_ids:
            for username, token in user_tokens.items():
                if username == author_username:
                    continue

                if random.random() < random.uniform(0.1, 0.6):
                    headers = {"Authorization": f"Bearer {token}"}
                    await client.post(f"/vibes/{vibe_id}/like/", headers=headers)
                    print(f"❤️ @{username} liked Vibe #{vibe_id}")

        print(f"\nDone! Generated 15 accounts, {total_posts_created} highly randomized posts, and mixed up likes.")

if __name__ == "__main__":
    asyncio.run(populate())