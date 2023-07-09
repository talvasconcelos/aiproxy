async def m001_initial(db):
    await db.execute(
        f"""
        CREATE TABLE aiproxy.apilinks (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            api_url TEXT NOT NULL,
            api_key TEXT,
            description TEXT NOT NULL,
            cost INTEGER NOT NULL,
            webhook TEXT
        );
        """
    )

    await db.execute(
        f"""
        CREATE TABLE aiproxy.users (
            id TEXT PRIMARY KEY,
            link TEXT NOT NULL,
            uses INTEGER NOT NULL,
            paid BOOLEAN NOT NULL DEFAULT 0
        );
        """
    )

