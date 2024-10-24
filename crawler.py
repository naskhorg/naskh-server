import os
import httpx
import asyncio
import aiosqlite
from bs4 import BeautifulSoup

TOTAL_PAGES = 315

BASE_URL = "https://quranicnames.com/all-baby-names/page/"

async def create(name, category, link):
    print('creating database')
    db_path = os.path.join(os.getcwd(), 'naskh.db')
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    category TEXT,
                    link TEXT
                )""")
        await db.execute("INSERT INTO posts (name, category, link) VALUES (?, ?, ?)", (name, category, link))
        await db.commit()


async def fetch_and_create(page_content):
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        posts = soup.select('#catsdiv > div[id^="post-"]')
        for post in posts:
            anchor = post.find('a')
            category = anchor.get('class')
            link = anchor.get('href')
            name = anchor.select_one('.entry-title-area h2.entry-title').text.strip()
            await create(name, category, link)
    except Exception as e:
        print(f"Error fetching the page: {e}")

async def fetch(url, client):
    print('url: ', url)
    response = await client.get(url)
    await fetch_and_create(response)
    
    
async def main():
    async with httpx.AsyncClient() as client:
        tasks = (fetch(f'{BASE_URL}/{i}/', client) for i in range(5))
        await asyncio.gather(*tasks)
        
        
asyncio.run(main())